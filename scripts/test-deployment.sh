#!/bin/bash

# MirrorMind Deployment Test Script
# Tests if backend and frontend are properly deployed

echo "🧪 Testing MirrorMind Deployment..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get URLs from user
read -p "Enter your backend URL (e.g., https://mirrormind-backend.onrender.com): " BACKEND_URL
read -p "Enter your frontend URL (e.g., https://mirrormind.vercel.app): " FRONTEND_URL

echo ""
echo "Testing backend at: $BACKEND_URL"
echo "Testing frontend at: $FRONTEND_URL"
echo ""

# Test 1: Backend Health Check
echo "1️⃣  Testing backend health check..."
HEALTH_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/")
if [ "$HEALTH_RESPONSE" -eq 200 ]; then
    echo -e "${GREEN}✓ Backend is responding${NC}"
else
    echo -e "${RED}✗ Backend health check failed (HTTP $HEALTH_RESPONSE)${NC}"
fi

# Test 2: Backend API Endpoints
echo "2️⃣  Testing backend API endpoints..."
AGENTS_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/agents")
if [ "$AGENTS_RESPONSE" -eq 200 ]; then
    echo -e "${GREEN}✓ Agents API is working${NC}"
else
    echo -e "${RED}✗ Agents API failed (HTTP $AGENTS_RESPONSE)${NC}"
fi

# Test 3: Frontend Accessibility
echo "3️⃣  Testing frontend accessibility..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$FRONTEND_URL")
if [ "$FRONTEND_RESPONSE" -eq 200 ]; then
    echo -e "${GREEN}✓ Frontend is accessible${NC}"
else
    echo -e "${RED}✗ Frontend failed (HTTP $FRONTEND_RESPONSE)${NC}"
fi

# Test 4: CORS Check
echo "4️⃣  Testing CORS configuration..."
CORS_RESPONSE=$(curl -s -H "Origin: $FRONTEND_URL" -H "Access-Control-Request-Method: POST" -X OPTIONS "$BACKEND_URL/api/agents" -o /dev/null -w "%{http_code}")
if [ "$CORS_RESPONSE" -eq 200 ] || [ "$CORS_RESPONSE" -eq 204 ]; then
    echo -e "${GREEN}✓ CORS is configured correctly${NC}"
else
    echo -e "${YELLOW}⚠ CORS might need configuration (HTTP $CORS_RESPONSE)${NC}"
fi

echo ""
echo "🎉 Deployment test complete!"
echo ""
echo "Next steps:"
echo "1. Visit $FRONTEND_URL in your browser"
echo "2. Try creating a debate"
echo "3. Test the agent builder"
echo ""
