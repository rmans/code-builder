#!/bin/bash
# Code Builder Overlay Installer
# This script sets up the Code Builder overlay in the current directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
DRY_RUN=false
KEEP_EXISTING=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --keep-existing)
            KEEP_EXISTING=true
            shift
            ;;
        --help)
            echo "Code Builder Overlay Installer"
            echo ""
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --dry-run       Show what would be done without making changes"
            echo "  --keep-existing Keep existing .cb directory if it exists"
            echo "  --help          Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    log_warning "Not in a git repository. Initializing git..."
    if [ "$DRY_RUN" = false ]; then
        git init
    fi
fi

# Detect OS and WSL
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q Microsoft /proc/version 2>/dev/null; then
            echo "wsl"
        else
            echo "linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

OS=$(detect_os)
log_info "Detected OS: $OS"

# Check if .cb already exists
if [ -d ".cb" ] && [ "$KEEP_EXISTING" = false ]; then
    log_error ".cb directory already exists. Use --keep-existing to keep it or remove it first."
    exit 1
fi

# Create directories
log_info "Creating overlay skeleton..."
if [ "$DRY_RUN" = false ]; then
    mkdir -p .cb/{bin,engine,venv,node_modules,cache,workspace,sessions,config}
    mkdir -p cb_docs/{decisions,tasks,discovery,context}
else
    log_info "Would create .cb/ and cb_docs/ directories"
fi

# Copy engine
log_info "Copying Code Builder engine..."
if [ "$DRY_RUN" = false ]; then
    if [ -d "builder" ]; then
        rsync -a builder .cb/engine/
        cp requirements.txt package.json .cb/engine/ 2>/dev/null || true
    else
        log_error "builder/ directory not found. Please run this script from the Code Builder repository root."
        exit 1
    fi
else
    log_info "Would copy builder/ to .cb/engine/"
fi

# Create virtual environment
log_info "Creating Python virtual environment..."
if [ "$DRY_RUN" = false ]; then
    python3 -m venv .cb/venv
    log_success "Virtual environment created"
else
    log_info "Would create Python virtual environment"
fi

# Install Python dependencies
log_info "Installing Python dependencies..."
if [ "$DRY_RUN" = false ]; then
    if [ -f ".cb/engine/requirements.txt" ]; then
        .cb/venv/bin/python -m pip install -r .cb/engine/requirements.txt
        log_success "Python dependencies installed"
    else
        log_warning "No requirements.txt found, skipping Python dependencies"
    fi
else
    log_info "Would install Python dependencies"
fi

# Install Node dependencies
log_info "Installing Node dependencies..."
if [ "$DRY_RUN" = false ]; then
    if [ -f ".cb/engine/package.json" ]; then
        cd .cb/engine
        if command -v pnpm >/dev/null 2>&1; then
            pnpm install
        else
            npm install
        fi
        cd ../..
        log_success "Node dependencies installed"
    else
        log_warning "No package.json found, skipping Node dependencies"
    fi
else
    log_info "Would install Node dependencies"
fi

# Create wrapper scripts
log_info "Creating wrapper scripts..."
if [ "$DRY_RUN" = false ]; then
    # Create cb wrapper
    cat > .cb/bin/cb << 'EOF'
#!/bin/bash
# Code Builder Overlay Wrapper
# This script sets up the overlay environment and routes commands to the engine

# Set overlay environment variables
export CB_OVERLAY_MODE=true
export CB_DOCS_DIR="$(pwd)/cb_docs"
export CB_CACHE_DIR="$(pwd)/.cb/cache"
export CB_ENGINE_DIR="$(pwd)/.cb/engine"
export CB_MODE=overlay

# Add .cb/bin to PATH if not already there
if [[ ":$PATH:" != *":$(pwd)/.cb/bin:"* ]]; then
    export PATH="$(pwd)/.cb/bin:$PATH"
fi

# Activate virtual environment if it exists
if [ -f "$(pwd)/.cb/venv/bin/activate" ]; then
    source "$(pwd)/.cb/venv/bin/activate"
fi

# Set PYTHONPATH to include the engine directory
export PYTHONPATH="$(pwd)/.cb/engine:$PYTHONPATH"

# Route to the engine CLI
exec "$(pwd)/.cb/venv/bin/python" -m builder.core.cli "$@"
EOF

    # Create activation script
    cat > .cb/activate << 'EOF'
#!/bin/bash
# Code Builder Overlay Environment Activation
# Source this file to activate the overlay environment

# Set overlay environment variables
export CB_OVERLAY_MODE=true
export CB_DOCS_DIR="$(pwd)/cb_docs"
export CB_CACHE_DIR="$(pwd)/.cb/cache"
export CB_ENGINE_DIR="$(pwd)/.cb/engine"
export CB_MODE=overlay

# Add .cb/bin to PATH if not already there
if [[ ":$PATH:" != *":$(pwd)/.cb/bin:"* ]]; then
    export PATH="$(pwd)/.cb/bin:$PATH"
fi

# Activate virtual environment if it exists
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

    chmod +x .cb/bin/cb
    log_success "Wrapper scripts created"
else
    log_info "Would create wrapper scripts"
fi

# Update .gitignore
log_info "Updating .gitignore..."
if [ "$DRY_RUN" = false ]; then
    if ! grep -q '.cb/' .gitignore 2>/dev/null; then
        echo "" >> .gitignore
        echo "# Code Builder Overlay" >> .gitignore
        echo ".cb/" >> .gitignore
        echo ".cb/*" >> .gitignore
        log_success ".gitignore updated"
    else
        log_info ".cb/ already in .gitignore"
    fi
else
    log_info "Would update .gitignore"
fi

# Test installation
if [ "$DRY_RUN" = false ]; then
    log_info "Testing installation..."
    if ./.cb/bin/cb --help >/dev/null 2>&1; then
        log_success "Installation test passed"
    else
        log_error "Installation test failed"
        exit 1
    fi
fi

# Print next steps
echo ""
log_success "Code Builder Overlay installed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate the overlay environment:"
echo "   source .cb/activate"
echo ""
echo "2. Try some commands:"
echo "   cb --help"
echo "   cb discover"
echo "   cb context"
echo "   cb docs"
echo ""
echo "3. Add to your shell rc file for automatic activation:"
echo "   echo 'source .cb/activate' >> ~/.bashrc  # or ~/.zshrc"
echo ""
echo "4. The overlay is now ready to use!"
echo "   - Documentation goes in cb_docs/"
echo "   - Cache and temporary files go in .cb/"
echo "   - .cb/ is gitignored, cb_docs/ is tracked"
echo ""

if [ "$DRY_RUN" = true ]; then
    log_info "This was a dry run. No changes were made."
fi
