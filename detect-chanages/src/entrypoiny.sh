#!/bin/sh

# Parse arguments
MODULES="$1"
SEMANTIC_VERSION="$2"
GITHUB_TOKEN="$3"

# Set GitHub token for authentication (if provided)
if [ -n "$GITHUB_TOKEN" ]; then
  git config --global http.https://github.com/.extraheader "AUTHORIZATION: bearer $GITHUB_TOKEN"
fi

# Run the Python script
python /app/detect_changes.py \
  --modules "$MODULES" \
  --semantic-version "$SEMANTIC_VERSION"

# Capture and output the results
if [ -f /github_output.txt ]; then
  while IFS= read -r line; do
    echo "$line" >> $GITHUB_OUTPUT
  done < /github_output.txt
fi