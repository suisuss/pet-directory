#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC}  $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_step() {
    echo -e "${BLUE}▶${NC} $1"
}

print_success() {
    echo -e "${GREEN}${BOLD}✨ $1${NC}"
}

# Function to show help
show_help() {
    echo -e "${BOLD}Pet Directory Development Helper${NC}"
    echo "================================"
    echo ""
    echo -e "${BOLD}Usage:${NC} ./dev.sh [command] [options]"
    echo ""
    echo -e "${BOLD}Docker Commands:${NC}"
    echo -e "  ${CYAN}up${NC}         - Start development environment"
    echo -e "  ${CYAN}down${NC}       - Stop development environment"
    echo -e "  ${CYAN}restart${NC}    - Restart all services"
    echo -e "  ${CYAN}rebuild${NC}    - Rebuild and restart development environment"
    echo -e "  ${CYAN}status${NC}     - Show status of all services"
    echo -e "  ${CYAN}clean${NC}      - Remove all containers and volumes"
    echo ""
    echo -e "${BOLD}Service Commands:${NC}"
    echo -e "  ${CYAN}logs${NC}       - Show logs from all services"
    echo -e "  ${CYAN}api${NC}        - Follow API logs"
    echo -e "  ${CYAN}worker${NC}     - Follow worker logs"
    echo -e "  ${CYAN}db${NC}         - Follow database logs"
    echo ""
    echo -e "${BOLD}Database Commands:${NC}"
    echo -e "  ${CYAN}db-shell${NC}   - Connect to PostgreSQL shell"
    echo -e "  ${CYAN}db-backup${NC}  - Create database backup"
    echo -e "  ${CYAN}db-restore${NC} - Restore database from backup"
    echo -e "  ${CYAN}migrate${NC}    - Run database migrations"
    echo -e "  ${CYAN}rollback${NC}   - Rollback last migration"
    echo ""
    echo -e "${BOLD}Development Commands:${NC}"
    echo -e "  ${CYAN}test${NC}       - Run test script to populate sample data"
    echo -e "  ${CYAN}format${NC}     - Format Python code with black and ruff"
    echo -e "  ${CYAN}lint${NC}       - Run linting checks"
    echo -e "  ${CYAN}typecheck${NC}  - Run type checking with mypy"
    echo -e "  ${CYAN}quality${NC}    - Run all code quality checks"
    echo ""
    echo -e "${BOLD}Utility Commands:${NC}"
    echo -e "  ${CYAN}shell${NC}      - Enter API container shell"
    echo -e "  ${CYAN}exec${NC}       - Execute command in API container"
    echo -e "  ${CYAN}ps${NC}         - Show running processes"
    echo -e "  ${CYAN}stats${NC}      - Show container resource usage"
    echo -e "  ${CYAN}help${NC}       - Show this help message"
    echo ""
    echo -e "${BOLD}Examples:${NC}"
    echo "  ./dev.sh up              # Start development environment"
    echo "  ./dev.sh test            # Run API tests"
    echo "  ./dev.sh exec bash       # Enter container shell"
    echo "  ./dev.sh db-backup       # Backup database"
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
    print_step "Starting development environment..."
    $COMPOSE_CMD -f docker-compose.development.yml up -d
    
    if [ $? -eq 0 ]; then
        echo ""
        print_success "Development environment started!"
        echo ""
        echo -e "   ${CYAN}API:${NC}     http://localhost:8000"
        echo -e "   ${CYAN}Docs:${NC}    http://localhost:8000/docs"
        echo -e "   ${CYAN}Adminer:${NC} http://localhost:8080"
        echo ""
        print_info "Run './dev.sh test' to populate with sample data"
    else
        print_error "Failed to start development environment"
        exit 1
    fi
}

# Stop development environment
stop_dev() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Stopping development environment..."
    $COMPOSE_CMD -f docker-compose.development.yml down
    print_success "Development environment stopped"
}

