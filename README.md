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

      - name: Use Terraform with SSH agent (default)
        uses: cham207388/github-custom-actions/terraform@main
        with:
          working-directory: ./terraform
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ secrets.AWS_REGION }}
          ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}
          variables: "aws_region=us-east-2"
          destroy: "yes"
          terraform-version: 1.12.0

      - name: Use Terraform without SSH agent
        uses: cham207388/github-custom-actions/tf-no-ssh@main
        with:
          working-directory: ./terraform
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: "us-east-1"
          variables: "domain_name=${{ secrets.DOMAIN_NAME }},frontend_domain_name=course.${{ secrets.DOMAIN_NAME }},api_domain_name=api.${{ secrets.DOMAIN_NAME }}"      
          destroy: "yes"
          terraform-version: 1.11.1

      - name: Use Gradle
        uses: cham207388/github-custom-actions/gradle-jdk21@main
        with:
          working-directory: ./backend
          java-version: 21
          test: "no"

      - name: Use Maven
        uses: cham207388/github-custom-actions/mvn-jdk21@main
        with:
          working-directory: ./backend
          java-version: 21
          test: "no"

      - name: Use Vite
        uses: cham207388/github-custom-actions/vite-node@main
        with:
          working-directory: ./frontend
          test: "no"

      - name: Use Docker
        uses: cham207388/github-custom-actions/docker@main
        with:
          working-directory: ./docker
          image-name: "cham207388/github-custom-actions"
          image-tag: "latest"
          dockerhub-username: "cham207388"
          dockerhub-token: ${{ secrets.DOCKERHUB_TOKEN }}
          
      - name: Use Helm
        uses: cham207388/github-custom-actions/helm@main
        with:
          working-directory: ./helm
          aws-region: "us-east-1"
          variables: "domain_name=${{ secrets.DOMAIN_NAME }},frontend_domain_name=course.${{ secrets.DOMAIN_NAME }},api_domain_name=api.${{ secrets.DOMAIN_NAME }}"
          destroy: "yes"
          terraform-version: 1.11.1
```