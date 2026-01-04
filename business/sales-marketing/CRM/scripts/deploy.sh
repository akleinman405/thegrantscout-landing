#!/bin/bash
# Deploy TGS CRM to Cloudflare Pages

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
FRONTEND_DIR="$PROJECT_DIR/frontend"

echo "Deploying TGS CRM..."
echo "Frontend directory: $FRONTEND_DIR"

# Check if wrangler is installed
if ! command -v wrangler &> /dev/null; then
    echo "Error: wrangler CLI not found"
    echo "Install with: npm install -g wrangler"
    exit 1
fi

# Check if logged in
if ! wrangler whoami &> /dev/null; then
    echo "Please login to Cloudflare first:"
    echo "  wrangler login"
    exit 1
fi

# Deploy
echo ""
echo "Deploying to Cloudflare Pages..."
wrangler pages deploy "$FRONTEND_DIR" --project-name tgs-crm

echo ""
echo "Deployment complete!"
echo "Your CRM is available at: https://tgs-crm.pages.dev"
