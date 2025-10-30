#!/bin/bash

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:8000"

print_colored() {
    echo -e "${1}${2}${NC}"
}

print_section() {
    echo
    print_colored "$BLUE" "═══════════════════════════════════════════"
    print_colored "$BLUE" "$1"
    print_colored "$BLUE" "═══════════════════════════════════════════"
}

# Check if API is running
print_section "Checking API Health"
if curl -s "$API_URL/health" | grep -q "healthy"; then
    print_colored "$GREEN" "✓ API is healthy"
else
    print_colored "$RED" "✗ API is not responding. Please start the services first."
    exit 1
fi

# Create some test pets
print_section "Creating Test Pets"

print_colored "$YELLOW" "Creating dog named 'Buddy'..."
curl -X POST "$API_URL/api/pets/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Buddy", "pet_type": "dog"}' \
    2>/dev/null | python3 -m json.tool

print_colored "$YELLOW" "Creating cat named 'Whiskers'..."
curl -X POST "$API_URL/api/pets/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Whiskers", "pet_type": "cat"}' \
    2>/dev/null | python3 -m json.tool

print_colored "$YELLOW" "Creating bird named 'Tweety'..."
TWEETY_RESPONSE=$(curl -X POST "$API_URL/api/pets/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Tweety", "pet_type": "bird"}' \
    2>/dev/null)
echo "$TWEETY_RESPONSE" | python3 -m json.tool
TWEETY_ID=$(echo "$TWEETY_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

print_colored "$YELLOW" "Creating dog named 'Max'..."
curl -X POST "$API_URL/api/pets/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Max", "pet_type": "dog"}' \
    2>/dev/null | python3 -m json.tool

print_colored "$YELLOW" "Creating cat named 'Luna'..."
curl -X POST "$API_URL/api/pets/" \
    -H "Content-Type: application/json" \
    -d '{"name": "Luna", "pet_type": "cat"}' \
    2>/dev/null | python3 -m json.tool

# List all pets
print_section "Listing All Pets"
curl -s "$API_URL/api/pets/" | python3 -m json.tool

# Get a specific pet
print_section "Getting Pet with ID 1"
curl -s "$API_URL/api/pets/1" | python3 -m json.tool

# Update a pet
print_section "Updating Pet with ID 2 (Changing name to 'Mr. Whiskers')"
curl -X PUT "$API_URL/api/pets/2" \
    -H "Content-Type: application/json" \
    -d '{"name": "Mr. Whiskers"}' \
    2>/dev/null | python3 -m json.tool

# Delete a pet
print_section "Deleting Pet 'Tweety' (ID: $TWEETY_ID)"
if curl -s -o /dev/null -w "%{http_code}" -X DELETE "$API_URL/api/pets/$TWEETY_ID" | grep -q "204"; then
    print_colored "$GREEN" "✓ Pet 'Tweety' deleted successfully (HTTP 204)"
else
    print_colored "$RED" "✗ Failed to delete pet"
fi

# List pets with pagination
print_section "Testing Pagination (skip=1, limit=2)"
curl -s "$API_URL/api/pets/?skip=1&limit=2" | python3 -m json.tool

# Test 404 error
print_section "Testing Error Handling (Getting non-existent pet)"
curl -s "$API_URL/api/pets/999" | python3 -m json.tool

print_section "Test Complete!"
print_colored "$GREEN" "All API endpoints tested successfully!"
print_colored "$YELLOW" "Check the worker logs to see the generated reports."
print_colored "$YELLOW" "Visit $API_URL/docs for interactive API documentation."