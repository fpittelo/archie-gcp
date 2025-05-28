# Change your imports at the top
import vertexai  # Import the main vertexai namespace
from vertexai.generative_models import GenerativeModel # Import GenerativeModel specifically
import os
import json
import logging
from flask import Flask, request, jsonify, redirect, session, url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token # For verifying ID token
from google.auth.transport import requests as google_auth_requests # For verifying ID token
from werkzeug.middleware.proxy_fix import ProxyFix # <--- Add this import

# Unique log line for deployment verification
logging.info("Main.py version with OAuth routes is running! - DEBUG_LOG_V2")

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Log the installed library version (still good to keep for future reference)
try:
    # To get the underlying google-cloud-aiplatform version
    import google.cloud.aiplatform as aiplatform_version_check
    logging.info(f"Underlying google-cloud-aiplatform version: {aiplatform_version_check.__version__}")
except ImportError:
    logging.warning("Could not import google.cloud.aiplatform for version check.")


# --- Constants for OAuth ---
# ---- STARTUP ENVIRONMENT VARIABLE CHECK AND AI INITIALIZATION ----
logging.info("---- STARTUP ENVIRONMENT VARIABLE CHECK (Using Manually Set Vars from Console) ----")
raw_project_id_manual = os.environ.get("GCP_PROJECT")
raw_location_ch_manual = os.environ.get("GCP_REGION_EU")
raw_model_id_manual = os.environ.get("GEMINI_MODEL")
GOOGLE_OAUTH_CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID")
GOOGLE_OAUTH_CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET")

logging.info(f"Read (manual) GCP_PROJECT. Value: '{raw_project_id_manual}', Type: {type(raw_project_id_manual)}")
logging.info(f"Read (manual) GCP_REGION_EU. Value: '{raw_location_ch_manual}', Type: {type(raw_location_ch_manual)}")
logging.info(f"Read (manual) GEMINI_MODEL. Value: '{raw_model_id_manual}', Type: {type(raw_model_id_manual)}")
logging.info(f"Read GOOGLE_OAUTH_CLIENT_ID. Is set: {bool(GOOGLE_OAUTH_CLIENT_ID)}")
logging.info(f"Read GOOGLE_OAUTH_CLIENT_SECRET. Is set: {bool(GOOGLE_OAUTH_CLIENT_SECRET)}")


PROJECT_ID = raw_project_id_manual
LOCATION = raw_location_ch_manual
MODEL_ID = raw_model_id_manual

