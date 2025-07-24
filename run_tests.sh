#!/bin/bash

# Run tests script

echo "Installing test dependencies..."
pip install -r requirements.txt

echo -e "\n========================================="
echo "Running all tests with coverage..."
echo "========================================="
pytest

echo -e "\n========================================="
echo "Running unit tests only..."
echo "========================================="
pytest -m "not integration"

echo -e "\n========================================="
echo "Running tests with detailed output..."
echo "========================================="
pytest -vv

echo -e "\n========================================="
echo "Coverage report has been generated in htmlcov/"
echo "Open htmlcov/index.html to view detailed coverage report"
echo "========================================="