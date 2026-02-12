#!/usr/bin/env bash
set -euo pipefail

# MovieBrain deployment script for a fresh VPS (Ubuntu/Debian)
# Usage: bash deploy.sh

REPO_DIR="/opt/moviebrain"

echo "=== MovieBrain Deployment ==="

# 1. Install Docker if not present
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable --now docker
fi

# 2. Install docker compose plugin if not present
if ! docker compose version &> /dev/null; then
    echo "Installing Docker Compose plugin..."
    apt-get update && apt-get install -y docker-compose-plugin
fi

# 3. Clone or pull repo
if [ -d "$REPO_DIR" ]; then
    echo "Updating existing repo..."
    cd "$REPO_DIR"
    git pull
else
    echo "Cloning repo..."
    git clone https://github.com/YOUR_USERNAME/MovieBrain.git "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 4. Create .env if missing
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo "*** IMPORTANT: Edit .env with your actual values before continuing ***"
    echo "    nano $REPO_DIR/.env"
    echo ""
    exit 1
fi

# Load domain from .env
source .env
DOMAIN="${DOMAIN:?DOMAIN must be set in .env}"

# 5. Get initial SSL certificate (if not already present)
if [ ! -d "/etc/letsencrypt/live/$DOMAIN" ]; then
    echo "Obtaining SSL certificate for $DOMAIN..."
    apt-get install -y certbot
    certbot certonly --standalone -d "$DOMAIN" --non-interactive --agree-tos -m "admin@$DOMAIN"

    # Copy certs to Docker volume location
    docker volume create moviebrain_certbot-conf 2>/dev/null || true
fi

# 6. Substitute domain in nginx config
envsubst '${DOMAIN}' < nginx/nginx.conf > nginx/nginx.conf.tmp
mv nginx/nginx.conf.tmp nginx/nginx.conf

# 7. Build and start services
echo "Building and starting services..."
docker compose -f docker-compose.yml -f docker-compose.prod.yml up --build -d

# 8. Wait for DB to be healthy
echo "Waiting for database..."
sleep 5

# 9. Run migrations
echo "Running database migrations..."
docker compose exec backend python -m alembic upgrade head

echo ""
echo "=== Deployment complete! ==="
echo "Visit https://$DOMAIN to access MovieBrain"
echo ""
echo "To restore a database dump:"
echo "  docker compose exec -T db pg_restore -U postgres -d moviebrain < moviebrain.dump"
