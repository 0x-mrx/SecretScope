#!/usr/bin/env bash

# SecretScope Environment Setup Script
# Works on Linux, macOS, and Git Bash/WSL on Windows

set -euo pipefail

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${BLUE}====================================================${NC}"
echo -e "${CYAN}    SecretScope - Enterprise Security Platform       ${NC}"
echo -e "${CYAN}                 Setup Wizard                        ${NC}"
echo -e "${BLUE}====================================================${NC}"
echo

# 1. Dependency Check
echo -e "${CYAN}[*] Checking system dependencies...${NC}"

# Check git
if command -v git >/dev/null 2>&1; then
    echo -e "  [${GREEN}✓${NC}] Git is installed: $(git --version)"
else
    echo -e "  [${RED}✗${NC}] Git is NOT installed. Please install git before proceeding."
    exit 1
fi

# Check Docker
DOCKER_AVAILABLE=true
if command -v docker >/dev/null 2>&1; then
    echo -e "  [${GREEN}✓${NC}] Docker is installed: $(docker --version)"
else
    echo -e "  [${YELLOW}⚠${NC}] Docker is NOT installed or not in PATH."
    DOCKER_AVAILABLE=false
fi

# Check Docker Compose
DOCKER_COMPOSE_AVAILABLE=true
if docker compose version >/dev/null 2>&1; then
    echo -e "  [${GREEN}✓${NC}] Docker Compose is installed: $(docker compose version)"
elif command -v docker-compose >/dev/null 2>&1; then
    echo -e "  [${GREEN}✓${NC}] docker-compose is installed: $(docker-compose --version)"
else
    echo -e "  [${YELLOW}⚠${NC}] Docker Compose is NOT installed."
    DOCKER_COMPOSE_AVAILABLE=false
fi

echo

# 2. Environment Configuration
echo -e "${CYAN}[*] Configuring environment variables...${NC}"

if [ -f .env ]; then
    echo -e "  [${YELLOW}⚠${NC}] .env file already exists. Skipping copying from .env.example."
else
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "  [${GREEN}✓${NC}] Copied .env.example to .env."
        
        # Try to generate secure credentials if python is available
        if command -v python3 >/dev/null 2>&1 || command -v python >/dev/null 2>&1; then
            PYTHON_CMD="python3"
            if ! command -v python3 >/dev/null 2>&1; then
                PYTHON_CMD="python"
            fi
            
            echo -e "  [*] Generating secure keys for .env..."
            
            # Generate JWT Secret Key
            SEC_KEY=$($PYTHON_CMD -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "")
            # Generate Fernet Encryption Key (32 bytes base64 encoded)
            ENC_KEY=$($PYTHON_CMD -c "import base64, os; print(base64.urlsafe_b64encode(os.urandom(32)).decode())" 2>/dev/null || echo "")
            
            if [ -n "$SEC_KEY" ] && [ -n "$ENC_KEY" ]; then
                # Replace keys in .env
                # Using sed. On macOS, sed -i requires '' or backup extension.
                if [[ "$OSTYPE" == "darwin"* ]]; then
                    sed -i '' "s|^SECRET_KEY=.*|SECRET_KEY=$SEC_KEY|g" .env
                    sed -i '' "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENC_KEY|g" .env
                else
                    sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$SEC_KEY|g" .env
                    sed -i "s|^ENCRYPTION_KEY=.*|ENCRYPTION_KEY=$ENC_KEY|g" .env
                fi
                echo -e "  [${GREEN}✓${NC}] Generated fresh SECRET_KEY and ENCRYPTION_KEY."
            else
                echo -e "  [${YELLOW}⚠${NC}] Could not generate secure keys automatically. Using default values."
            fi
        else
            echo -e "  [${YELLOW}⚠${NC}] Python not found. Using default values in .env. Please update them manually for production."
        fi
    else
        echo -e "  [${RED}✗${NC}] .env.example not found! Cannot create .env configuration."
        exit 1
    fi
fi
echo

# 3. Startup Prompt
if [ "$DOCKER_AVAILABLE" = true ] && [ "$DOCKER_COMPOSE_AVAILABLE" = true ]; then
    echo -e "${CYAN}[*] Docker and Docker Compose are available.${NC}"
    read -p "Do you want to start the SecretScope platform services now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}[*] Booting up all platform services via Docker Compose...${NC}"
        docker compose up --build -d
        
        echo
        echo -e "${GREEN}====================================================${NC}"
        echo -e "${GREEN}    SecretScope Services Started Successfully!       ${NC}"
        echo -e "${GREEN}====================================================${NC}"
        echo -e "Web Application: ${CYAN}http://localhost${NC}"
        echo -e "Default Credentials:"
        echo -e "  - Username: ${BLUE}admin@secretscope.local${NC}"
        echo -e "  - Password: ${BLUE}SecretScopeAdminPassword123!${NC}"
        echo -e "===================================================="
    else
        echo -e "${YELLOW}[*] Setup completed. You can start the services later using:${NC}"
        echo -e "    ${BLUE}docker compose up --build -d${NC}"
    fi
else
    echo -e "${YELLOW}====================================================${NC}"
    echo -e "${YELLOW}               Docker Setup Needed                  ${NC}"
    echo -e "${YELLOW}====================================================${NC}"
    echo -e "Please ensure Docker is installed and running, then execute:"
    echo -e "    ${BLUE}docker compose up --build -d${NC}"
    echo -e "===================================================="
fi