# Show logs
show_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Showing logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f
}

# Rebuild environment
rebuild_dev() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Rebuilding development environment..."
    $COMPOSE_CMD -f docker-compose.development.yml down
    print_step "Building containers..."
    $COMPOSE_CMD -f docker-compose.development.yml build --no-cache
    print_step "Starting services..."
    $COMPOSE_CMD -f docker-compose.development.yml up -d
    print_success "Development environment rebuilt and started"
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
    print_warning "This will remove all containers and volumes!"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm == [yY] ]]; then
        print_step "Cleaning all containers and volumes..."
        $COMPOSE_CMD -f docker-compose.development.yml down -v
        $COMPOSE_CMD down -v 2>/dev/null
        docker system prune -f 2>/dev/null
        print_success "Cleaned all containers and volumes"
    else
        print_info "Cancelled"
    fi
}

# Show worker logs
worker_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Worker logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f worker
}

# Show API logs
api_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "API logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f api
}

# Connect to database
db_shell() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Connecting to PostgreSQL..."
    $COMPOSE_CMD -f docker-compose.development.yml exec db psql -U pets_user -d pets_db
}

# Show status
show_status() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Service Status:"
    echo ""
    $COMPOSE_CMD -f docker-compose.development.yml ps
}

# Restart services
restart_services() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Restarting all services..."
    $COMPOSE_CMD -f docker-compose.development.yml restart
    print_success "Services restarted"
}

# Show database logs
db_logs() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Database logs (Ctrl+C to exit)..."
    $COMPOSE_CMD -f docker-compose.development.yml logs -f db
}

# Database backup
db_backup() {
    COMPOSE_CMD=$(get_compose_command)
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="backup_${TIMESTAMP}.sql"
    
    print_step "Creating database backup: $BACKUP_FILE"
    $COMPOSE_CMD -f docker-compose.development.yml exec -T db pg_dump -U pets_user pets_db > "$BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Backup created: $BACKUP_FILE"
        print_info "Size: $(du -h $BACKUP_FILE | cut -f1)"
    else
        print_error "Backup failed"
        exit 1
    fi
}

# Database restore
db_restore() {
    if [ -z "$1" ]; then
        print_error "Please provide a backup file"
        echo "Usage: ./dev.sh db-restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$1" ]; then
        print_error "Backup file not found: $1"
        exit 1
    fi
    
    COMPOSE_CMD=$(get_compose_command)
    print_warning "This will replace all data in the database!"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm == [yY] ]]; then
        print_step "Restoring database from: $1"
        $COMPOSE_CMD -f docker-compose.development.yml exec -T db psql -U pets_user pets_db < "$1"
        
        if [ $? -eq 0 ]; then
            print_success "Database restored successfully"
        else
            print_error "Restore failed"
            exit 1
        fi
    else
        print_info "Restore cancelled"
    fi
}

# Run migrations
run_migrations() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Running database migrations..."
    $COMPOSE_CMD -f docker-compose.development.yml exec api alembic upgrade head
    
    if [ $? -eq 0 ]; then
        print_success "Migrations completed"
    else
        print_error "Migration failed"
        exit 1
    fi
}

# Rollback migration
rollback_migration() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Rolling back last migration..."
    $COMPOSE_CMD -f docker-compose.development.yml exec api alembic downgrade -1
    
    if [ $? -eq 0 ]; then
        print_success "Rollback completed"
    else
        print_error "Rollback failed"
        exit 1
    fi
}

# Enter container shell
enter_shell() {
    COMPOSE_CMD=$(get_compose_command)
    SERVICE="${1:-api}"
    print_info "Entering $SERVICE container shell..."
    $COMPOSE_CMD -f docker-compose.development.yml exec $SERVICE /bin/bash
}

