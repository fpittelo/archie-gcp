# Change your imports at the top
import vertexai  # Import the main vertexai namespace
from vertexai.generative_models import GenerativeModel # Import GenerativeModel specifically
import os
import json
import logging
from flask import Flask, request, jsonify

# Configure basic logging
logging.basicConfig(level=logging.INFO)

# Log the installed library version (still good to keep for future reference)
try:
    # To get the underlying google-cloud-aiplatform version
    import google.cloud.aiplatform as aiplatform_version_check
    logging.info(f"Underlying google-cloud-aiplatform version: {aiplatform_version_check.__version__}")
except ImportError:
    logging.warning("Could not import google.cloud.aiplatform for version check.")


# ---- STARTUP ENVIRONMENT VARIABLE CHECK AND AI INITIALIZATION ----
logging.info("---- STARTUP ENVIRONMENT VARIABLE CHECK (Using Manually Set Vars from Console) ----")
raw_project_id_manual = os.environ.get("GCP_PROJECT")
raw_location_ch_manual = os.environ.get("GCP_REGION_EU")
raw_model_id_manual = os.environ.get("GEMINI_MODEL")

logging.info(f"Read (manual) GCP_PROJECT. Value: '{raw_project_id_manual}', Type: {type(raw_project_id_manual)}")
logging.info(f"Read (manual) GCP_REGION_EU. Value: '{raw_location_ch_manual}', Type: {type(raw_location_ch_manual)}")
logging.info(f"Read (manual) GEMINI_MODEL. Value: '{raw_model_id_manual}', Type: {type(raw_model_id_manual)}")


PROJECT_ID = raw_project_id_manual
LOCATION = raw_location_ch_manual
MODEL_ID = raw_model_id_manual

# Fallbacks
if not MODEL_ID:
    MODEL_ID = "gemini-2.0-pro-exp-02-05"
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