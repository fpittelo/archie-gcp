resource "google_service_account" "archiemcp_function_sa" {
  project      = var.project_id
  account_id   = "${var.cloudfunction}-sa"
  display_name = "Service Account for ArchieMCP Function"
}

# Cloud Run v2 Service resource
resource "google_cloud_run_v2_service" "archiemcp_service" {
  name     = var.cloudfunction // e.g., "archiefunct-dev"
  project  = var.project_id
  location = var.region 
  deletion_protection = false # Add this line

  template {
    service_account = google_service_account.archiemcp_function_sa.email
    containers { 
      image = var.archie_mcp_image_uri // e.g., "europe-west6-docker.pkg.dev/archie-458607/archie-mcp-dev/archiefunct:latest"
      ports {
        container_port = 8080
      }
      
      env {
        name  = "GCP_PROJECT"
        value = var.project_id # This 'var.project_id' is a Terraform variable
      }
      env {
        name  = "GCP_REGION_EU"
        value = var.region # This 'var.region' is a Terraform variable, ensure it gets the correct region e.g. europe-west6
      }
      env {
        name  = "GEMINI_MODEL"
        value = var.gemini_model_name # You'll need to define/pass this Terraform variable too
                                     # e.g., "gemini-2.0-pro-exp-02-05" or pass from GitHub Actions
      }
      env {
        name  = "GOOGLE_OAUTH_CLIENT_ID"
        value = var.google_oauth_client_id # You will need to define this variable
      }
      env {
        name  = "GOOGLE_OAUTH_CLIENT_SECRET"
        value = var.google_oauth_client_secret # You will need to define this variable
                                               # and mark it as sensitive
      }
      env {
        name  = "FLASK_SECRET_KEY"
        value = var.flask_secret_key # Use the Terraform variable
      }
      
      env {
        name  = "FRONTEND_BASE_URL"
      value = var.frontend_base_url
      }

      resources {
        limits = {
          cpu    = "1000m"
          memory = "512Mi" // Adjust as needed
        }
      }
    }
    timeout = "60s" // Request timeout for Cloud Run service
    # execution_environment = "EXECUTION_ENVIRONMENT_GEN2" // Not needed if image is specified or built from source like this
  }
}

# To allow unauthenticated access (like GCF default HTTP):
resource "google_cloud_run_v2_service_iam_member" "allow_unauthenticated" {
  project  = google_cloud_run_v2_service.archiemcp_service.project
  location = google_cloud_run_v2_service.archiemcp_service.location
  name     = google_cloud_run_v2_service.archiemcp_service.name
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# --- Enable Necessary APIs ---
# (These ensure the APIs are active, good practice to keep them declared)
resource "google_project_service" "cloudfunctions" {
  project                    = var.project_id
  service                    = "cloudfunctions.googleapis.com"
  disable_dependent_services = false # Keep true if you want to manage dependencies explicitly
  disable_on_destroy         = true # Keep true if you want them to stay enabled after destroy
}

resource "google_project_service" "run" {
  project                    = var.project_id
  service                    = "run.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "artifactregistry" {
  project                    = var.project_id
  service                    = "artifactregistry.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "cloudbuild" {
  project                    = var.project_id
  service                    = "cloudbuild.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "aiplatform" {
  project                    = var.project_id
  service                    = "aiplatform.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_service" "iam" { # Identity and Access Management API
  project                    = var.project_id
  service                    = "iam.googleapis.com"
  disable_dependent_services = false
  disable_on_destroy         = false
}

resource "google_project_iam_member" "function_sa_aiplatform_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = google_service_account.archiemcp_function_sa.member
}

resource "google_project_iam_member" "function_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = google_service_account.archiemcp_function_sa.member
}

resource "google_service_account_iam_member" "gha_can_act_as_function_sa" {
  service_account_id = google_service_account.archiemcp_function_sa.name 
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.deployer_service_account_email}" 
}

variable "mcp_service_account_email" {
  description = "The email of the MCP service account that needs to act as the function SA. Ensure this SA exists."
  type        = string
}

resource "google_service_account_iam_member" "mcp_sa_can_act_as_function_sa" {
  service_account_id = google_service_account.archiemcp_function_sa.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${var.mcp_service_account_email}"
}

resource "google_storage_bucket_iam_member" "function_sa_can_write_to_bucket" { # Renamed for clarity
  bucket = google_storage_bucket.archiemcp_bucket.name
  role   = "roles/storage.objectCreator" # Corrected role
  member = google_service_account.archiemcp_function_sa.member
}

resource "google_project_iam_member" "function_build_sa_project_storage_viewer" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = google_service_account.archiemcp_function_sa.member
}

resource "google_project_iam_member" "function_build_sa_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer" // Allows reading and writing to any AR repo in the project
  member  = google_service_account.archiemcp_function_sa.member
}

resource "google_storage_bucket" "archiemcp_bucket" {
  name                        = var.storage_bucket
  project                     = var.project_id
  location                    = var.region

  uniform_bucket_level_access = true
  force_destroy               = true # OK for dev, use with caution in prod
}


resource "google_storage_bucket_iam_member" "public_website_viewer" {
  bucket = google_storage_bucket.archiemcp_bucket.name // Uses the name of your existing bucket
  role   = "roles/storage.objectViewer"
  member = "allUsers"
}

# --- Variables for OAuth ---
variable "google_oauth_client_id" {
  description = "The Google OAuth 2.0 Client ID for web application authentication (obtained from GCP Console)."
  type        = string
  sensitive   = true # Mark as sensitive to prevent output in logs
}

variable "google_oauth_client_secret" {
  description = "The Google OAuth 2.0 Client Secret for web application authentication (obtained from GCP Console)."
  type        = string
  sensitive   = true # Mark as sensitive to prevent output in logs
}