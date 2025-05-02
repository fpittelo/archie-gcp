# Archie AI: The EPFL AI Assistant for EA Powered by Google Cloud 🚀🤖🏛️

**(EA + AI + API Integration)**

---

**Feeling bogged down by EA Repository upkeep?** Imagine a smart assistant intimately familiar with EPFL's architectural landscape. What if you could simply *ask* who's responsible for an application instead of endless digging?

**Your wish is granted! Introducing Archie AI Assistant**

This project is forging an intelligent connection between EPFL's EA instance and the powerful capabilities of [Google Cloud Platform](https://cloud.google.com/) and [Google Gemini](https://gemini.google.com/). Our mission is to create a helpful companion that can:

1.  **Answer your questions** about EPFL's architecture residing in the EA repository.
2.  **Streamline the population and maintenance** of the EA repository, reducing manual effort.

Think of Archie as your **digital EA assistant** 🧑‍🍳, preparing your data so you can concentrate on the strategic vision!

---

## ✨ The Core Idea ✨

EPFL's EA repository holds a treasure trove of architectural information, but accessing and updating it can sometimes feel like an expedition. We're harnessing the intelligence of Large Language Models (LLMs) through the Google Gemini API to:

* **Query in Natural Language:** Pose questions like "Which applications depend on service X?" or "Show me the business capabilities supported by application Y."
* **Automate Data Input:** Assist in filling in details, such as identifying application owners, stakeholders, or suggesting relationships between components (starting with the "Find Editors" use case!).
* **Enhance Data Quality:** Propose corrections or highlight inconsistencies based on its understanding.

All seamlessly integrated within EPFL's Google Cloud ecosystem and secured with Google Cloud IAM.

---

## 🎯 Key Features (Planned & In-Progress) 🎯

* ✅ **Natural Language Querying:** Ask questions about the architecture.
* ✅ **"Find Editors" Assistant:** Intelligently suggest and add application editors to the EA tool (Our MVP!).
* 📝 **Populate Application Details:** Help fill in descriptions, business owners, etc. (Future).
* 🔗 **Suggest Relationships:** Identify potential connections between architectural elements (Future).
* ❓ **Consistency Checks:** Identify potential gaps or outdated information (Future).
* *... Your innovative ideas are welcome!*

---

## 🏗️ Architectural Overview (High-Level) 🏗️

We're building this using a modern, cloud-native approach on Google Cloud Platform:

1.  **Frontend (UI):** A user-friendly web interface (built with [React/Vue/Angular - TBD]) hosted on Google Cloud Storage and served via Cloud CDN. Users authenticate via EPFL Google Workspace accounts.
2.  **Backend (MCP Server):** The central processing unit! Serverless Google Cloud Functions written in Python handle:
    * Orchestrating requests.
    * Communicating with the Google Gemini API (securely, using credentials from Google Cloud Secret Manager).
    * Interacting with the EA REST API (using delegated user permissions via OAuth 2.0/Google Cloud IAM).
    * Managing specialized "Agents" for specific tasks (like the "Editor Finder Agent").
3.  **Google Gemini API:** Provides advanced language understanding and generation capabilities.
4.  **EA API:** The authoritative source of architectural data and the target for updates.
5.  **EPFL Google Workspace:** Manages secure authentication and authorization.
6.  **GitHub:** Hosts our code repository and manages our CI/CD pipelines (GitHub Actions or Google Cloud Build).

**(Stay tuned for a detailed architecture diagram soon!)**

---

## 🛠️ Technology Stack 🛠️

* **Cloud:** Google Cloud Platform (Cloud Functions, Cloud Storage, Cloud CDN, Secret Manager, Cloud Logging, Cloud Monitoring)
* **AI:** Google Gemini API
* **Backend:** Python 🐍, Google Cloud Functions
* **Frontend:** JavaScript/TypeScript (React/Vue/Angular - TBD)
* **Authentication:** EPFL Google Workspace (OAuth 2.0)
* **Architecture Tool:** EPFL EA Tool
* **Code & CI/CD:** GitHub / GitHub Actions / Google Cloud Build
* **Potentially:** `Langchain` or similar frameworks to enhance prompt and context management.

---

## 🚀 Getting Started (Development) 🚀

*(High-level outline - detailed instructions will be in `CONTRIBUTING.md`)*

1.  **Clone the repository:** `git clone [your-repo-url]`
2.  **Set up Google Cloud:** Ensure you have access to the necessary Google Cloud resources.
3.  **Configure Google Cloud IAM:** The application registration details will be required.
4.  **Python Environment:** Set up your Python environment (`venv` is recommended) and install dependencies (`pip install -r requirements.txt`).
5.  **Secrets Management:** Configure access to Google Cloud Secret Manager for API keys (primarily Google Gemini).
6.  **Run it!** (Specific instructions for running the Cloud Functions locally and the frontend will follow).

---

## 💡 Usage Example: Find Editors 💡

1.  Log in to the A²I³ web interface using your EPFL Google Workspace credentials.
2.  Select an application from the displayed list (sourced from ADOIT).
3.  Click the "Find Editors" button.
4.  A²I³ transmits the application details to Google Gemini via the MCP Server agent.
5.  Google Gemini suggests potential editors based on the provided information.
6.  The MCP Server agent may verify/create these editors in ADOIT through its API.
7.  The results are presented in the UI. Voilà! ✨

---

## 🤝 Contributing 🤝

This is an EPFL initiative! Your contributions, ideas, and feedback are highly valued.

* Have an idea? Encountered a bug? Please open an issue!
* Interested in contributing code? Fork the repository, create a dedicated branch, and submit a Pull Request.
* Let's collaborate to make EA at EPFL even better! We might even share some delightful Swiss chocolate 🍫 for outstanding contributions 😉.

*(A comprehensive `CONTRIBUTING.md` file with detailed guidelines is coming soon).*

---

## 📜 License 📜

MIT License

---

**Happy Architecting!** 🇨🇭