# Execute command in container
exec_in_container() {
    if [ $# -eq 0 ]; then
        print_error "Please provide a command to execute"
        echo "Usage: ./dev.sh exec <command>"
        exit 1
    fi
    
    COMPOSE_CMD=$(get_compose_command)
    print_step "Executing in API container: $@"
    $COMPOSE_CMD -f docker-compose.development.yml exec api $@
}

# Show container processes
show_processes() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Container processes:"
    $COMPOSE_CMD -f docker-compose.development.yml ps
    echo ""
    print_info "System processes in containers:"
    $COMPOSE_CMD -f docker-compose.development.yml exec api ps aux
}

# Show container stats
show_stats() {
    COMPOSE_CMD=$(get_compose_command)
    print_info "Container resource usage:"
    docker stats --no-stream $($COMPOSE_CMD -f docker-compose.development.yml ps -q)
}

# Format code
format_code() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Formatting Python code..."
    
    # Check if running in container
    if $COMPOSE_CMD -f docker-compose.development.yml ps | grep -q "api.*Up"; then
        print_info "Running formatters in container..."
        $COMPOSE_CMD -f docker-compose.development.yml exec api black app/
        $COMPOSE_CMD -f docker-compose.development.yml exec api ruff check --fix app/
    else
        print_warning "API container not running, trying local formatters..."
        if command -v black &> /dev/null; then
            black app/
        else
            print_error "Black not installed locally"
        fi
        if command -v ruff &> /dev/null; then
            ruff check --fix app/
        else
            print_error "Ruff not installed locally"
        fi
    fi
    print_success "Formatting complete"
}

# Run linting
run_lint() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Running linting checks..."
    
    if $COMPOSE_CMD -f docker-compose.development.yml ps | grep -q "api.*Up"; then
        $COMPOSE_CMD -f docker-compose.development.yml exec api ruff check app/
    else
        print_warning "API container not running, trying local linter..."
        if command -v ruff &> /dev/null; then
            ruff check app/
        else
            print_error "Ruff not installed locally"
            exit 1
        fi
    fi
}

# Run type checking
run_typecheck() {
    COMPOSE_CMD=$(get_compose_command)
    print_step "Running type checking..."
    
    if $COMPOSE_CMD -f docker-compose.development.yml ps | grep -q "api.*Up"; then
        $COMPOSE_CMD -f docker-compose.development.yml exec api mypy app/
    else
        print_warning "API container not running, trying local mypy..."
        if command -v mypy &> /dev/null; then
            mypy app/
        else
            print_error "Mypy not installed locally"
            exit 1
        fi
    fi
}

# Run all quality checks
run_quality() {
    print_info "Running all code quality checks..."
    format_code
    run_lint
    run_typecheck
    print_success "All quality checks complete"
}

# Main script logic
check_requirements

case "$1" in
    # Docker commands
    up)
        start_dev
        ;;
    down)
        stop_dev
        ;;
    restart)
        restart_services
        ;;
    rebuild)
        rebuild_dev
        ;;
    status)
        show_status
        ;;
    clean)
        clean_all
        ;;
    
    # Service commands
    logs)
        show_logs
        ;;
    api)
        api_logs
        ;;
    worker)
        worker_logs
        ;;
    db)
        db_logs
        ;;
    
    # Database commands
    db-shell)
        db_shell
        ;;
    db-backup)
        db_backup
        ;;
    db-restore)
        db_restore "$2"
        ;;
    migrate)
        run_migrations
        ;;
    rollback)
        rollback_migration
        ;;
    
    # Development commands
    test)
        run_tests
        ;;
    format)
        format_code
        ;;
    lint)
        run_lint
        ;;
    typecheck)
        run_typecheck
        ;;
    quality)
        run_quality
        ;;
    
    # Utility commands
    shell)
        enter_shell "$2"
        ;;
    exec)
        shift
        exec_in_container "$@"
        ;;
    ps)
        show_processes
        ;;
    stats)
        show_stats
        ;;
    
    # Help
    help|"")
        show_help
        ;;
    
    # Unknown command
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac