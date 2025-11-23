#!/bin/bash
# Elrond Test Runner Script
#
# Convenience script for running tests with common configurations

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ELROND_ROOT="$(dirname "$SCRIPT_DIR")"

# Default values
TEST_TYPE="all"
COVERAGE=false
VERBOSE=false
PARALLEL=false
MARKERS=""
PATTERN=""
STOP_ON_FIRST=false

# Help message
show_help() {
    cat << EOF
Elrond Test Runner

Usage: ./run_tests.sh [OPTIONS]

Options:
    -h, --help              Show this help message
    -a, --all               Run all tests (default)
    -u, --unit              Run only unit tests
    -i, --integration       Run only integration tests
    -w, --web               Run only web API tests
    -c, --coverage          Generate coverage report
    -v, --verbose           Verbose output
    -p, --parallel          Run tests in parallel
    -k, --keyword PATTERN   Run tests matching pattern
    -m, --marker MARKER     Run tests with specific marker
    -x, --stop-first        Stop on first failure
    -q, --quick             Quick mode (no coverage, parallel)
    -f, --fast              Fast mode (unit tests only, parallel, no coverage)

Examples:
    # Run all tests with coverage
    ./run_tests.sh --all --coverage

    # Run only unit tests in parallel
    ./run_tests.sh --unit --parallel

    # Run tests matching "mount"
    ./run_tests.sh -k mount

    # Quick test run
    ./run_tests.sh --quick

    # Fast unit tests only
    ./run_tests.sh --fast
EOF
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -a|--all)
            TEST_TYPE="all"
            shift
            ;;
        -u|--unit)
            TEST_TYPE="unit"
            shift
            ;;
        -i|--integration)
            TEST_TYPE="integration"
            shift
            ;;
        -w|--web)
            TEST_TYPE="web"
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -k|--keyword)
            PATTERN="$2"
            shift 2
            ;;
        -m|--marker)
            MARKERS="$2"
            shift 2
            ;;
        -x|--stop-first)
            STOP_ON_FIRST=true
            shift
            ;;
        -q|--quick)
            PARALLEL=true
            COVERAGE=false
            shift
            ;;
        -f|--fast)
            TEST_TYPE="unit"
            PARALLEL=true
            COVERAGE=false
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Print header
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Elrond Test Suite Runner          ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Change to test directory
cd "$SCRIPT_DIR"

# Build pytest command
PYTEST_CMD="pytest"

# Add test type marker
if [ "$TEST_TYPE" != "all" ]; then
    MARKERS="$TEST_TYPE"
fi

# Add markers
if [ ! -z "$MARKERS" ]; then
    PYTEST_CMD="$PYTEST_CMD -m $MARKERS"
    echo -e "${YELLOW}Test Markers:${NC} $MARKERS"
fi

# Add keyword pattern
if [ ! -z "$PATTERN" ]; then
    PYTEST_CMD="$PYTEST_CMD -k \"$PATTERN\""
    echo -e "${YELLOW}Keyword Pattern:${NC} $PATTERN"
fi

# Add coverage
if [ "$COVERAGE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD --cov=elrond --cov-report=html --cov-report=term-missing"
    echo -e "${YELLOW}Coverage:${NC} Enabled"
fi

# Add verbose
if [ "$VERBOSE" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -v"
    echo -e "${YELLOW}Verbosity:${NC} Enabled"
fi

# Add parallel
if [ "$PARALLEL" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -n auto"
    echo -e "${YELLOW}Parallel:${NC} Enabled"
fi

# Add stop on first failure
if [ "$STOP_ON_FIRST" = true ]; then
    PYTEST_CMD="$PYTEST_CMD -x"
    echo -e "${YELLOW}Stop on First:${NC} Enabled"
fi

echo ""
echo -e "${GREEN}Running tests...${NC}"
echo -e "${BLUE}Command: $PYTEST_CMD${NC}"
echo ""

# Run tests
eval $PYTEST_CMD
TEST_RESULT=$?

echo ""

# Show results
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"

    if [ "$COVERAGE" = true ]; then
        echo ""
        echo -e "${BLUE}Coverage report generated:${NC}"
        echo -e "  HTML: ${SCRIPT_DIR}/htmlcov/index.html"
        echo ""
        echo -e "${YELLOW}To view coverage report:${NC}"
        echo -e "  open htmlcov/index.html"
    fi
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit $TEST_RESULT
fi

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Test Run Complete                  ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"

exit 0
