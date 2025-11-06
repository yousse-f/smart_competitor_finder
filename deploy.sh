#!/bin/bash

# Smart Competitor Finder - Automated Deployment Script
# Usage: ./deploy.sh [production|staging|development]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
PROJECT_NAME="smart_competitor_finder"
COMPOSE_FILE="docker-compose.yml"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    if [ ! -f backend/.env ]; then
        log_error "backend/.env file not found. Please create it from backend/.env.example"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Environment setup
setup_environment() {
    log_info "Setting up $ENVIRONMENT environment..."
    
    case $ENVIRONMENT in
        production)
            export COMPOSE_PROJECT_NAME="${PROJECT_NAME}_prod"
            ;;
        staging)
            export COMPOSE_PROJECT_NAME="${PROJECT_NAME}_staging"
            ;;
        development)
            export COMPOSE_PROJECT_NAME="${PROJECT_NAME}_dev"
            ;;
        *)
            log_error "Unknown environment: $ENVIRONMENT"
            exit 1
            ;;
    esac
    
    log_success "Environment set to: $ENVIRONMENT"
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    log_success "Docker images built successfully"
}

# Stop existing containers
stop_containers() {
    log_info "Stopping existing containers..."
    
    docker-compose -f $COMPOSE_FILE down
    
    log_success "Containers stopped"
}

# Start containers
start_containers() {
    log_info "Starting containers..."
    
    docker-compose -f $COMPOSE_FILE up -d
    
    log_success "Containers started"
}

# Health check
health_check() {
    log_info "Performing health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        # Check backend
        if curl -f -s http://localhost:8000/health > /dev/null 2>&1; then
            log_success "Backend is healthy"
            
            # Check frontend
            if curl -f -s http://localhost:3000 > /dev/null 2>&1; then
                log_success "Frontend is healthy"
                return 0
            fi
        fi
        
        sleep 2
        attempt=$((attempt + 1))
    done
    
    log_error "Health check failed after $max_attempts attempts"
    docker-compose -f $COMPOSE_FILE logs
    return 1
}

# Show status
show_status() {
    log_info "Container status:"
    docker-compose -f $COMPOSE_FILE ps
    
    echo ""
    log_info "Service URLs:"
    echo "  - Frontend: http://localhost:3000"
    echo "  - Backend:  http://localhost:8000"
    echo "  - API Docs: http://localhost:8000/docs"
    
    echo ""
    log_info "Useful commands:"
    echo "  - View logs:    docker-compose logs -f"
    echo "  - Stop all:     docker-compose down"
    echo "  - Restart:      docker-compose restart"
    echo "  - Shell backend: docker-compose exec backend bash"
    echo "  - Shell frontend: docker-compose exec frontend sh"
}

# Backup data
backup_data() {
    log_info "Creating backup..."
    
    local backup_dir="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $backup_dir
    
    # Backup reports
    if [ -d "backend/reports" ]; then
        cp -r backend/reports $backup_dir/
        log_success "Reports backed up to $backup_dir"
    fi
    
    # Backup environment
    if [ -f "backend/.env" ]; then
        cp backend/.env $backup_dir/
        log_success "Environment backed up"
    fi
}

# Main deployment flow
main() {
    echo ""
    log_info "🚀 Starting deployment of Smart Competitor Finder"
    log_info "Environment: $ENVIRONMENT"
    echo ""
    
    check_prerequisites
    setup_environment
    
    # Ask for confirmation in production
    if [ "$ENVIRONMENT" = "production" ]; then
        read -p "⚠️  Deploy to PRODUCTION? This will rebuild all images. (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_warning "Deployment cancelled"
            exit 0
        fi
        
        backup_data
    fi
    
    stop_containers
    build_images
    start_containers
    
    log_info "Waiting for services to start..."
    sleep 10
    
    if health_check; then
        echo ""
        log_success "🎉 Deployment successful!"
        echo ""
        show_status
    else
        log_error "Deployment failed - services are not healthy"
        exit 1
    fi
}

# Run main
main
