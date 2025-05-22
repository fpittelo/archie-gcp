import google.cloud.aiplatform as aiplatform
import os
import json
import logging
from flask import Flask, request, jsonify

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# ---- START DEBUGGING BLOCK (Reverting to manually set names, adding FULL ENV DUMP) ----
logging.info("---- STARTUP ENVIRONMENT VARIABLE CHECK (Using Manually Set Vars from Console) ----")
# These are the names confirmed to be in your Cloud Run console screenshot for revision -00003-9vd
raw_project_id_manual = os.environ.get("GCP_PROJECT")
raw_location_ch_manual = os.environ.get("GCP_REGION_CH") # As per your screenshot
raw_model_id_manual = os.environ.get("GEMINI_MODEL") # This one was working

logging.info(f"Attempting to read (manual) GCP_PROJECT. Value: '{raw_project_id_manual}', Type: {type(raw_project_id_manual)}")
logging.info(f"Attempting to read (manual) GCP_REGION_CH. Value: '{raw_location_ch_manual}', Type: {type(raw_location_ch_manual)}")
logging.info(f"Attempting to read (manual) GEMINI_MODEL. Value: '{raw_model_id_manual}', Type: {type(raw_model_id_manual)}")

logging.info("---- Dumping ALL available environment variables from os.environ: ----")
for key, value in os.environ.items():
    logging.info(f"'{key}': '{value}'")
logging.info("---- End of all available environment variables ----")
# ---- END DEBUGGING BLOCK ----

PROJECT_ID = raw_project_id_manual
LOCATION = raw_location_ch_manual
MODEL_ID = raw_model_id_manual

# Fallback for MODEL_ID if it was somehow None (though it was being read)
if not MODEL_ID:
    MODEL_ID = "gemini-2.0-pro-exp-02-05"

# Fallback for LOCATION if it was somehow None
if not LOCATION:
    LOCATION = "europe-west1"


logging.info(f"Effective PROJECT_ID for AI init: '{PROJECT_ID}'")
logging.info(f"Effective LOCATION for AI init: '{LOCATION}'")
logging.info(f"Effective MODEL_ID for AI init: '{MODEL_ID}'")

gemini_model_instance = None
if PROJECT_ID and LOCATION:
    try:
        aiplatform.init(project=PROJECT_ID, location=LOCATION)
        gemini_model_instance = aiplatform.GenerativeModel(MODEL_ID)
        logging.info(f"Vertex AI SDK initialized successfully for project {PROJECT_ID} in {LOCATION} using model {MODEL_ID}.")
    except Exception as e:
        logging.error(f"Error initializing Vertex AI SDK: {e}", exc_info=True)
        gemini_model_instance = None
else:
    # Update this log message to be accurate
    logging.error("Manually set GCP_PROJECT or GCP_REGION_CH environment variables were NOT resolved correctly by Python. SDK not initialized.")
    logging.error(f"Values at point of failure: PROJECT_ID ('{PROJECT_ID}') is {bool(PROJECT_ID)}, LOCATION ('{LOCATION}') is {bool(LOCATION)}")
# ---- END DEBUGGING BLOCK ----

# Initialize Vertex AI SDK
# These are automatically set in the Cloud Functions environment
PROJECT_ID = os.environ.get("GOOGLE_CLOUD_PROJECT") # Standard Cloud Run env var
LOCATION = os.environ.get("GOOGLE_CLOUD_REGION")    # Standard Cloud Run env var
if not LOCATION:
    LOCATION = "europe-west1" # Default to a common region if GOOGLE_CLOUD_REGION is somehow not set

# Model ID from environment variable, defaulting if not set
MODEL_ID = os.environ.get("GEMINI_MODEL", "gemini-2.0-pro-exp-02-05")

gemini_model_instance = None
if PROJECT_ID and LOCATION:
    try:
        aiplatform.init(project=PROJECT_ID, location=LOCATION) # Initialize with function's location for Vertex AI client
        gemini_model_instance = aiplatform.GenerativeModel(MODEL_ID)
        logging.info(f"Vertex AI SDK initialized successfully for project {PROJECT_ID} in {LOCATION} using model {MODEL_ID}.")
    except Exception as e:
        logging.error(f"Error initializing Vertex AI SDK: {e}", exc_info=True)
        gemini_model_instance = None # Ensure it's None if initialization fails
else:
    logging.error("GCP_PROJECT or GCP_REGION environment variables not set internally. Vertex AI SDK not initialized.")

app = Flask(__name__)

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

    request_json = request.get_json(silent=True)

    if not request_json or "question" not in request_json:
        logging.warning("Invalid request: JSON body with 'question' field is required.")
        return (json.dumps({"error": "Invalid request: JSON body with 'question' field is required."}), 400, headers)

    user_question = request_json["question"]
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)