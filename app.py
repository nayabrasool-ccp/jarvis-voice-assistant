import http.server
import socketserver
import threading
import os
import platform
import json
import time

# Cloud Configuration - Port 80 is the standard HTTP port
PORT = 80
DIRECTORY = os.getcwd()

class ResourceDashboardHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        if self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            # Enable CORS so the API is globally reachable if needed
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else (0, 0, 0)
            metrics = {
                "os": platform.system(),
                "os_release": platform.release(),
                "architecture": platform.machine(),
                "cpu_load_1m": load_avg,
                "current_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "shared_directory": DIRECTORY,
                "files_count": len(os.listdir(DIRECTORY))
            }
            self.wfile.write(json.dumps(metrics).encode('utf-8'))
            
        elif self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            
            html_dashboard = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>JARVIS Core - AWS EC2 Cloud Live Metrics</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; background: #0c101f; color: #00ffcc; padding: 30px; text-align: center; }
                    .card { background: #141b37; border: 1px solid #ff9900; border-radius: 8px; padding: 20px; margin: 20px auto; max-width: 600px; box-shadow: 0 0 15px rgba(255,153,0,0.2); text-align: left; }
                    h1 { color: #fff; border-bottom: 2px solid #ff9900; padding-bottom: 10px; display: inline-block; }
                    .metric { font-size: 1.2rem; margin: 10px 0; }
                    .value { color: #fff; font-weight: bold; }
                    .badge { background: #ff9900; color: #0c101f; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; float: right;}
                </style>
                <script>
                    async function fetchStats() {
                        try {
                            let response = await fetch('/api/stats');
                            let data = await response.json();
                            document.getElementById('os').innerText = data.os + " (" + data.os_release + ")";
                            document.getElementById('arch').innerText = data.architecture;
                            document.getElementById('cpu').innerText = JSON.stringify(data.cpu_load_1m);
                            document.getElementById('time').innerText = data.current_time;
                        } catch (err) {
                            document.getElementById('os').innerText = "Link Offline";
                        }
                    }
                    setInterval(fetchStats, 2000);
                    window.onload = fetchStats;
                </script>
            </head>
            <body>
                <h1>JARVIS Cloud Instance Telemetry Engine</h1>
                <div class="card">
                    <h2>☁️ AWS EC2 Live Metrics <span class="badge">Production</span></h2>
                    <div class="metric">Host Environment: <span id="os" class="value">Loading...</span></div>
                    <div class="metric">Architecture Target: <span id="arch" class="value">Loading...</span></div>
                    <div class="metric">Linux Load Average: <span id="cpu" class="value">Loading...</span></div>
                    <div class="metric">AWS Instance Time: <span id="time" class="value">Loading...</span></div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_dashboard.encode('utf-8'))
        else:
            super().do_GET()

def launch_server():
    # Bind explicitly to 0.0.0.0 for public traffic visibility
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), ResourceDashboardHandler) as httpd:
        print(f"🚀 [JARVIS Cloud] Operational on Public HTTP Port {PORT}...")
        httpd.serve_forever()

if __name__ == "__main__":
    server_thread = threading.Thread(target=launch_server, daemon=True)
    server_thread.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Cloud server closing cleanly.")
