#!/bin/bash
# Script to run all tests for URL Shortener
# Usage: bash run_tests.sh

echo "============================================"
echo "URL Shortener - Test Suite"
echo "============================================"
echo ""

echo "Running all tests..."
echo ""

python -m pytest tests/ -v --tb=short

echo ""
echo "============================================"
echo "Test run complete!"
echo "============================================"
