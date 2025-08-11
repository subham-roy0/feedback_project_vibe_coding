import http.server
import socketserver
import webbrowser
from urllib.parse import parse_qs
import os

PORT = 8000
HTML_FILE = "index.html"
DATA_FILE = "data.txt"

positive_words = ["good", "great", "excellent", "happy", "love", "amazing"]
negative_words = ["bad", "poor", "terrible", "sad", "hate", "awful"]

class FeedbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = HTML_FILE
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/save":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode("utf-8")
            feedback = parse_qs(post_data).get("feedback", [""])[0]

            # Save feedback
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(feedback)

            # Analyse sentiment
            feedback_lower = feedback.lower()
            sentiment = "Neutral"
            if any(word in feedback_lower for word in positive_words):
                sentiment = "Positive"
            elif any(word in feedback_lower for word in negative_words):
                sentiment = "Negative"

            # Respond with sentiment result
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"<h2>Feedback Saved!</h2><p>Sentiment: <b>{sentiment}</b></p>".encode())

# Start server and open HTML
with socketserver.TCPServer(("", PORT), FeedbackHandler) as httpd:
    print(f"Server started at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    httpd.serve_forever()
