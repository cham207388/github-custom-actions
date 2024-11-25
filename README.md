# Notes

## ssh-agent

- `ssh-keygen -t rsa -b 4096 -C "<your_email@example.com>"`
- add public key to github
  - `cat ~/.ssh/id_rsa_github.pub`
  - Go to your GitHub repository or organization.
  - Navigate to Settings > Deploy keys.
  - Click Add deploy key.
  - Paste the public key into the Key field.
  - Optionally, select Allow write access if needed for the workflow.

- add private key as a secret to github repo
  - `cat ~/.ssh/id_rsa_github`
