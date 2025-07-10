# WebADB Android

Aplikasi web ringan berbasis Flask untuk mengelola ADB (Android Debug Bridge) melalui browser. Cocok untuk server Linux/Ubuntu, memungkinkan kontrol perangkat Android yang terhubung via USB atau WiFi.

## Fitur

- **Aktifkan ADB Wi-Fi:** Mengaktifkan mode ADB melalui jaringan WiFi.
- **Cek IP HP:** Menampilkan alamat IP perangkat Android.
- **Reset ADB Server:** Merestart service ADB di server.
- **Cek Status ADB:** Menampilkan daftar perangkat yang terhubung.
- **Nonaktifkan ADB Wi-Fi:** Mengembalikan mode ADB ke USB.
- **Aktifkan ADB USB:** Memastikan mode ADB USB aktif.
- **Info Device Lengkap:** Menampilkan info model, brand, versi Android, status root, baterai, IP, status koneksi USB/WiFi.
- **Log Aktivitas:** Semua aksi terekam dan bisa dilihat/di-clear dari web.
- **Restart & Status WebADB:** Kontrol service WebADB langsung dari web.
- **Dark Mode:** Tampilan gelap yang nyaman di mata.

## Instalasi

### Prasyarat

- Python 3.x
- `adb` sudah terinstall di server
- Linux/Ubuntu (direkomendasikan)

### Langkah Instalasi

1. **Clone repo ini:**
   ```bash
   git clone https://github.com/latifangren/Web-Adb-Android-Control.git
   cd Web-Adb-Android-Control
   ```

2. **Jalankan script instalasi:**
   ```bash
   chmod +x install_webadb.sh
   ./install_webadb.sh
   ```

3. **Akses aplikasi:**
   Buka browser ke `http://<ip-server>:5000`

### Uninstall

```bash
sudo systemctl stop webadb
sudo systemctl disable webadb
sudo rm /etc/systemd/system/webadb.service
sudo systemctl daemon-reload
```

## Catatan

- Script menggunakan `venv` untuk isolasi environment Python.
- Service otomatis berjalan saat server restart (systemd).
- Untuk keamanan, batasi akses web ini hanya dari jaringan lokal.
- Log aktivitas tersimpan di file `adb_web_log.txt`.

## Kontribusi

Pull request dan issue sangat diterima!

## Lisensi

GPL-3.0 License 