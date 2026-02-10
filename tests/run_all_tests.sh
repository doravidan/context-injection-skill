#!/bin/bash
# Context Injection Skill — Run All Tests
# Usage: ./run_all_tests.sh [--evaluate]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TESTS_DIR="$SCRIPT_DIR"
RESULTS_DIR="$SCRIPT_DIR/results"

# Check for API key
if [ -z "${ANTHROPIC_API_KEY:-}" ]; then
    echo "❌ ANTHROPIC_API_KEY not set"
    echo "   export ANTHROPIC_API_KEY=sk-ant-..."
    exit 1
fi

# Check for anthropic package
if ! python3 -c "import anthropic" 2>/dev/null; then
    echo "❌ anthropic package not installed"
    echo "   pip3 install anthropic"
    exit 1
fi

# Create results dir
mkdir -p "$RESULTS_DIR"

# Forward args (e.g., --evaluate)
EXTRA_ARGS="${@}"

echo "🧪 Running all context injection tests..."
echo ""

python3 "$TESTS_DIR/test-runner.py" --all --output "$RESULTS_DIR" $EXTRA_ARGS

echo ""
echo "📁 Results saved to: $RESULTS_DIR"
