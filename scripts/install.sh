#!/bin/bash

# Code Builder Overlay Installer
# Simple approach: .cb/ = project copy, cb_cb_docs/ = cb_docs/ copy

set -e

echo "🔧 Code Builder Overlay Installer"
echo "================================="

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

echo "📋 Detected OS: $OS"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Not in a git repository. Please run from project root."
    exit 1
fi

# Check if already installed
if [ -d ".cb" ]; then
    echo "⚠️  Overlay already exists. Reinstalling..."
    rm -rf .cb
fi

# Ensure cb_docs exists and is complete (source of truth for documentation)
if [ ! -d "cb_docs" ]; then
    echo "⚠️  cb_docs/ not found. Creating from git history..."
    git checkout 2bc80cc -- docs && cp -r docs cb_docs && rm -rf docs
else
    echo "   Checking cb_docs/ for missing files..."
    # Check if key directories exist, restore if missing
    if [ ! -d "cb_docs/rules" ]; then
        echo "   Restoring missing cb_docs/rules/..."
        git checkout 2bc80cc -- docs/rules && cp -r docs/rules cb_docs/ && rm -rf docs/rules
    fi
    if [ ! -d "cb_docs/templates" ]; then
        echo "   Restoring missing cb_docs/templates/..."
        git checkout 2bc80cc -- docs/templates && cp -r docs/templates cb_docs/ && rm -rf docs/templates
    fi
    if [ ! -d "cb_docs/adrs" ]; then
        echo "   Restoring missing cb_docs/adrs/..."
        git checkout 2bc80cc -- docs/adrs && cp -r docs/adrs cb_docs/ && rm -rf docs/adrs
    fi
    # Check for other key files
    if [ ! -f "cb_docs/rules/guardrails.json" ]; then
        echo "   Restoring missing guardrails.json..."
        git checkout 2bc80cc -- docs/rules/guardrails.json && cp docs/rules/guardrails.json cb_docs/rules/ && rm -rf docs/rules/guardrails.json
    fi
fi

echo "📁 Creating overlay structure..."

# Create .cb directory (only essential files)
echo "   Creating .cb/ structure..."
mkdir -p .cb

# Copy only essential files
echo "   Copying essential files..."
cp -r builder .cb/
cp -r .cursor .cb/  # Copy .cursor/rules for Code Builder
cp .cursorrules .cb/  # Copy .cursorrules for Cursor configuration
cp -r .github .cb/  # Copy .github/ for GitHub Actions and templates

# Copy important configuration files
cp .markdownlint.json .cb/  # Markdown linting configuration
cp cspell.json .cb/  # Spell checking configuration
cp eslint.config.js .cb/  # ESLint configuration
cp pytest.ini .cb/  # Python testing configuration
cp tsconfig.json .cb/  # TypeScript configuration
cp tsconfig.build.json .cb/  # TypeScript build configuration
cp vitest.config.ts .cb/  # Testing configuration
cp package.json .cb/  # Node.js package configuration
cp pnpm-workspace.yaml .cb/  # pnpm workspace configuration
cp LICENSE .cb/  # License file

mkdir -p .cb/cache  # Create empty cache directory
mkdir -p .cb/bin

# cb_docs directory is the source of truth for documentation
echo "   Using cb_docs/ as documentation source..."

# Create virtual environment in root and install dependencies
echo "   Creating virtual environment and installing dependencies..."
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Create wrapper scripts
echo "   Creating wrapper scripts..."

# .cb/bin/cb - main CLI wrapper
mkdir -p .cb/bin
cat > .cb/bin/cb << 'EOF'
#!/bin/bash
# Code Builder Overlay CLI Wrapper

# Set overlay environment
export CB_OVERLAY_MODE=true
export CB_DOCS_DIR="$(pwd)/cb_docs"
export CB_CACHE_DIR="$(pwd)/.cb/cache"
export CB_ENGINE_DIR="$(pwd)/.cb"
export CB_MODE=overlay

# Add .cb/bin to PATH
if [[ ":$PATH:" != *":$(pwd)/.cb/bin:"* ]]; then
    export PATH="$(pwd)/.cb/bin:$PATH"
fi

# Activate virtual environment
if [ -f "$(pwd)/.venv/bin/activate" ]; then
    source "$(pwd)/.venv/bin/activate"
fi

# Set PYTHONPATH to include .cb
export PYTHONPATH="$(pwd)/.cb:$PYTHONPATH"

# Run the CLI from .cb/
exec "$(pwd)/.venv/bin/python" -m builder.core.cli "$@"
EOF

chmod +x .cb/bin/cb

# .cb/activate - environment activation
cat > .cb/activate << 'EOF'
#!/bin/bash
# Code Builder Overlay Environment Activation

# Set overlay environment
export CB_OVERLAY_MODE=true
export CB_DOCS_DIR="$(pwd)/cb_docs"
export CB_CACHE_DIR="$(pwd)/.cb/cache"
export CB_ENGINE_DIR="$(pwd)/.cb"
export CB_MODE=overlay

# Add .cb/bin to PATH
if [[ ":$PATH:" != *":$(pwd)/.cb/bin:"* ]]; then
    export PATH="$(pwd)/.cb/bin:$PATH"
fi

# Activate virtual environment
if [ -f "$(pwd)/.venv/bin/activate" ]; then
    source "$(pwd)/.venv/bin/activate"
fi

echo "🔧 Code Builder Overlay activated!"
echo "   CB_MODE: $CB_MODE"
echo "   CB_DOCS_DIR: $CB_DOCS_DIR"
echo "   CB_CACHE_DIR: $CB_CACHE_DIR"
echo "   CB_ENGINE_DIR: $CB_ENGINE_DIR"
echo ""
echo "💡 Add 'source .cb/activate' to your shell rc file for automatic activation"
echo "   Commands: cb help, cb discover, cb context, cb docs, etc."
EOF

chmod +x .cb/activate

# Update .gitignore
echo "   Updating .gitignore..."
if ! grep -q "^\.cb/" .gitignore 2>/dev/null; then
    echo "" >> .gitignore
    echo "# Code Builder Overlay" >> .gitignore
    echo ".cb/" >> .gitignore
    echo "cb_cb_docs/" >> .gitignore
fi

echo ""
echo "✅ Code Builder Overlay installed successfully!"
echo ""
echo "🚀 Next steps:"
echo "   1. Activate: source .cb/activate"
echo "   2. Test: cb help"
echo "   3. Add to shell: echo 'source .cb/activate' >> ~/.bashrc"
echo ""
echo "📁 Structure:"
echo "   .cb/     - Essential overlay files (builder/, bin/, cache/)"
echo "   .venv/   - Virtual environment (created during installation)"
echo "   cb_docs/ - Documentation directory (source of truth for docs)"
echo ""
echo "💡 The overlay system is now ready to use!"