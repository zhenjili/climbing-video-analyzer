#!/bin/bash
set -e

# Climbing Video Analyzer - Oracle Cloud VM Deployment Script
# Usage: ./deploy.sh <your-domain>

DOMAIN=${1:?Usage: ./deploy.sh your-domain.com}

echo "=== Deploying Climbing Video Analyzer ==="
echo "Domain: $DOMAIN"

# 1. Update nginx.conf with actual domain
sed -i "s/YOUR_DOMAIN/$DOMAIN/g" nginx.conf

# 2. Update .env.prod (remind user)
if grep -q "your-api-key-here" backend/.env.prod; then
    echo ""
    echo "ERROR: Please edit backend/.env.prod first:"
    echo "  - Set ANTHROPIC_API_KEY"
    echo "  - Set CORS_ORIGINS to your Vercel frontend URL"
    echo ""
    exit 1
fi

# 3. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker $USER
    echo "Docker installed. Please log out and back in, then re-run this script."
    exit 0
fi

# 4. Get SSL certificate (first time only)
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "Obtaining SSL certificate..."
    # Start nginx temporarily on port 80 for ACME challenge
    docker compose -f docker-compose.prod.yml up -d nginx
    docker compose -f docker-compose.prod.yml run --rm certbot \
        certbot certonly --webroot -w /var/www/certbot \
        --email admin@$DOMAIN --agree-tos --no-eff-email \
        -d $DOMAIN
    docker compose -f docker-compose.prod.yml down
fi

# 5. Build and start all services
echo "Building and starting services..."
docker compose -f docker-compose.prod.yml up -d --build

echo ""
echo "=== Deployment complete ==="
echo "Backend API: https://$DOMAIN/api/health"
echo ""
echo "Next steps:"
echo "  1. Set NEXT_PUBLIC_API_URL=https://$DOMAIN/api in Vercel environment variables"
echo "  2. Deploy frontend to Vercel: cd frontend && vercel --prod"
