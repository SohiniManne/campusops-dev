#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/bin:$PATH"
cd /mnt/c/Project/campusops-dev/infra/terraform
terraform plan
