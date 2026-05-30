import subprocess
import os
import sys
import threading
import http.server
import socketserver

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(__file__, '..'))
# Determine the repository root (one level up from raven-mood)
REPO_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, '..'))
# Path to the mood detector script located in sibling 'skills' directory
MOOD_DETECTOR = os.path.join(REPO_ROOT, 'skills', 'mood-detector', 'mood_detector.py')
REPORT_MD = os.path.join(PROJECT_ROOT, 'mood_report.md')
REPORT_HTML = os.path.join(PROJECT_ROOT, 'mood_report.html')

def generate_report():
    try:
        result = subprocess.run([sys.executable, MOOD_DETECTOR], capture_output=True, text=True, check=True)
        markdown = result.stdout
    except subprocess.CalledProcessError as e:
        markdown = f"Error running mood detector:\n{e.stdout}\n{e.stderr}"
    # Write markdown file
    with open(REPORT_MD, 'w', encoding='utf-8') as f:
        f.write(markdown)
    # Simple HTML wrapper
    html_content = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Project Mood Report</title></head><body><pre>{markdown}</pre></body></html>"
    with open(REPORT_HTML, 'w', encoding='utf-8') as f:
        f.write(html_content)

class SilentHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress logging

def serve(port=8001):
    os.chdir(PROJECT_ROOT)
    handler = SilentHandler
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving mood report at http://localhost:{port}/mood_report.html")
        httpd.serve_forever()

if __name__ == "__main__":
    generate_report()
    # Run server in main thread (blocking)
    serve()
