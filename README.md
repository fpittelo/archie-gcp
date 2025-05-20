Archie AI: The EPFL AI Assistant for EA Powered by Google Cloud 🚀🤖🏛️
(EA + AI + API Integration)

Feeling bogged down by EA Repository upkeep? Imagine a smart assistant intimately familiar with EPFL's architectural landscape. What if you could simply ask who's responsible for an application instead of endless digging?

Your wish is granted! Introducing Archie AI Assistant

This project is forging an intelligent connection between EPFL's EA instance and the powerful capabilities of Google Cloud Platform and Google Gemini. Our mission is to create a helpful companion that can:

Answer your questions about EPFL's architecture residing in the EA repository.

Streamline the population and maintenance of the EA repository, reducing manual effort.

Think of Archie as your digital EA assistant 🧑‍🍳, preparing your data so you can concentrate on the strategic vision!

✨ The Core Idea ✨
EPFL's EA repository holds a treasure trove of architectural information, but accessing and updating it can sometimes feel like an expedition. We're harnessing the intelligence of Large Language Models (LLMs) through the Google Gemini API to:

Query in Natural Language: Pose questions like "Which applications depend on service X?" or "Show me the business capabilities supported by application Y."

Automate Data Input: Assist in filling in details, such as identifying application owners, stakeholders, or suggesting relationships between components (starting with the "Find Editors" use case!).

Enhance Data Quality: Propose corrections or highlight inconsistencies based on its understanding.

All seamlessly integrated within EPFL's Google Cloud ecosystem and secured with Google Cloud IAM.

🎯 Key Features (Planned & In-Progress) 🎯
✅ Natural Language Querying: Ask questions about the architecture.

✅ "Find Editors" Assistant: Intelligently suggest and add application editors to the EA tool (Our MVP!).

📝 Populate Application Details: Help fill in descriptions, business owners, etc. (Future).

🔗 Suggest Relationships: Identify potential connections between architectural elements (Future).

❓ Consistency Checks: Identify potential gaps or outdated information (Future).

... Your innovative ideas are welcome!

🏗️ Architectural Overview (High-Level) 🏗️
We're building this using a modern, cloud-native approach on Google Cloud Platform:

Frontend (UI): A user-friendly web interface (to be developed in the frontend/ directory, built with [React/Vue/Angular - TBD]) hosted on Google Cloud Storage. Users authenticate via EPFL Google Workspace accounts.

Backend (MCP Server): The central processing unit! A Python-based backend application (e.g., using Flask), containerized and deployed as a Google Cloud Run service. The source code is located in the functions/archiemcp/ directory. It handles:

Orchestrating requests from the frontend.

Communicating with the Google Gemini API (securely, potentially using credentials from Google Cloud Secret Manager or environment variables injected into Cloud Run).

Interacting with the EA REST API (using delegated user permissions via OAuth 2.0/Google Cloud IAM).

Managing specialized "Agents" or logic for specific tasks (like the "Find Editors" use case).

Google Gemini API: Provides advanced language understanding and generation capabilities.

EA API: The authoritative source of architectural data and the target for updates.

EPFL Google Workspace: Manages secure authentication and authorization for users.

GitHub & CI/CD: GitHub hosts our code repository. GitHub Actions manages our CI/CD pipelines, including:

Building the container image for the backend service.

Pushing the image to Google Artifact Registry.

Running Terraform to provision and manage GCP infrastructure (Cloud Run, GCS, IAM, etc.).

Deploying the new container image to Cloud Run.

(Future) Deploying frontend assets to Google Cloud Storage.

(Refer to the Archie-GCP Architecture document for a more detailed diagram and component descriptions.)

🛠️ Technology Stack 🛠️
Cloud: Google Cloud Platform (Cloud Run, Google Cloud Storage (for frontend hosting and Terraform state), Google Artifact Registry, Secret Manager, Cloud Logging, Cloud Monitoring)

AI: Google Gemini API

Backend: Python 🐍 (e.g., Flask), Google Cloud Run (containerized, sourced from functions/archiemcp/)

Frontend: JavaScript/TypeScript (React/Vue/Angular - TBD), hosted on Google Cloud Storage (sourced from frontend/)

