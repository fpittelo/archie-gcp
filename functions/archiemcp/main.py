# Change your imports at the top
import vertexai  # Import the main vertexai namespace
from vertexai.generative_models import GenerativeModel # Import GenerativeModel specifically
import os
import json
import logging
from flask import Flask, request, jsonify, redirect, session, url_for
from google_auth_oauthlib.flow import Flow

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
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key_please_change_in_prod")
if app.secret_key == "dev_secret_key_please_change_in_prod":
    logging.warning("Using default FLASK_SECRET_KEY. Please set a strong secret key in your environment for production.")



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

    # Placeholder: Exchange authorization code for tokens
    auth_code = request.args.get('code')
    logging.info(f"Received callback from Google. Authorization code (first 10 chars): {str(auth_code)[:10]}...")
    # In a real app:
    # flow.fetch_token(authorization_response=request.url)
    # credentials = flow.credentials
    # # Store credentials, get user info, create session, etc.
    return f"Login successful (callback received)! Auth Code (snippet): {str(auth_code)[:10]}... You would now exchange the code for tokens."


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)