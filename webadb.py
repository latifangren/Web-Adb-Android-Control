from flask import Flask, render_template_string, redirect, url_for, send_file, request
import subprocess
import re
import os

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang='id'>
<head>
  <meta charset='UTF-8'>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <title>ADB Wi-Fi Bridge</title>
  <link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css' rel='stylesheet'>
  <link rel='stylesheet' href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'>
  <style>
    body.dark-mode { background: #181a1b; color: #eee; }
    .card { margin-bottom: 1rem; }
    .spinner-border { display: none; }
    .toast-container { position: fixed; top: 1rem; right: 1rem; z-index: 9999; }
    pre { background: #111; color: #0f0; padding: 10px; border-radius: 5px; }
  </style>
</head>
<body>
<div class='container py-4'>
  <div class='d-flex justify-content-between align-items-center mb-3'>
    <h2><i class='fa-solid fa-wifi'></i> ADB Wi-Fi Bridge</h2>
    <button class='btn btn-dark' id='toggle-dark'><i class='fa-solid fa-moon'></i> Dark Mode</button>
  </div>
  <div class='row'>
    <div class='col-md-6'>
      <div class='card'>
        <div class='card-body'>
          <form action='/tcpip' method='post' class='d-inline'>
            <button class='btn btn-success mb-1'><i class='fa-solid fa-wifi'></i> Aktifkan ADB Wi-Fi</button>
          </form>
          <form action='/ip' method='post' class='d-inline'>
            <button class='btn btn-info mb-1'><i class='fa-solid fa-globe'></i> Cek IP HP</button>
          </form>
          <form action='/reset' method='post' class='d-inline'>
            <button class='btn btn-warning mb-1'><i class='fa-solid fa-rotate'></i> Reset ADB Server</button>
          </form>
          <form action='/status' method='post' class='d-inline'>
            <button class='btn btn-primary mb-1'><i class='fa-solid fa-microchip'></i> Cek Status ADB</button>
          </form>
          <form action='/disable-wifi' method='post' class='d-inline'>
            <button class='btn btn-danger mb-1'><i class='fa-solid fa-ban'></i> Nonaktifkan ADB Wi-Fi</button>
          </form>
          <form action='/enable-usb' method='post' class='d-inline'>
            <button class='btn btn-secondary mb-1'><i class='fa-solid fa-usb'></i> Aktifkan ADB USB</button>
          </form>
          <!-- Tombol Hotspot -->
          <form action='/hotspot-on' method='post' class='d-inline'>
            <button class='btn btn-outline-success mb-1'><i class='fa-solid fa-broadcast-tower'></i> Aktifkan Hotspot</button>
          </form>
          <form action='/hotspot-off' method='post' class='d-inline'>
            <button class='btn btn-outline-warning mb-1'><i class='fa-solid fa-broadcast-tower'></i> Nonaktifkan Hotspot</button>
          </form>
          <button class='btn btn-outline-danger mb-1' id='btn-restart-webadb'><i class='fa-solid fa-arrows-rotate'></i> Restart WebADB</button>
          <button class='btn btn-outline-info mb-1' id='btn-status-webadb'><i class='fa-solid fa-circle-info'></i> Status WebADB</button>
        </div>
      </div>
      <div class='card'>
        <div class='card-body'>
          <h5 class='card-title'><i class='fa-solid fa-terminal'></i> Output</h5>
          <div class='spinner-border text-success' id='spinner' role='status'>
            <span class='visually-hidden'>Loading...</span>
          </div>
          <pre id='output'>{{output}}</pre>
        </div>
      </div>
    </div>
    <div class='col-md-6'>
      <div class='card'>
        <div class='card-body'>
          <h5 class='card-title'><i class='fa-solid fa-info-circle'></i> Info Device
            <button class='btn btn-sm btn-outline-info float-end' id='refresh-device-info' title='Refresh'><i class='fa-solid fa-rotate'></i></button>
          </h5>
          <div id='device-info-panel'>
            <div class='text-center'><div class='spinner-border text-info'></div> Memuat info device...</div>
          </div>
        </div>
      </div>
    </div>
  </div>
  <div class='row'>
    <div class='col-12'>
      <div class='card'>
        <div class='card-body'>
          <h5 class='card-title'><i class='fa-solid fa-list'></i> Log Aktivitas
            <button class='btn btn-sm btn-outline-info' id='refresh-log' title='Refresh'><i class='fa-solid fa-rotate'></i></button>
            <button class='btn btn-sm btn-outline-danger' id='clear-log' title='Clear'><i class='fa-solid fa-trash'></i></button>
          </h5>
          <div id='log-panel'><div class='text-center'><div class='spinner-border text-info'></div> Memuat log...</div></div>
        </div>
      </div>
    </div>
  </div>
  <div class='toast-container' id='toast-container'></div>
</div>
<script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js'></script>
<script>
// Dark mode toggle
const btn = document.getElementById('toggle-dark');
btn.onclick = () => {
  document.body.classList.toggle('dark-mode');
  btn.classList.toggle('btn-light');
  btn.classList.toggle('btn-dark');
};
// Spinner (dummy, bisa diaktifkan via JS fetch di masa depan)
// Toast notification
function showToast(msg, type='success') {
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-bg-${type} border-0 show mb-2`;
  toast.role = 'alert';
  toast.innerHTML = `<div class='d-flex'><div class='toast-body'>${msg}</div><button type='button' class='btn-close btn-close-white me-2 m-auto' data-bs-dismiss='toast'></button></div>`;
  document.getElementById('toast-container').appendChild(toast);
  setTimeout(() => toast.remove(), 4000);
}
// Auto-load info device
function loadDeviceInfo() {
  const panel = document.getElementById('device-info-panel');
  panel.innerHTML = "<div class='text-center'><div class='spinner-border text-info'></div> Memuat info device...</div>";
  fetch('/device-info').then(r => r.text()).then(html => {
    panel.innerHTML = html;
  });
}
window.onload = function() {
  loadDeviceInfo();
  loadLog();
};
document.addEventListener('DOMContentLoaded', function() {
  const btn = document.getElementById('refresh-device-info');
  if (btn) btn.onclick = loadDeviceInfo;
  const logBtn = document.getElementById('refresh-log');
  if (logBtn) logBtn.onclick = loadLog;
  const clearBtn = document.getElementById('clear-log');
  if (clearBtn) clearBtn.onclick = function() {
    fetch('/clear-log', {method:'POST'}).then(() => {
      loadLog();
      showToast('Log dibersihkan', 'danger');
    });
  };
  const btnRestart = document.getElementById('btn-restart-webadb');
  if (btnRestart) btnRestart.onclick = function() {
    fetch('/restart-webadb', {method:'POST'})
      .then(r => r.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const output = doc.getElementById('output');
        if (output) document.getElementById('output').innerText = output.innerText;
      });
  };
  const btnStatus = document.getElementById('btn-status-webadb');
  if (btnStatus) btnStatus.onclick = function() {
    fetch('/status-webadb', {method:'POST'})
      .then(r => r.text())
      .then(html => {
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const output = doc.getElementById('output');
        if (output) document.getElementById('output').innerText = output.innerText;
      });
  };
});
function loadLog() {
  const panel = document.getElementById('log-panel');
  panel.innerHTML = "<div class='text-center'><div class='spinner-border text-info'></div> Memuat log...</div>";
  fetch('/log').then(r => r.text()).then(html => {
    panel.innerHTML = html;
  });
}
// JS: Populate device dropdown, handle upload/download
function populateDeviceDropdowns() {
  fetch('/device-info?json=1').then(r => r.json()).then(devices => {
    const selects = [document.getElementById('device-select-upload'), document.getElementById('device-select-download')];
    selects.forEach(sel => {
      sel.innerHTML = '';
      devices.forEach(d => {
        const opt = document.createElement('option');
        opt.value = d.id;
        opt.textContent = d.id + ' (' + d.model + ')';
        sel.appendChild(opt);
      });
    });
  });
}
// JS: Hapus semua kode terkait upload/download file
</script>
</body>
</html>
"""

LOG_FILE = "adb_web_log.txt"

def write_log(action, result):
    from datetime import datetime
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action}\n{result}\n{'-'*40}\n")

def read_log():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Balik urutan log agar terbaru di atas, pisahkan per blok log
            blocks = ''.join(lines).split('-' * 40 + '\n')
            blocks = [b.strip() for b in blocks if b.strip()]
            return ('\n' + '-' * 40 + '\n').join(blocks[::-1])
    except FileNotFoundError:
        return "Belum ada aktivitas."

def clear_log():
    open(LOG_FILE, "w").close()

@app.route("/")
def index():
    return render_template_string(HTML, output="")

@app.route("/tcpip", methods=["POST"])
def tcpip():
    subprocess.getoutput("adb wait-for-device")
    cmd = "adb shell ip route | grep wlan0 | awk '{print $NF}'"
    ip = subprocess.getoutput(cmd).strip()
    out = subprocess.getoutput("adb tcpip 5555")
    if ip:
        with open("/tmp/hp_adb_ip.txt", "w") as f:
            f.write(ip)
        result = f"ADB Wi-Fi Aktif\nIP HP: {ip}\n\n{out}"
        write_log("Aktifkan ADB Wi-Fi", result)
        return render_template_string(HTML, output=result)
    result = f"ADB Wi-Fi Aktif\nTapi Gagal Deteksi IP\n\n{out}"
    write_log("Aktifkan ADB Wi-Fi (Gagal Deteksi IP)", result)
    return render_template_string(HTML, output=result)

@app.route("/ip", methods=["POST"])
def get_ip():
    cmd = "adb shell ip route | grep wlan0 | awk '{print $NF}'"
    ip = subprocess.getoutput(cmd).strip()
    if ip:
        with open("/tmp/hp_adb_ip.txt", "w") as f:
            f.write(ip)
        result = f"IP HP: {ip}"
        write_log("Cek IP HP", result)
        return render_template_string(HTML, output=result)
    result = "Gagal mendeteksi IP HP"
    write_log("Cek IP HP (Gagal)", result)
    return render_template_string(HTML, output=result)

@app.route("/reset", methods=["POST"])
def reset():
    out = subprocess.getoutput("adb kill-server && adb start-server")
    write_log("Reset ADB Server", out)
    return render_template_string(HTML, output=out)

@app.route("/status", methods=["POST"])
def status():
    out = subprocess.getoutput("adb devices")
    write_log("Cek Status ADB", out)
    return render_template_string(HTML, output=out)

@app.route("/disable-wifi", methods=["POST"])
def disable_wifi():
    devices = get_connected_devices()
    results = []
    if not devices:
        result = "Tidak ada device terhubung."
    else:
        for dev in devices:
            # Hanya jalankan untuk device yang terhubung via WiFi (ada ':')
            if ':' in dev:
                out = subprocess.getoutput(f"adb -s {dev} usb")
                results.append(f"{dev}: {out}")
        if results:
            result = "Nonaktifkan ADB Wi-Fi → USB mode aktif\n\n" + "\n".join(results)
        else:
            result = "Tidak ada device WiFi yang perlu dinonaktifkan."
    write_log("Nonaktifkan ADB Wi-Fi", result)
    return render_template_string(HTML, output=result)

@app.route("/enable-usb", methods=["POST"])
def enable_usb():
    out = subprocess.getoutput("adb usb")
    result = f"ADB USB Mode Diaktifkan\n\n{out}"
    write_log("Aktifkan ADB USB", result)
    return render_template_string(HTML, output=result)

@app.route("/hotspot-on", methods=["POST"])
def hotspot_on():
    # Perintah ADB untuk mengaktifkan hotspot (umum, bisa berbeda tiap device)
    # Biasanya: svc wifi disable && svc wifi enable && svc tether start
    out = subprocess.getoutput("adb shell svc wifi disable && adb shell svc wifi enable && adb shell svc tether start")
    result = f"Hotspot WiFi diaktifkan.\n\n{out}"
    write_log("Aktifkan Hotspot WiFi", result)
    return render_template_string(HTML, output=result)

@app.route("/hotspot-off", methods=["POST"])
def hotspot_off():
    # Perintah ADB untuk menonaktifkan hotspot
    out = subprocess.getoutput("adb shell svc tether stop")
    result = f"Hotspot WiFi dinonaktifkan.\n\n{out}"
    write_log("Nonaktifkan Hotspot WiFi", result)
    return render_template_string(HTML, output=result)

@app.route("/restart-webadb", methods=["POST"])
def restart_webadb():
    out = subprocess.getoutput("sudo systemctl restart webadb")
    result = "WebADB service direstart.\n" + out
    write_log("Restart WebADB Service", result)
    return render_template_string(HTML, output=result)

@app.route("/status-webadb", methods=["POST"])
def status_webadb():
    out = subprocess.getoutput("sudo systemctl status webadb")
    write_log("Status WebADB Service", out)
    return render_template_string(HTML, output=out)

# Endpoint log
@app.route("/log", methods=["GET"])
def get_log():
    return f"<pre style='max-height:300px;overflow:auto'>{read_log()}</pre>"

@app.route("/clear-log", methods=["POST"])
def clear_log_route():
    clear_log()
    return "OK"

def get_connected_devices():
    out = subprocess.getoutput("adb devices")
    devices = []
    for line in out.splitlines():
        if '\tdevice' in line:
            devices.append(line.split('\t')[0])
    return devices

def get_device_connection_type(device_id):
    # Jika device_id berupa IP:PORT, berarti WiFi
    if ":" in device_id:
        return "WiFi"
    return "USB"

def get_device_info(device_id):
    def run(cmd):
        return subprocess.getoutput(f"adb -s {device_id} {cmd}").strip()
    connection = get_device_connection_type(device_id)
    ip_wifi = run("shell ip route | grep wlan0 | awk '{print $NF}'")
    # Cek status ADB WiFi
    wifi_status = "Tidak aktif"
    if ip_wifi:
        # Coba cek apakah device bisa diakses via WiFi (port 5555)
        out = subprocess.getoutput(f"adb connect {ip_wifi}:5555")
        if "connected to" in out or "already connected to" in out:
            wifi_status = f"Aktif ({ip_wifi}:5555)"
        else:
            wifi_status = f"Tidak aktif ({ip_wifi}:5555)"
    return {
        'id': device_id,
        'model': run("shell getprop ro.product.model"),
        'brand': run("shell getprop ro.product.brand"),
        'android': run("shell getprop ro.build.version.release"),
        'battery': re.sub(r'[^0-9]', '', run("shell dumpsys battery | grep level")),
        'root': run("shell whoami"),
        'ip': ip_wifi,
        'connection': connection,
        'wifi_status': wifi_status,
    }

def get_connected_devices_full():
    """
    Return list of (device_id, connection_type) where connection_type is 'USB' or 'WiFi'.
    """
    out = subprocess.getoutput("adb devices")
    devices = []
    for line in out.splitlines():
        if '\tdevice' in line:
            dev_id = line.split('\t')[0]
            if ':' in dev_id:
                devices.append((dev_id, 'WiFi'))
            else:
                devices.append((dev_id, 'USB'))
    return devices

def get_device_info_combined():
    devices = get_connected_devices_full()
    info_list = []
    seen = set()
    # Ambil info semua device
    raw_infos = []
    for dev_id, conn_type in devices:
        info = get_device_info(dev_id)
        info['connection_type'] = conn_type
        raw_infos.append(info)
    # Gabungkan berdasarkan (model, ip wifi)
    for info in raw_infos:
        key = (info['model'], info['ip'])
        if key in seen:
            continue
        # Cari info lain (USB/WiFi) dengan key sama
        others = [i for i in raw_infos if (i['model'], i['ip']) == key]
        # Gabungkan status koneksi
        koneksi_usb = any(i['connection_type']=='USB' for i in others)
        koneksi_wifi = any(i['connection_type']=='WiFi' for i in others)
        # Pilih id USB jika ada, jika tidak pakai id WiFi
        id_tampil = next((i['id'] for i in others if i['connection_type']=='USB'), others[0]['id'])
        info_gabungan = others[0].copy()
        info_gabungan['id'] = id_tampil
        info_gabungan['koneksi_usb'] = 'Aktif' if koneksi_usb else 'Tidak aktif'
        info_gabungan['koneksi_wifi'] = info_gabungan['wifi_status']
        seen.add(key)
        info_list.append(info_gabungan)
    return info_list

@app.route("/device-info")
def device_info():
    if 'json' in request.args:
        info = get_device_info_combined()
        return flask.jsonify(info)
    # Render info as HTML
    info = get_device_info_combined()
    info_html = ""
    if not info:
        info_html = "<div class='alert alert-danger'>Tidak ada device terhubung.</div>"
    for d in info:
        info_html += f"""
        <div class='card mb-2'>
          <div class='card-body'>
            <h5 class='card-title'><i class='fa-solid fa-mobile'></i> Device: {d['id']}</h5>
            <ul class='list-group list-group-flush'>
              <li class='list-group-item'>Model: <b>{d['brand']} {d['model']}</b></li>
              <li class='list-group-item'>Android: <b>{d['android']}</b></li>
              <li class='list-group-item'>Battery: <b>{d['battery']}%</b></li>
              <li class='list-group-item'>Root: <b>{d['root']}</b></li>
              <li class='list-group-item'>IP WiFi: <b>{d['ip']}</b></li>
              <li class='list-group-item'>Koneksi USB: <b>{d['koneksi_usb']}</b></li>
              <li class='list-group-item'>ADB WiFi: <b>{d['koneksi_wifi']}</b></li>
            </ul>
          </div>
        </div>
        """
    return info_html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
