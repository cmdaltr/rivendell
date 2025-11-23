#!/bin/bash
# Docker Clean-up Script for Rivendell
# Clears Docker caches and resets build environment
# Use this when experiencing Docker build issues

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         Docker Clean-up Script for Rivendell              ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Function to show disk usage
show_disk_usage() {
    echo -e "${BLUE}Current Docker disk usage:${NC}"
    docker system df
    echo ""
}

# Function to kill running builds
kill_builds() {
    echo -e "${YELLOW}Killing any running Docker builds...${NC}"
    pkill -f "docker-compose.*build" 2>/dev/null || true
    pkill -f "docker.*build" 2>/dev/null || true
    echo -e "${GREEN}✓ Build processes terminated${NC}"
    echo ""
}

# Function to stop containers
stop_containers() {
    echo -e "${YELLOW}Stopping Rivendell containers...${NC}"
    cd "$PROJECT_ROOT"
    docker-compose -f docker/docker-compose.yml down 2>/dev/null || true
    docker-compose down 2>/dev/null || true
    echo -e "${GREEN}✓ Containers stopped${NC}"
    echo ""
}

# Function to clean build cache
clean_build_cache() {
    echo -e "${YELLOW}Cleaning Docker build cache...${NC}"
    docker builder prune -a -f
    echo -e "${GREEN}✓ Build cache cleared${NC}"
    echo ""
}

# Function to clean images
clean_images() {
    echo -e "${YELLOW}Removing unused Docker images...${NC}"
    docker image prune -a -f
    echo -e "${GREEN}✓ Unused images removed${NC}"
    echo ""
}

# Function to clean containers
clean_containers() {
    echo -e "${YELLOW}Removing stopped containers...${NC}"
    docker container prune -f
    echo -e "${GREEN}✓ Stopped containers removed${NC}"
    echo ""
}

# Function to clean networks
clean_networks() {
    echo -e "${YELLOW}Removing unused networks...${NC}"
    docker network prune -f 2>/dev/null || true
    echo -e "${GREEN}✓ Unused networks removed${NC}"
    echo ""
}

# Function to clean volumes (DANGEROUS)
clean_volumes() {
    echo -e "${RED}⚠️  WARNING: This will delete Docker volumes!${NC}"
    echo -e "${RED}⚠️  All data in volumes will be PERMANENTLY LOST!${NC}"
    echo -e "${YELLOW}Do you want to remove Docker volumes? (yes/no)${NC}"
    read -r response
    if [[ "$response" == "yes" ]]; then
        echo -e "${YELLOW}Removing unused volumes...${NC}"
        docker volume prune -f
        echo -e "${GREEN}✓ Volumes removed${NC}"
    else
        echo -e "${BLUE}✓ Volumes preserved${NC}"
    fi
    echo ""
}

# Function to clean Rivendell-specific resources
clean_rivendell_specific() {
    echo -e "${YELLOW}Removing Rivendell-specific Docker resources...${NC}"

    # Stop and remove Rivendell containers
    docker ps -a | grep elrond | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

    # Remove Rivendell images
    docker images | grep elrond | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true

    echo -e "${GREEN}✓ Rivendell-specific resources removed${NC}"
    echo ""
}

# Function to verify Docker is running
check_docker() {
    if ! docker info >/dev/null 2>&1; then
        echo -e "${RED}✗ Docker is not running!${NC}"
        echo -e "${YELLOW}Please start Docker Desktop or Docker daemon and try again.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Docker is running${NC}"
    echo ""
}

# Main menu
show_menu() {
    echo -e "${BLUE}Select clean-up level:${NC}"
    echo ""
    echo "  1) Quick Clean (Build cache + unused images)"
    echo "  2) Standard Clean (Build cache + images + containers)"
    echo "  3) Deep Clean (Everything except volumes)"
    echo "  4) Nuclear Clean (Everything including volumes)"
    echo "  5) Rivendell Only (Only Rivendell-specific resources)"
    echo "  6) Show Disk Usage"
    echo "  7) Exit"
    echo ""
}

