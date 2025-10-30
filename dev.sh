#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}$1${NC}"
}

print_warning() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

# Function to show help
show_help() {
    echo "Pet Directory Development Helper"
    echo "================================"
    echo ""
    echo "Usage: ./dev.sh [command]"
    echo ""
    echo "Available commands:"
    echo "  up         - Start development environment"
    echo "  down       - Stop development environment"
    echo "  logs       - Show logs from all services"
    echo "  rebuild    - Rebuild and restart development environment"
    echo "  test       - Run test script to populate sample data"
    echo "  clean      - Remove all containers and volumes"
    echo "  worker     - Follow worker logs"
    echo "  api        - Follow API logs"
    echo "  db-shell   - Connect to PostgreSQL shell"
    echo "  status     - Show status of all services"
    echo "  help       - Show this help message"
    echo ""
}

# Check if docker and docker compose are installed
check_requirements() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed!"
        exit 1
    fi
    
    if ! docker compose version &> /dev/null 2>&1 && ! docker-compose version &> /dev/null 2>&1; then
        print_error "Docker Compose is not installed!"
        exit 1
    fi
}

# Determine docker compose command
get_compose_command() {
    if docker compose version &> /dev/null 2>&1; then
        echo "docker compose"
    else
        echo "docker-compose"
    fi
}

# Start development environment
start_dev() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "🚀 Starting development environment..."
    $COMPOSE_CMD -f docker-compose.development.yml up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        print_info "✅ Development environment started!"
        echo ""
        echo "   📡 API: http://localhost:8000"
        echo "   📚 Docs: http://localhost:8000/docs"
        echo "   🗄️ Adminer: http://localhost:8080"
        echo ""
        print_warning "Run './dev.sh test' to populate with sample data"
    else
        print_error "Failed to start development environment"
        exit 1
    fi
}

# Stop development environment
stop_dev() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "🛑 Stopping development environment..."
    $COMPOSE_CMD -f docker-compose.development.yml down
    print_info "✅ Development environment stopped"
}

# Show logs
show_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "📋 Showing logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f
}

# Rebuild environment
rebuild_dev() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "🔨 Rebuilding development environment..."
    $COMPOSE_CMD -f docker-compose.development.yml down
    $COMPOSE_CMD -f docker-compose.development.yml build --no-cache
    $COMPOSE_CMD -f docker-compose.development.yml up -d
    print_info "✅ Development environment rebuilt and started"
}

# Run tests
run_tests() {
    if [ ! -f "./test_api.sh" ]; then
        print_error "Test script not found!"
        exit 1
    fi
    ./test_api.sh
}

# Clean everything
clean_all() {
    COMPOSE_CMD=$(get_compose_command)
    print_warning "⚠️  This will remove all containers and volumes!"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm == [yY] ]]; then
        print_info "🧹 Cleaning all containers and volumes..."
        $COMPOSE_CMD -f docker-compose.development.yml down -v
        $COMPOSE_CMD down -v 2>/dev/null
        print_info "✅ Cleaned all containers and volumes"
    else
        print_info "Cancelled"
    fi
}

# Show worker logs
worker_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "📊 Worker logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f worker
}

# Show API logs
api_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "🌐 API logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f api
}

# Connect to database
db_shell() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "🗄️  Connecting to PostgreSQL..."
    $COMPOSE_CMD -f docker-compose.development.yml exec db psql -U pets_user -d pets_db
}

# Show status
show_status() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "📊 Service Status:"
    echo ""
    $COMPOSE_CMD -f docker-compose.development.yml ps
}

# Main script logic
check_requirements

case "$1" in
    up)
        start_dev
        ;;
    down)
        stop_dev
        ;;
    logs)
        show_logs
        ;;
    rebuild)
        rebuild_dev
        ;;
    test)
        run_tests
        ;;
    clean)
        clean_all
        ;;
    worker)
        worker_logs
        ;;
    api)
        api_logs
        ;;
    db-shell)
        db_shell
        ;;
    status)
        show_status
        ;;
    help|"")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac