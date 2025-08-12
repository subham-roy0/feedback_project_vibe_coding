import http.server
import socketserver
import webbrowser
from urllib.parse import parse_qs
import os
from datetime import datetime

PORT = 8000
HTML_FILE = "index.html"
DATA_FILE = "data.txt"
SCORE_FILE = "score.txt"
HISTORY_FILE = "history.txt"

# Exact match lists (must match HTML radio button values exactly)
positive_words = ["good", "great", "somewhat good", "excellent", "happy", "love", "amazing"]
negative_words = ["bad", "poor", "somewhat bad", "terrible", "sad", "hate", "awful"]
neutral_words = ["average", "okay", "neither good neither bad"]

class FeedbackHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = HTML_FILE
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path == "/save":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode("utf-8")
            feedback = parse_qs(post_data).get("feedback", [""])[0].strip().lower()

            # Save latest feedback (for record)
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                f.write(feedback)

            # Determine score change
            if feedback in positive_words:
                score_change = 1
                feedback_sentiment = "Positive"
            if feedback in negative_words:
                score_change = -1
                feedback_sentiment = "Negative"
            if feedback in neutral_words:
                score_change = 0
                feedback_sentiment = "Neutral"

            # Read current score
            total_score = 0
            if os.path.exists(SCORE_FILE):
                try:
                    with open(SCORE_FILE, "r", encoding="utf-8") as sf:
                        total_score = int(sf.read().strip() or "0")
                except ValueError:
                    total_score = 0

            # Update score
            total_score += score_change
            with open(SCORE_FILE, "w", encoding="utf-8") as sf:
                sf.write(str(total_score))

            # Determine overall sentiment from score
            if total_score > 0:
                overall_sentiment = "Positive"
            if total_score < 0:
                overall_sentiment = "Negative"
            else:
                overall_sentiment = "Neutral"

            # Append to history file
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(HISTORY_FILE, "a", encoding="utf-8") as hf:
                hf.write(f"{timestamp}|{feedback}|{feedback_sentiment}|{score_change}|{total_score}\n")

            # Read history for display
            history_entries = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as hf:
                    for line in hf:
                        parts = line.strip().split("|")
                        if len(parts) == 5:
                            history_entries.append(parts)

            # Build HTML table
            history_html = """
            <h3>Feedback History</h3>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Timestamp</th>
                    <th>Feedback</th>
                    <th>Sentiment</th>
                    <th>Score Change</th>
                    <th>Total Score After</th>
                </tr>
            """
            for entry in history_entries:
                history_html += f"""
                <tr>
                    <td>{entry[0]}</td>
                    <td>{entry[1]}</td>
                    <td>{entry[2]}</td>
                    <td>{entry[3]}</td>
                    <td>{entry[4]}</td>
                </tr>
                """
            history_html += "</table>"

            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(f"""
                <h2>Feedback Saved!</h2>
                <p>Current Feedback: <b>{feedback}</b></p>
                <p>Feedback Sentiment: <b>{feedback_sentiment}</b> (Score Change: {score_change})</p>
                <p>Updated Total Score: <b>{total_score}</b></p>
                <p>Overall Sentiment: <b>{overall_sentiment}</b></p>
                {history_html}
            """.encode())

# Start the server
with socketserver.TCPServer(("", PORT), FeedbackHandler) as httpd:
    print(f"Server started at http://localhost:{PORT}")
    webbrowser.open(f"http://localhost:{PORT}")
    httpd.serve_forever()
