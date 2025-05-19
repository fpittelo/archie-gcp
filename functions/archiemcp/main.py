from flask import Flask

# Define the Flask app instance globally
app = Flask(__name__)

@app.route('/')
def hello():
    """A simple hello world endpoint."""
    return "Hello, World from Minimal Flask App!"

# Note: The 'if __name__ == "__main__": app.run(...)' block is NOT needed for GCF deployment
# as the platform provides the web server (via Functions Framework in this test).