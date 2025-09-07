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
if [ -d ".cb" ] || [ -d "cb_docs" ]; then
    echo "⚠️  Overlay already exists. Reinstalling..."
    rm -rf .cb cb_docs
fi

echo "📁 Creating overlay structure..."

# Create .cb directory (only essential files)
echo "   Creating .cb/ structure..."
mkdir -p .cb

# Copy only essential files
echo "   Copying essential files..."
cp -r builder .cb/
mkdir -p .cb/cache  # Create empty cache directory
mkdir -p .cb/bin

# cb_docs directory already exists, skipping copy
echo "   cb_docs/ already exists, skipping copy..."

# Create virtual environment in .cb/
echo "   Creating virtual environment..."
python3 -m venv .cb/venv

# Install dependencies
echo "   Installing dependencies..."
.cb/venv/bin/pip install -r requirements.txt

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
if [ -f "$(pwd)/.cb/venv/bin/activate" ]; then
    source "$(pwd)/.cb/venv/bin/activate"
fi

# Set PYTHONPATH to include .cb
export PYTHONPATH="$(pwd)/.cb:$PYTHONPATH"

# Run the CLI from .cb/
exec "$(pwd)/.cb/venv/bin/python" -m builder.core.cli "$@"
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
if [ -f "$(pwd)/.cb/venv/bin/activate" ]; then
    source "$(pwd)/.cb/venv/bin/activate"
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
echo "   .cb/     - Essential overlay files (builder/, venv/, bin/, cache/)"
echo "   cb_docs/ - Documentation directory (outputs go here)"
echo ""
echo "💡 The overlay system is now ready to use!"