# Parse command line arguments
LEVEL=""
AUTO_REBUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --quick|-q)
            LEVEL="quick"
            shift
            ;;
        --standard|-s)
            LEVEL="standard"
            shift
            ;;
        --deep|-d)
            LEVEL="deep"
            shift
            ;;
        --nuclear|-n)
            LEVEL="nuclear"
            shift
            ;;
        --rivendell|-r)
            LEVEL="rivendell"
            shift
            ;;
        --rebuild|-b)
            AUTO_REBUILD=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -q, --quick       Quick clean (build cache + unused images)"
            echo "  -s, --standard    Standard clean (+ containers)"
            echo "  -d, --deep        Deep clean (everything except volumes)"
            echo "  -n, --nuclear     Nuclear clean (everything including volumes)"
            echo "  -r, --rivendell   Clean only Rivendell-specific resources"
            echo "  -b, --rebuild     Automatically rebuild after cleaning"
            echo "  -h, --help        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0 --quick                # Quick clean"
            echo "  $0 --deep --rebuild       # Deep clean and rebuild"
            echo "  $0                        # Interactive mode"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check Docker is running
check_docker

# Show initial disk usage
echo -e "${BLUE}Before cleanup:${NC}"
show_disk_usage

# If no level specified, show menu
if [ -z "$LEVEL" ]; then
    while true; do
        show_menu
        read -p "Enter choice [1-7]: " choice
        case $choice in
            1) LEVEL="quick"; break;;
            2) LEVEL="standard"; break;;
            3) LEVEL="deep"; break;;
            4) LEVEL="nuclear"; break;;
            5) LEVEL="rivendell"; break;;
            6) show_disk_usage; continue;;
            7) echo "Exiting..."; exit 0;;
            *) echo -e "${RED}Invalid choice. Please try again.${NC}"; continue;;
        esac
    done
fi

# Execute cleanup based on level
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  Starting: $(printf '%-44s' "${LEVEL^^} CLEAN")  ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

kill_builds
stop_containers

case $LEVEL in
    quick)
        clean_build_cache
        clean_images
        ;;
    standard)
        clean_build_cache
        clean_images
        clean_containers
        clean_networks
        ;;
    deep)
        clean_build_cache
        clean_images
        clean_containers
        clean_networks
        echo -e "${YELLOW}Running system prune...${NC}"
        docker system prune -a -f
        echo -e "${GREEN}✓ System prune complete${NC}"
        echo ""
        ;;
    nuclear)
        echo -e "${RED}⚠️  NUCLEAR OPTION SELECTED${NC}"
        echo -e "${RED}⚠️  This will delete ALL Docker data including volumes!${NC}"
        echo -e "${YELLOW}Type 'YES' to confirm nuclear clean: ${NC}"
        read -r confirm
        if [[ "$confirm" == "YES" ]]; then
            clean_build_cache
            clean_images
            clean_containers
            clean_networks
            echo -e "${YELLOW}Running system prune with volumes...${NC}"
            docker system prune -a --volumes -f
            echo -e "${GREEN}✓ Nuclear clean complete${NC}"
            echo ""
        else
            echo -e "${BLUE}Nuclear clean cancelled${NC}"
            exit 0
        fi
        ;;
    rivendell)
        clean_rivendell_specific
        clean_build_cache
        ;;
esac

# Show final disk usage
echo -e "${BLUE}After cleanup:${NC}"
show_disk_usage

# Calculate space saved
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║             Clean-up Complete!                             ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Ask about rebuild
if [ "$AUTO_REBUILD" = false ]; then
    echo -e "${YELLOW}Do you want to rebuild Rivendell now? (yes/no)${NC}"
    read -r rebuild
else
    rebuild="yes"
fi

if [[ "$rebuild" == "yes" ]]; then
    echo ""
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║             Starting Rebuild                               ║${NC}"
    echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    echo -e "${YELLOW}Building Rivendell (this may take 10-20 minutes)...${NC}"
    echo ""

    if docker-compose -f docker/docker-compose.yml build --no-cache; then
        echo ""
        echo -e "${GREEN}✓ Build completed successfully!${NC}"
        echo ""
        echo -e "${YELLOW}Start services with:${NC}"
        echo -e "${BLUE}  docker-compose -f docker/docker-compose.yml up -d${NC}"
    else
        echo ""
        echo -e "${RED}✗ Build failed!${NC}"
        echo -e "${YELLOW}Check the error messages above for details.${NC}"
        exit 1
    fi
else
    echo ""
    echo -e "${BLUE}To rebuild manually, run:${NC}"
    echo -e "${BLUE}  cd $PROJECT_ROOT${NC}"
    echo -e "${BLUE}  docker-compose -f docker/docker-compose.yml build --no-cache${NC}"
fi

echo ""
echo -e "${GREEN}Done! 🎉${NC}"
