#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BRANCH="main"

echo "== BPJS Demo Git Pull =="
echo "Repo   : $REPO_DIR"
echo "Branch : $BRANCH"
echo

cd "$REPO_DIR"

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "Error: folder ini bukan git repository."
  exit 1
fi

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
echo "Current branch: $CURRENT_BRANCH"

if [ "$CURRENT_BRANCH" != "$BRANCH" ]; then
  echo "Pindah ke branch $BRANCH..."
  git checkout "$BRANCH"
fi

echo "Fetch dari origin..."
git fetch origin

LOCAL_HASH="$(git rev-parse HEAD)"
REMOTE_HASH="$(git rev-parse origin/$BRANCH)"
BASE_HASH="$(git merge-base HEAD origin/$BRANCH)"

echo
if [ "$LOCAL_HASH" = "$REMOTE_HASH" ]; then
  echo "Sudah paling update. Tidak ada perubahan."
  exit 0
fi

if [ "$LOCAL_HASH" = "$BASE_HASH" ]; then
  echo "Ada update baru. Pulling latest changes..."
  git pull origin "$BRANCH"
  echo "Pull selesai."
  exit 0
fi

if [ "$REMOTE_HASH" = "$BASE_HASH" ]; then
  echo "Branch lokal punya commit yang belum di-push."
  echo "Tidak melakukan pull otomatis untuk menghindari konflik."
  exit 1
fi

echo "Branch lokal dan remote sudah diverge."
echo "Silakan review manual:"
echo "  git status"
echo "  git pull --rebase origin $BRANCH"
exit 1