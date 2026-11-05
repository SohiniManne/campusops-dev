#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/bin:$PATH"

cd /mnt/c/Project/campusops-dev/infra/terraform

echo "=== Running terraform init -migrate-state ==="
echo "yes" | terraform init -migrate-state

echo "=== Running terraform plan ==="
terraform plan

