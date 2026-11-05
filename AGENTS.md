# CampusOps agent rules

Project spec: docs/project.md. Read it before every task.

## Stack
- Frontend: React + Vite
- Backend: Python 3.12 Lambda (set runtime to python3.12)
- AWS: API Gateway, DynamoDB, Cognito, S3, EventBridge, SNS, CloudWatch
- IaC: Terraform. CI/CD: GitHub Actions
- Region: ap-south-1. Free Tier only.

## Rules
- Work on ONE module at a time. Show a plan first and wait for my OK.
- NEVER run terraform apply or terraform destroy. Only terraform plan.
- NEVER run any command that creates, changes or deletes AWS resources.
- NEVER commit or print secrets or AWS keys. Use environment variables.
- Write pytest tests for every Lambda (use moto for AWS mocks).
- After each step, update docs/PROGRESS.md with what was done.
- Explain each AWS resource in one line.
- Keep code simple and commented. I must be able to explain it in a viva.
