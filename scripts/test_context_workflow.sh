#!/bin/bash

# Test script to verify context workflow logic
echo "🧪 Testing Context Workflow Logic"
echo "================================="

# Test 1: Auth context (documentation-connected)
echo ""
echo "Test 1: Auth context (documentation-connected)"
echo "----------------------------------------------"
python3 builder/cli.py ctx:build-enhanced src/auth/login.ts --purpose implement --feature auth --stacks typescript,react --token-limit 8000

if [ -f "builder/cache/pack_context.json" ] && [ -f "builder/cache/context.md" ]; then
    echo "✅ Files generated successfully"
    
    # Test validation
    if grep -q "## Rules" builder/cache/context.md && \
       grep -q "## Code" builder/cache/context.md && \
       grep -q "## Acceptance Criteria" builder/cache/context.md && \
       grep -q "## Architecture" builder/cache/context.md; then
        echo "✅ Documentation-connected context validation passed"
    else
        echo "❌ Documentation-connected context validation failed"
        exit 1
    fi
else
    echo "❌ Files not generated"
    exit 1
fi

# Test 2: Code-only context
echo ""
echo "Test 2: Code-only context"
echo "-------------------------"
python3 builder/cli.py ctx:build-enhanced src/index.ts --purpose implement --stacks typescript,react --token-limit 6000

if [ -f "builder/cache/pack_context.json" ] && [ -f "builder/cache/context.md" ]; then
    echo "✅ Files generated successfully"
    
    # Test validation
    if grep -q "## Rules" builder/cache/context.md && \
       grep -q "## Code" builder/cache/context.md; then
        if grep -q "## Acceptance Criteria" builder/cache/context.md; then
            echo "❌ Code-only context incorrectly detected as documentation-connected"
            exit 1
        else
            echo "✅ Code-only context validation passed"
        fi
    else
        echo "❌ Code-only context validation failed"
        exit 1
    fi
else
    echo "❌ Files not generated"
    exit 1
fi

# Test 3: JSON structure validation
echo ""
echo "Test 3: JSON structure validation"
echo "---------------------------------"
python3 -c "
import json
with open('builder/cache/pack_context.json', 'r') as f:
    data = json.load(f)

# Check for rules_md (always required)
if 'rules_md' not in data.get('constraints', {}):
    print('❌ ERROR: Missing rules_md in constraints')
    exit(1)

# Check for code section (always required)
if 'code' not in data or not data['code']:
    print('❌ ERROR: Missing code section or empty code section')
    exit(1)

print('✅ JSON structure validation passed')
"

echo ""
echo "🎉 All tests passed! Context workflow is ready for CI."
