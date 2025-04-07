#!/bin/bash

# Optional: for GitHub Enterprise
export GH_HOST=github.paypal.com

DELETED_LOG="deleted_repos.log"
SKIPPED_LOG="skipped_repos.log"

echo "==============================="
echo " GitHub Repo Cleanup Tool 🧹"
echo "==============================="
echo "Choose cleanup type:"
echo "1. Archived Repositories"
echo "2. Forked Repositories"
read -rp "Enter your choice (1 or 2): " choice

TMP_FILE="/tmp/repo_list.txt"

if [[ "$choice" == "1" ]]; then
  TYPE="archived"
  echo "🔍 Fetching archived repositories..."
  gh repo list --limit 1000 --json name,isArchived,owner \
    -q '.[] | select(.isArchived==true) | [.owner.login, .name] | @tsv' > "$TMP_FILE"
elif [[ "$choice" == "2" ]]; then
  TYPE="forked"
  echo "🔍 Fetching forked repositories..."
  gh repo list --limit 1000 --json name,isFork,owner \
    -q '.[] | select(.isFork==true) | [.owner.login, .name] | @tsv' > "$TMP_FILE"
else
  echo "❌ Invalid choice. Exiting."
  exit 1
fi

echo ""
repo_count=$(wc -l < "$TMP_FILE")
echo "Found $repo_count $TYPE repositories."

# Read repos into an array
repos=()
while IFS= read -r line; do
  repos+=("$line")
done < "$TMP_FILE"

# Clear previous logs
> "$DELETED_LOG"
> "$SKIPPED_LOG"

# Use for loop so `read` works interactively
for entry in "${repos[@]}"; do
  owner=$(echo "$entry" | cut -f1)
  repo=$(echo "$entry" | cut -f2)
  full_name="$owner/$repo"

  echo ""
  echo "📁 $TYPE Repo: $full_name"
  read -rp "❓ Delete this repo? Type 'yes' to confirm: " confirm
  if [[ "$confirm" =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "🗑️  Deleting $full_name..."
    if gh repo delete "$full_name" --yes; then
      echo "$full_name" >> "$DELETED_LOG"
    else
      echo "⚠️  Failed to delete $full_name"
    fi
  else
    echo "⏭️  Skipped $full_name"
    echo "$full_name" >> "$SKIPPED_LOG"
  fi
done

echo ""
echo "✅ Cleanup complete!"
echo "📝 Deleted repos logged in:   $DELETED_LOG"
echo "📝 Skipped repos logged in:   $SKIPPED_LOG"
