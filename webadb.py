from flask import Flask, render_template_string, redirect, url_for
import subprocess

app = Flask(__name__)

HTML = """
<h2>ADB Wi-Fi Bridge</h2>
<form action="/tcpip" method="post"><button>Aktifkan ADB Wi-Fi</button></form>
<form action="/ip" method="post"><button>Cek IP HP</button></form>
<form action="/reset" method="post"><button>Reset ADB Server</button></form>
<form action="/status" method="post"><button>Cek Status ADB</button></form>
<form action="/disable-wifi" method="post"><button>Nonaktifkan ADB Wi-Fi</button></form>
<form action="/enable-usb" method="post"><button>Aktifkan ADB USB</button></form>
<pre style="background:#111;color:#0f0;padding:10px;">{{output}}</pre>
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
