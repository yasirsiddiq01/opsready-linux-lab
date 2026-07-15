#!/usr/bin/env bash
set -euo pipefail

if [ -d .git ]; then
  echo "A .git directory already exists. No repository was changed."
  exit 1
fi

git init
git branch -M main
git add .
git commit -m "Initial standalone release: OpsReady Linux Lab 1.0.0"

cat <<'MSG'

Local repository created.

Next:
  1. Create an empty remote repository named opsready-linux-lab.
  2. Run:
       git remote add origin <REMOTE_URL>
       git push -u origin main
MSG
