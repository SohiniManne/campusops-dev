#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/bin:$PATH"

cd /mnt/c/Project/campusops-dev/frontend
npm run build
aws s3 sync dist/ s3://campusops-frontend-dev-c0cf6c4c/ --delete

