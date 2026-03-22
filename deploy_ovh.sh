#!/bin/bash
# ============================================
# RE'ACTIF PRO - Script de déploiement OVH
# ============================================
set -e

echo "===== 1/7 - Mise à jour du système ====="
sudo apt update && sudo apt upgrade -y

echo "===== 2/7 - Installation Python, Node, Nginx, Git ====="
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx certbot python3-certbot-nginx git

echo "===== 3/7 - Cloner le projet ====="
cd /home/ubuntu
if [ -d "reactif-pro" ]; then
  cd reactif-pro && git pull
else
  echo "IMPORTANT: Remplacez l'URL ci-dessous par votre repo GitHub"
  echo "Exemple: git clone https://github.com/VOTRE_USER/VOTRE_REPO.git reactif-pro"
  echo ""
  read -p "Collez l'URL de votre repo GitHub: " REPO_URL
  git clone "$REPO_URL" reactif-pro
fi
cd /home/ubuntu/reactif-pro

echo "===== 4/7 - Configuration Backend ====="
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "--- Configuration des variables d'environnement ---"
echo "Vous aurez besoin de:"
echo "  1. Votre MONGO_URL (MongoDB Atlas)"
echo "  2. Votre EMERGENT_LLM_KEY"
echo ""

if [ ! -f .env ]; then
  read -p "Collez votre MONGO_URL: " MONGO_URL_INPUT
  read -p "Collez votre EMERGENT_LLM_KEY: " LLM_KEY_INPUT
  cat > .env << ENVEOF
MONGO_URL=${MONGO_URL_INPUT}
DB_NAME=reactif_pro
EMERGENT_LLM_KEY=${LLM_KEY_INPUT}
CORS_ORIGINS=https://reactif.pro,https://www.reactif.pro
ENVEOF
  echo "Fichier .env créé !"
else
  echo "Fichier .env existe déjà, pas de modification."
fi
deactivate

echo "===== 5/7 - Build Frontend ====="
cd /home/ubuntu/reactif-pro/frontend
npm install
REACT_APP_BACKEND_URL="" npm run build
echo "Frontend build terminé !"

echo "===== 6/7 - Configuration Nginx ====="
sudo tee /etc/nginx/sites-available/reactif.pro > /dev/null << 'NGINXEOF'
server {
    listen 80;
    server_name reactif.pro www.reactif.pro;

    # Frontend (React build servi par Nginx)
    location / {
        root /home/ubuntu/reactif-pro/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API (proxy vers FastAPI)
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 30s;
        client_max_body_size 20M;
    }
}
NGINXEOF

sudo ln -sf /etc/nginx/sites-available/reactif.pro /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx
echo "Nginx configuré !"

echo "===== 7/7 - Service Backend (systemd) ====="
sudo tee /etc/systemd/system/reactif-backend.service > /dev/null << 'SVCEOF'
[Unit]
Description=Re'Actif Pro Backend
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/reactif-pro/backend
ExecStart=/home/ubuntu/reactif-pro/backend/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=5
Environment=PATH=/home/ubuntu/reactif-pro/backend/venv/bin:/usr/bin

[Install]
WantedBy=multi-user.target
SVCEOF

sudo systemctl daemon-reload
sudo systemctl enable reactif-backend
sudo systemctl start reactif-backend
echo "Backend lancé en service !"

echo ""
echo "============================================"
echo "  DEPLOIEMENT TERMINE !"
echo "============================================"
echo ""
echo "Prochaines étapes :"
echo "  1. Allez sur OVH Manager > Noms de domaine > reactif.pro > Zone DNS"
echo "  2. Modifiez l'entrée A pour pointer vers : 51.91.124.85"
echo "  3. Puis lancez : sudo certbot --nginx -d reactif.pro -d www.reactif.pro"
echo ""
echo "Testez : http://51.91.124.85 (devrait afficher le site)"
echo "Status backend : sudo systemctl status reactif-backend"
echo "Logs backend : sudo journalctl -u reactif-backend -f"
echo ""
