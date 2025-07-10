from flask import Flask, render_template_string, redirect, url_for
import subprocess

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
          <h5 class='card-title'><i class='fa-solid fa-info-circle'></i> Info</h5>
          <p>Gunakan tombol di samping untuk mengelola ADB device Anda melalui web.</p>
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
</script>
</body>
</html>
"""

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
        return render_template_string(HTML, output=f"ADB Wi-Fi Aktif\nIP HP: {ip}\n\n{out}")
    return render_template_string(HTML, output=f"ADB Wi-Fi Aktif\nTapi Gagal Deteksi IP\n\n{out}")

@app.route("/ip", methods=["POST"])
def get_ip():
    cmd = "adb shell ip route | grep wlan0 | awk '{print $NF}'"
    ip = subprocess.getoutput(cmd).strip()
    if ip:
        with open("/tmp/hp_adb_ip.txt", "w") as f:
            f.write(ip)
        return render_template_string(HTML, output=f"IP HP: {ip}")
    return render_template_string(HTML, output="Gagal mendeteksi IP HP")

@app.route("/reset", methods=["POST"])
def reset():
    out = subprocess.getoutput("adb kill-server && adb start-server")
    return render_template_string(HTML, output=out)

@app.route("/status", methods=["POST"])
def status():
    out = subprocess.getoutput("adb devices")
    return render_template_string(HTML, output=out)

@app.route("/disable-wifi", methods=["POST"])
def disable_wifi():
    out = subprocess.getoutput("adb usb")
    return render_template_string(HTML, output=f"Nonaktifkan ADB Wi-Fi → USB mode aktif\n\n{out}")

@app.route("/enable-usb", methods=["POST"])
def enable_usb():
    out = subprocess.getoutput("adb usb")
    return render_template_string(HTML, output=f"ADB USB Mode Diaktifkan\n\n{out}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
