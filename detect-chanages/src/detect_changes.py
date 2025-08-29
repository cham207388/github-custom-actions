#!/usr/bin/env python3
"""
Detect Changes Script for GitHub Actions CI/CD Pipeline

This script detects changes in multiple modules within a mono-repo by comparing
folder hashes between base and head commits. It outputs GitHub Actions compatible
outputs for conditional workflow execution.
"""

import os
import sys
import json
import hashlib
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ChangeDetector:
    def __init__(self, modules: List[str]):
        self.modules = modules
        
    def _get_commit_shas(self) -> Tuple[Optional[str], str]:
        """Determine base and head commit SHAs based on event type"""
        event_name = os.environ.get('GITHUB_EVENT_NAME', '')
        event_path = os.environ.get('GITHUB_EVENT_PATH', '')
        
        event_data = {}
        if event_path and os.path.exists(event_path):
            try:
                with open(event_path, 'r') as f:
                    event_data = json.load(f)
            except json.JSONDecodeError:
                print("Warning: Could not parse event JSON file")
        
        if event_name == "pull_request":
            print("is pull request")
            base_sha = event_data.get('pull_request', {}).get('base', {}).get('sha')
            head_sha = event_data.get('pull_request', {}).get('head', {}).get('sha')
        else:
            print("is not pull request")
            base_sha = os.environ.get('GITHUB_EVENT_BEFORE')
            head_sha = os.environ.get('GITHUB_SHA')
        
        # Handle first-push scenario
        if base_sha and all(c == '0' for c in base_sha):
            try:
                result = subprocess.run(
                    ['git', 'rev-parse', f'{head_sha}^'],
                    capture_output=True, text=True, check=False
                )
                base_sha = result.stdout.strip() if result.returncode == 0 else None
            except Exception as e:
                print(f"Warning: Could not get parent commit: {e}")
                base_sha = None
        
        return base_sha, head_sha
    
    def _folder_hash(self, folder_path: str) -> str:
        """Calculate content-only hash of a folder"""
        if not os.path.exists(folder_path):
            return ""
        
        hasher = hashlib.sha256()
        
        # Get all files and sort them for consistent hashing
        files = []
        for root, _, filenames in os.walk(folder_path):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                files.append(file_path)
        
        files.sort()
        
        for file_path in files:
            try:
                with open(file_path, 'rb') as f:
                    while chunk := f.read(8192):
                        hasher.update(chunk)
            except Exception as e:
                print(f"Warning: Could not read file {file_path}: {e}")
                continue
        
        return hasher.hexdigest()
    
    def _extract_module_tree(self, commit_sha: str, module: str, extract_dir: str) -> bool:
        """Extract module files from a specific commit"""
        if not commit_sha:
            return False
        
        try:
            os.makedirs(extract_dir, exist_ok=True)
            
            # Check if the module exists in the commit
            result = subprocess.run(
                ['git', 'ls-tree', commit_sha, module],
                capture_output=True, text=True, check=False
            )
            
            if result.returncode != 0:
                print(f"Module {module} not found in commit {commit_sha}")
                return False
            
            # Extract using git archive and tar
            git_process = subprocess.Popen(
                ['git', 'archive', commit_sha, module],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            tar_process = subprocess.Popen(
                ['tar', '-x', '-C', extract_dir],
                stdin=git_process.stdout,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            git_process.stdout.close()
            stdout, stderr = tar_process.communicate()
            
            if tar_process.returncode != 0:
                print(f"Error extracting {module}: {stderr.decode() if stderr else 'Unknown error'}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error extracting {module} from {commit_sha}: {e}")
            return False
    
    def detect_changes(self) -> Dict[str, bool]:
        """Detect changes for all modules"""
        base_sha, head_sha = self._get_commit_shas()
        changes = {}
        
        print(f"Base SHA: {base_sha}")
        print(f"Head SHA: {head_sha}")
        
        # Create temporary directories
        base_dir = Path("/tmp/base_modules")
        head_dir = Path("/tmp/head_modules")
        base_dir.mkdir(exist_ok=True)
        head_dir.mkdir(exist_ok=True)
        
        for module in self.modules:
            base_module_dir = base_dir / module
            head_module_dir = head_dir / module
            
            # Extract base and head versions
            base_extracted = self._extract_module_tree(base_sha, module, str(base_module_dir))
            head_extracted = self._extract_module_tree(head_sha, module, str(head_module_dir))
            
            if not head_extracted:
                # Module doesn't exist in head commit
                print(f"Module {module}: not found in HEAD, marking as unchanged")
                changes[module] = False
                continue
            
            # Calculate hashes
            base_hash = self._folder_hash(str(base_module_dir)) if base_extracted else ""
            head_hash = self._folder_hash(str(head_module_dir))
            
            # Determine if changed
            has_changed = base_hash != head_hash
            changes[module] = has_changed
            
            print(f"Module {module}: base_hash={base_hash[:8]}..., head_hash={head_hash[:8]}..., changed={has_changed}")
        
        # Cleanup
        shutil.rmtree(base_dir, ignore_errors=True)
        shutil.rmtree(head_dir, ignore_errors=True)
        
        return changes
    
    def output_github_actions(self, changes: Dict[str, bool], semantic_version: str):
        """Output GitHub Actions compatible outputs"""
        github_output = os.environ.get('GITHUB_OUTPUT')
        
        if github_output:
            # Use new GITHUB_OUTPUT file method
            with open(github_output, 'a') as f:
                # Output individual module changes
                for module, changed in changes.items():
                    output_name = module.replace('_', '-').replace('/', '-')
                    f.write(f"{output_name}-changed={str(changed).lower()}\n")
                
                # Output JSON object with all changes
                changes_json = json.dumps(changes)
                f.write(f"changes={changes_json}\n")
                f.write(f"semantic-version={semantic_version}\n")
        else:
            # Fallback to deprecated set-output for compatibility
            for module, changed in changes.items():
                output_name = module.replace('_', '-').replace('/', '-')
                print(f"::set-output name={output_name}-changed::{str(changed).lower()}")
            
            changes_json = json.dumps(changes)
            print(f"::set-output name=changes::{changes_json}")
            print(f"::set-output name=semantic-version::{semantic_version}")


def parse_modules_string(modules_str: str) -> List[str]:
    """Parse modules string from GitHub Actions into a list"""
    if not modules_str:
        return []
    
    # Remove quotes and split by space
    modules_str = modules_str.strip().strip('"').strip("'")
    modules = [m.strip() for m in modules_str.split() if m.strip()]
    
    return modules


def main():
    # Parse command line arguments
    if len(sys.argv) < 3:
        print("Usage: detect_changes.py --modules <modules> --semantic-version <version>")
        sys.exit(1)
    
    # Simple argument parsing (for composite action compatibility)
    modules_str = None
    semantic_version = None
    
    # Parse arguments in order (since composite actions pass them positionally)
    if len(sys.argv) >= 2:
        modules_str = sys.argv[1]
    if len(sys.argv) >= 3:
        semantic_version = sys.argv[2]
    
    if not modules_str or not semantic_version:
        print("Error: Both modules and semantic-version are required")
        sys.exit(1)
    
    # Parse modules
    modules_list = parse_modules_string(modules_str)
    
    if not modules_list:
        print("Error: No modules specified")
        sys.exit(1)
    
    print(f"Checking modules: {modules_list}")
    print(f"Semantic version: {semantic_version}")
    
    # Initialize detector
    detector = ChangeDetector(modules=modules_list)
    
    # Detect changes
    changes = detector.detect_changes()
    
    # Output results for GitHub Actions
    detector.output_github_actions(changes, semantic_version)
    
    # Print summary
    print("\nChange Detection Summary:")
    for module, changed in changes.items():
        status = "CHANGED" if changed else "UNCHANGED"
        print(f"  {module}: {status}")


if __name__ == "__main__":
    main()