# --- OAuth Configuration ---
CLIENT_SECRETS_DICT = None
if GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET:
    CLIENT_SECRETS_DICT = {
        "web": {
            "client_id": GOOGLE_OAUTH_CLIENT_ID,
            "client_secret": GOOGLE_OAUTH_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
else:
    logging.error("GOOGLE_OAUTH_CLIENT_ID or GOOGLE_OAUTH_CLIENT_SECRET not set. OAuth flow will not work.")

# Fallbacks
if not MODEL_ID:
    MODEL_ID = "gemini-2.0-flash-001"
if not LOCATION:
    LOCATION = "europe-west1" # Should be set from env, but as a last resort

logging.info(f"Effective PROJECT_ID for AI init: '{PROJECT_ID}'")
logging.info(f"Effective LOCATION for AI init: '{LOCATION}'")
logging.info(f"Effective MODEL_ID for AI init: '{MODEL_ID}'")

gemini_model_instance = None # Initialize once
if PROJECT_ID and LOCATION:
    try:
        logging.info(f"Initializing Vertex AI with project='{PROJECT_ID}', location='{LOCATION}' using vertexai.init()...")
        vertexai.init(project=PROJECT_ID, location=LOCATION) # Use vertexai.init()
        logging.info("Vertex AI initialized via vertexai.init(). Attempting to load GenerativeModel...")
        gemini_model_instance = GenerativeModel(MODEL_ID) # Use GenerativeModel directly after the new import
        logging.info(f"Vertex AI GenerativeModel '{MODEL_ID}' loaded successfully.")
    except AttributeError as ae: # Should ideally not happen with the new import
        logging.error(f"AttributeError during Vertex AI SDK usage: {ae}", exc_info=True)
        try:
            logging.error(f"google-cloud-aiplatform version at time of AttributeError: {aiplatform_version_check.__version__}")
        except NameError:
            logging.error("google-cloud-aiplatform version could not be determined for AttributeError.")
        gemini_model_instance = None
    except Exception as e:
        logging.error(f"General error initializing Vertex AI SDK or Model: {e}", exc_info=True)
        gemini_model_instance = None
else:
    logging.error("Manually set GCP_PROJECT or GCP_REGION_EU were NOT resolved by Python. SDK not initialized.")
    logging.error(f"Values at point of failure: PROJECT_ID ('{PROJECT_ID}') is {bool(PROJECT_ID)}, LOCATION ('{LOCATION}') is {bool(LOCATION)}")
# ---- END INITIALIZATION ----

app = Flask(__name__)

# --- Add ProxyFix ---
# This tells Flask to trust the X-Forwarded-Proto (and other) headers
# set by the Cloud Run proxy, so url_for(_external=True) generates https URLs.
# Adjust x_for, x_proto, x_host, x_prefix as needed depending on your proxy setup.
# For Cloud Run, these defaults are usually fine.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
# --- End ProxyFix ---
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_please_change_in_prod")
if app.secret_key == "dev_secret_key_please_change_in_prod":
    logging.warning("Using default FLASK_SECRET_KEY. Please set a strong secret key in your environment for production.")

# --- Helper Functions ---
def credentials_to_dict(credentials):
    return {'token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': credentials.scopes}

@app.route('/', methods=['POST', 'OPTIONS']) # Removed 'request' parameter
def archiemcp():  # Removed 'request' parameter - Flask provides it automatically
    """
    HTTP Cloud Function to proxy requests to the Gemini API.
    Args:
        request (flask.Request): The request object.
                                 Expected JSON body: {"question": "Your question here"}
    Returns:
        A tuple containing the JSON response, HTTP status code, and headers.
    """
    headers = {
        'Access-Control-Allow-Origin': '*',  # For development. Restrict in production.
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Content-Type': 'application/json'
    }

    if request.method == 'OPTIONS':
        return ('', 204, headers)

    if request.method != "POST":
        return (json.dumps({"error": "Only POST requests are accepted"}), 405, headers)

    if not gemini_model_instance:
        logging.error("Gemini model not initialized. Cannot process request.")
        return (json.dumps({"error": "Internal server error: Model not initialized"}), 500, headers)

    # To handle multipart/form-data as sent by the frontend's FormData
    if "question" not in request.form:
        # Fallback for testing with tools that send application/json
        request_json = request.get_json(silent=True)
        if not request_json or "question" not in request_json:
            logging.warning("Invalid request: 'question' field missing in form data or JSON body.")
            return (json.dumps({"error": "Invalid request: 'question' field is required in form data or JSON body."}), 400, headers)
        user_question = request_json["question"]
    else:
        user_question = request.form["question"]

    logging.info(f"Received question for {MODEL_ID}: {user_question[:100]}...") # Log snippet

    try:
        # Example generation config, adjust as needed
        generation_config = {
            "max_output_tokens": 2048,
            "temperature": 0.7,
            "top_p": 1.0,
        }
        
        response = gemini_model_instance.generate_content(
            [user_question], # Ensure content is passed as a list or correct type
            generation_config=generation_config,
            # stream=False, # Set to True if you intend to stream responses
        )
        logging.info("Successfully received response from Gemini API.")

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            gemini_answer = "".join(part.text for part in response.candidates[0].content.parts if hasattr(part, 'text'))
        else:
            # Log the actual response structure if it's not as expected
            logging.warning(f"Gemini API response structure not as expected or empty. Full response: {response}")
            gemini_answer = "Could not retrieve a valid answer from the model at this time."

        return (json.dumps({"answer": gemini_answer}), 200, headers)

    except Exception as e:
        logging.error(f"Error during Gemini API call or response processing: {e}", exc_info=True)
        # Provide a more generic error message to the client for security
        return (json.dumps({"error": "An internal error occurred while processing your request."}), 500, headers)

# --- Google OAuth Routes ---

@app.route('/auth/google', methods=['GET'])
def auth_google_initiate():
    """Initiates the Google OAuth 2.0 login flow."""
    if not CLIENT_SECRETS_DICT:
        logging.error("OAuth client secrets not configured. Cannot initiate login.")
        return "OAuth is not configured correctly on the server.", 500

    redirect_uri = url_for('auth_google_callback', _external=True)
    logging.info(f"Calculated redirect_uri for OAuth: {redirect_uri}")

    flow = Flow.from_client_config(
        client_config=CLIENT_SECRETS_DICT,
        scopes=[
            "https://www.googleapis.com/auth/userinfo.profile",
            "https://www.googleapis.com/auth/userinfo.email",
            "openid"
        ],
        redirect_uri=redirect_uri
    )

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent'
    )
    session['oauth_state'] = state
    logging.info(f"Redirecting to Google authorization URL. State: {state}")
    return redirect(authorization_url)

@app.route('/auth/google/callback', methods=['GET'])
def auth_google_callback():
    """Handles the callback from Google after user authentication."""
    state = session.pop('oauth_state', None)
    if not state or state != request.args.get('state'):
        logging.error("OAuth state mismatch. Possible CSRF attack.")
        return "Invalid state parameter.", 400

    if not CLIENT_SECRETS_DICT:
        logging.error("OAuth client secrets not configured. Cannot process callback.")
        return "OAuth is not configured correctly on the server.", 500

    redirect_uri = url_for('auth_google_callback', _external=True) # Must match what was used in initiate
    flow = Flow.from_client_config(
        client_config=CLIENT_SECRETS_DICT,
        scopes=None, # Scopes are not needed again here if state is used correctly
        redirect_uri=redirect_uri
    )

    try:
        # Use the full URL for `fetch_token` as it contains the state and code
        flow.fetch_token(authorization_response=request.url)
    except Exception as e:
        logging.error(f"Failed to fetch token: {e}", exc_info=True)
        return "Failed to fetch authorization token.", 500

    credentials = flow.credentials
    if not credentials or not credentials.id_token:
        logging.error("Failed to obtain ID token from credentials.")
        return "Could not obtain ID token.", 500

    try:
        # Verify the ID token and get user info
        # You MUST verify the ID token on the server-side.
        # The audience is your app's OAuth Client ID.
        id_info = id_token.verify_oauth2_token(
            credentials.id_token,
            google_auth_requests.Request(),
            CLIENT_SECRETS_DICT['web']['client_id']
        )

        # Store user information in session
        session['google_id'] = id_info.get('sub')
        session['name'] = id_info.get('name')
        session['email'] = id_info.get('email')
        session['picture'] = id_info.get('picture')
        session['credentials'] = credentials_to_dict(credentials) # Helper to store serializable credentials

        logging.info(f"User {session['email']} logged in successfully.")

        FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL")
        if FRONTEND_BASE_URL:
            # Redirect to the configured frontend URL.
            # This should be the URL where your index.html is served.
            # e.g., "https://storage.googleapis.com/your-frontend-bucket"
            redirect_target_url = FRONTEND_BASE_URL
            logging.info(f"Redirecting to FRONTEND_BASE_URL: {redirect_target_url}")
        else:
            logging.warning("FRONTEND_BASE_URL environment variable not set. "
                            "Falling back to internal '/app' page. "
                            "Set FRONTEND_BASE_URL to your frontend's main page URL.")
            redirect_target_url = url_for('archiemcp_page') # Fallback
        return redirect(redirect_target_url)
    except ValueError as e:
        logging.error(f"ID token verification failed: {e}", exc_info=True)
        return "ID token verification failed.", 400

# --- Placeholder App Page and Logout ---
@app.route('/app', methods=['GET']) # Example route for after login
def archiemcp_page():
    if 'email' not in session:
        # If FRONTEND_BASE_URL is not set and user lands here unauthenticated,
        # redirect to login.
        return redirect(url_for('auth_google_initiate'))

    user_email = session.get('email', 'Guest')
    user_name = session.get('name', 'User')
    # This page would typically be your main application interface
    # For now, just a welcome message.
    return f"""
        <h1>Welcome to Archie MCP (Fallback Page)</h1>
        <p>Hello, {user_name} ({user_email})! You are logged in.</p>
        <p><a href="{url_for('logout')}">Logout</a></p>
        <p><em>Note: You are seeing this fallback page because the FRONTEND_BASE_URL might not be configured correctly. Normally, you would be redirected to the main application page.</em></p>
    """
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth_google_initiate')) # Or redirect to a public landing page

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)