@echo off
REM Script to run all tests for URL Shortener
REM Usage: run_tests.bat

echo ============================================
echo URL Shortener - Test Suite
echo ============================================
echo.

echo Running all tests...
echo.

py -m pytest tests/ -v --tb=short

echo.
echo ============================================
echo Test run complete!
echo ============================================
