# WebADB Android

Aplikasi web sederhana untuk mengelola ADB melalui browser (Flask).

## Fitur
- Aktifkan ADB Wi-Fi
- Cek IP HP
- Reset ADB Server
- Cek Status ADB
- Nonaktifkan ADB Wi-Fi
- Aktifkan ADB USB

## Instalasi (Linux)

1. **Clone repo ini:**
   ```bash
   git clone <repo-url>
   cd Web\ Adb\ Android
   ```
2. **Jalankan script instalasi:**
   ```bash
   chmod +x install_webadb.sh
   ./install_webadb.sh
   ```
3. **Akses aplikasi:**
   Buka browser ke `http://<ip-server>:5000`

## Catatan
- Pastikan `adb` sudah terinstall di server.
- Script ini menggunakan `venv` untuk isolasi environment Python.
- Service otomatis berjalan saat server restart (systemd).
- Untuk keamanan, sebaiknya batasi akses web ini hanya dari jaringan lokal.
- Jika ingin uninstall: 
   ```bash
   sudo systemctl stop webadb
   sudo systemctl disable webadb
   sudo rm /etc/systemd/system/webadb.service
   sudo systemctl daemon-reload
   ```

## Kontribusi
Pull request dan issue sangat diterima! 