Authentication: EPFL Google Workspace (OAuth 2.0)

Architecture Tool: EPFL EA Tool (interacted with via its API)

Infrastructure as Code: Terraform (configurations in infra/)

Code & CI/CD: GitHub / GitHub Actions (for build, infrastructure deployment, and service deployment)

Potentially: Langchain or similar frameworks to enhance prompt and context management within the backend service.

🚀 Getting Started (Development) 🚀
(High-level outline - detailed instructions will be in CONTRIBUTING.md)

Clone the repository: git clone [your-repo-url]

Understand the Project Structure:

.github/workflows/: Contains GitHub Actions CI/CD workflow definitions.

functions/archiemcp/: Contains the source code (Python/Flask), Dockerfile, and requirements.txt for the backend MCP Cloud Run service.

frontend/: (Future) Will contain the source code for the web application frontend.

infra/: Contains Terraform configuration files for defining GCP infrastructure.

Set up Google Cloud:

Ensure you have access to the necessary Google Cloud project and your gcloud CLI is authenticated and configured for this project.

Required APIs (Cloud Run, Artifact Registry, IAM, etc.) should be enabled.

Terraform Infrastructure Setup:

Navigate to the infra/ directory.

Initialize Terraform: terraform init (configure backend state storage in GCS as per project setup).

Review and select the appropriate .tfvars file for your target environment (e.g., dev.tfvars).

Plan and apply the Terraform configuration: terraform plan -var-file=<env>.tfvars then terraform apply -var-file=<env>.tfvars. This will provision the necessary GCP resources.

Backend Development (functions/archiemcp/):

Set up your Python virtual environment: python -m venv .venv and source .venv/bin/activate (or equivalent for your OS).

Install dependencies: pip install -r functions/archiemcp/requirements.txt.

Develop/modify the Flask application in main.py.

Update the Dockerfile in functions/archiemcp/ if necessary.

Secrets Management:

Ensure API keys (e.g., for Gemini) and other sensitive configurations are managed securely. This might involve storing them in Google Cloud Secret Manager and referencing them in your Terraform configurations to be injected as environment variables into the Cloud Run service.

Running & Deploying:

Local Backend Testing (Optional):

Build the Docker container: docker build -t archie-mcp-local ./functions/archiemcp/

Run the container locally: docker run -p 8080:8080 -e GCP_PROJECT=<your-project> -e GCP_REGION=<your-region> -e GEMINI_MODEL=<model-id> archie-mcp-local (adjust port and environment variables as needed).

Deployment via CI/CD: Pushing changes to the appropriate branch in GitHub will trigger the GitHub Actions workflow, which will:

Build and push the Docker image to Google Artifact Registry.

Apply Terraform configurations (if changed).

Deploy the new image to the Cloud Run service.

Frontend:

(Future) Develop frontend assets in the frontend/ directory.

(Future) For local development, use a local development server (e.g., npm start for React).

(Future) Deployment to Google Cloud Storage will be handled by a GitHub Actions workflow.

💡 Usage Example: Find Editors 💡
Access the A²I³ web interface (hosted on Google Cloud Storage) using your EPFL Google Workspace credentials.

Select an application from the displayed list (sourced from ADOIT via the EA API).

Click the "Find Editors" button.

The frontend sends the application details to the backend MCP server (Cloud Run service).

The MCP server processes the request, potentially forms a prompt, and calls the Google Gemini API.

Google Gemini suggests potential editors based on the provided information and its training.

The MCP server receives the response from Gemini and may perform additional actions, such as verifying/creating these editors in ADOIT through its API.

The results are formatted and sent back to the frontend, which presents them in the UI. Voilà! ✨

🤝 Contributing 🤝
This is an EPFL initiative! Your contributions, ideas, and feedback are highly valued.

Have an idea? Encountered a bug? Please open an issue!

Interested in contributing code? Fork the repository, create a dedicated branch, and submit a Pull Request.

Let's collaborate to make EA at EPFL even better! We might even share some delightful Swiss chocolate 🍫 for outstanding contributions 😉.

(A comprehensive CONTRIBUTING.md file with detailed guidelines is coming soon).

📜 License 📜
MIT License

Happy Architecting! 🇨🇭