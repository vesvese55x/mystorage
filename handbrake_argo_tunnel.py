
import os
import subprocess
import re
import time
from flask import Flask, request, jsonify
from subprocess import Popen, PIPE

# Flask app setup
app = Flask(__name__)

def check_handbrake_installed():
    """Ensure HandBrakeCLI is installed."""
    try:
        subprocess.run(["HandBrakeCLI", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("HandBrakeCLI is installed.")
    except FileNotFoundError:
        print("HandBrakeCLI is not installed. Install it using: `sudo apt install handbrake-cli`")
        exit(1)

@app.route('/convert', methods=['POST'])
def convert_video():
    """Convert video using HandBrakeCLI."""
    data = request.json
    input_file = data.get('input_file')
    output_file = data.get('output_file')
    preset = data.get('preset', 'Fast 1080p30')

    if not input_file or not output_file:
        return jsonify({"error": "input_file and output_file are required."}), 400

    if not os.path.isfile(input_file):
        return jsonify({"error": f"Input file does not exist: {input_file}"}), 400

    command = [
        "HandBrakeCLI",
        "-i", input_file,
        "-o", output_file,
        "--preset", preset
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return jsonify({"message": f"Conversion successful! Output saved to {output_file}"})
        else:
            return jsonify({"error": result.stderr}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

class ArgoTunnel:
    def __init__(self, port, proto='http', metrics=49589):
        self.connection = None
        self.proto = proto
        self.port = port
        self.metricPort = metrics

    def start(self):
        """Start ArgoTunnel and return public URL."""
        try:
            self.connection = Popen(
                ["cloudflared", "tunnel", "--url", f"{self.proto}://localhost:{self.port}"],
                stdout=PIPE, stderr=PIPE, text=True
            )
            time.sleep(5)
            for _ in range(10):  # Wait and parse output for hostname
                line = self.connection.stdout.readline()
                if "https://" in line:
                    url = re.search(r"https://[\w.-]+", line)
                    if url:
                        return url.group(0)
            raise RuntimeError("Failed to get public URL from ArgoTunnel.")
        except Exception as e:
            raise RuntimeError(f"Error starting ArgoTunnel: {e}")

    def stop(self):
        if self.connection:
            self.connection.terminate()

if __name__ == "__main__":
    import threading

    check_handbrake_installed()

    # Start Flask app in a separate thread
    port = 5000
    flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=port, debug=False))
    flask_thread.daemon = True
    flask_thread.start()

    # Start ArgoTunnel and display the public URL
    tunnel = ArgoTunnel(port)
    try:
        public_url = tunnel.start()
        print(f"HandBrake Web Interface is available at: {public_url}")
        flask_thread.join()
    except Exception as e:
        print(str(e))
        tunnel.stop()
