#!/bin/bash
# Helper script to run tests with the correct Python interpreter

# Find the Python interpreter with Google packages
PYTHON_CMD=""

# Try anaconda first (most likely to have packages)
if [ -f "/Users/thomasmulhern/anaconda3/bin/python3" ]; then
    PYTHON_CMD="/Users/thomasmulhern/anaconda3/bin/python3"
# Try system python
elif command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
else
    echo "❌ Python 3 not found"
    exit 1
fi

echo "🐍 Using Python: $PYTHON_CMD"
echo "📍 Current directory: $(pwd)"
echo ""

# Run the requested test
if [ $# -eq 0 ]; then
    echo "🧪 Running Simple Integration Test..."
    $PYTHON_CMD test_simple_integration.py
else
    echo "🧪 Running: $1"
    $PYTHON_CMD "$1"
fi