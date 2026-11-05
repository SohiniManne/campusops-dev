#!/usr/bin/env bash
set -e
export PATH="$HOME/.local/bin:$PATH"
cd /mnt/c/Project/campusops-dev
python3 scripts/smoke_test.py

