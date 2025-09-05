#!/bin/bash

# Setup script for evaluation dependencies
# This script installs all required dependencies and creates necessary directories

set -e  # Exit on any error

echo "🚀 Setting up evaluation dependencies..."

# Install pnpm dev dependencies
echo "📦 Installing pnpm dev dependencies..."
pnpm install

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
# Create virtual environment if it doesn't exist
if [ ! -d ".venv/bin" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi
.venv/bin/pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating evaluation directories..."
mkdir -p builder/cache
mkdir -p builder/evaluators
mkdir -p builder/prompts

# Create .gitkeep file to ensure directories are tracked by git
echo "📝 Creating .gitkeep files..."
touch builder/cache/.gitkeep

echo "✅ Setup complete! All evaluation dependencies installed and directories created."
