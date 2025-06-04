#!/usr/bin/env bash
set -e

mkdir -p data/content_templates data/style_profiles storage

# Move unique YAMLs
rsync -a --ignore-existing content_templates/ data/content_templates/ 2>/dev/null || true
rsync -a --ignore-existing style_profiles/   data/style_profiles/   2>/dev/null || true
rsync -a --ignore-existing content-templates/ data/content_templates/ 2>/dev/null || true
rsync -a --ignore-existing style-profiles/   data/style_profiles/   2>/dev/null || true

# Remove duplicates
rm -rf content_templates content-templates style_profiles style-profiles

# Move generated drafts
rsync -a --ignore-existing generated_content/ storage/ 2>/dev/null || true
rm -rf generated_content

echo "✅ Project folders cleaned. Update import paths in code."
