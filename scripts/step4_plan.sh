#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/bin:$PATH"

echo "=== AWS Identity Check ==="
aws sts get-caller-identity

echo "=== Terraform Init ==="
cd /mnt/c/Project/campusops-dev/infra/terraform
terraform init

echo "=== Terraform Validate ==="
terraform validate

echo "=== Terraform Plan ==="
terraform plan -out=tfplan

