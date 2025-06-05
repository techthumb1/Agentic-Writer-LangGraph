#!/usr/bin/env bash
set -euo pipefail

####  CONFIG  #############################################################
FILES=$(find . \
  -type f \
  \( -name '*.py' -o -name '*.ts' -o -name '*.tsx' -o -name '*.js' \) \
  -not -path './node_modules/*' \
  -not -path './.next/*' \
  -not -path './.git/*' \
  -not -path './storage/*' \
)

PATTERNS=(
  's|"content_templates"|"../data/content_templates"|g'
  "s|'content_templates'|'../data/content_templates'|g"
  's|"style_profiles"|"../data/style_profiles"|g'
  "s|'style_profiles'|'../data/style_profiles'|g"
  's|"generated_content"|"../storage"|g'
  "s|'generated_content'|'../storage'|g"
)
###########################################################################

echo "🔍  Updating paths in $(echo "$FILES" | wc -l) files"

for f in $FILES; do
  cp "$f" "$f.bak"                    # backup once
  for p in "${PATTERNS[@]}"; do
    # BSD-sed (macOS) compatibility: use -i '' ; GNU sed use -i
    sed -i '' -e "$p" "$f"
  done
done

echo "✅  Replacement finished. Original files have *.bak backups."
