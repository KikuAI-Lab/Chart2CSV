#!/bin/bash
# Deploy Chart2CSV API to Hetzner server
# Usage: ./deploy.sh

set -e

SERVER="root@65.109.141.228"
DEPLOY_DIR="/opt/chart2csv"

echo "🚀 Deploying Chart2CSV API..."

# Create deploy directory on server
ssh $SERVER "mkdir -p $DEPLOY_DIR"

# Sync files
rsync -avz --exclude 'venv*' --exclude '.git' --exclude '__pycache__' \
    --exclude '*.pyc' --exclude 'fixtures' --exclude 'docs' \
    ./ $SERVER:$DEPLOY_DIR/

# Copy nginx config
scp deploy/nginx.conf $SERVER:/etc/nginx/sites-available/chart2csv.kikuai.dev

# SSH into server and run deployment
ssh $SERVER << 'ENDSSH'
cd /opt/chart2csv

# Enable nginx site
ln -sf /etc/nginx/sites-available/chart2csv.kikuai.dev /etc/nginx/sites-enabled/

# Get SSL certificate if not exists
if [ ! -f /etc/letsencrypt/live/chart2csv.kikuai.dev/fullchain.pem ]; then
    certbot certonly --webroot -w /var/www/certbot -d chart2csv.kikuai.dev --non-interactive --agree-tos -m admin@kikuai.dev
fi

# Build and start Docker container
docker-compose down 2>/dev/null || true
docker-compose build
docker-compose up -d

# Reload nginx
nginx -t && systemctl reload nginx

echo "✅ Deployment complete!"
echo "API available at: https://chart2csv.kikuai.dev"
ENDSSH
