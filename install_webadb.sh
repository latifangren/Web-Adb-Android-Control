#!/bin/bash

# 1. Buat venv
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Pastikan adb terinstall
if ! command -v adb &> /dev/null
then
    echo "adb tidak ditemukan, silakan install adb terlebih dahulu."
    exit 1
fi

# 4. Permission (jika perlu, misal akses /tmp)
sudo chmod 777 /tmp

# 5. Buat systemd service
SERVICE_FILE=/etc/systemd/system/webadb.service
sudo bash -c "cat > $SERVICE_FILE" <<EOL
[Unit]
Description=Web ADB Flask Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(pwd)/venv/bin/python $(pwd)/webadb.py
Restart=always

[Install]
WantedBy=multi-user.target
EOL

# 6. Reload systemd dan enable service
sudo systemctl daemon-reload
sudo systemctl enable webadb
sudo systemctl start webadb

echo "WebADB sudah berjalan di port 5000" 