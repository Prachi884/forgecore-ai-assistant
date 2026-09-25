#!/usr/bin/env bash
# ─── ForgeCore Codespaces — first-run setup ─────────────────
# Runs once when the Codespace is created.

set -euo pipefail

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ForgeCore AI Assistant — setting up dev container"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Upgrade pip
python -m pip install --upgrade pip wheel setuptools --quiet

# Install the project in editable mode with dev extras
pip install -e ".[dev]" --quiet

# Copy .env.example to .env if .env doesn't exist yet
if [ ! -f .env ]; then
  cp .env.example .env
  echo "✓ Created .env from .env.example (fill in your GEMINI_API_KEY later)"
fi

echo ""
echo "✓ Setup complete."
echo "  Try:  make run"
echo "  Or:   make test"
