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

Checkout code to use custom action

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: build mvn project
        uses: cham207388/github-custom-actions/mvn-jdk21@main
        with:
          test: 'no'

      - name: Terraform
        uses: cham207388/github-custom-actions/terraform@main
        with:
          directory: ./terraform
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
          variables: "aws_region=us-east-2"
          destroy: "yes"
```