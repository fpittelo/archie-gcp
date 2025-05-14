
resource "google_storage_bucket" "archiemcp_bucket" {
  name                        = var.storage_bucket
  project                     = var.project_id
  location                    = var.location
  
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_service_account" "archiemcp_function_sa" {
  account_id = "${var.cloudfunction}-mcp-${var.archiemcp_sa_id_suffix}"
  display_name = "Service Account for ArchieMCP Function (${var.environment})" # Corrected typo
  project      = var.project_id
}

# IAM binding: Allow ArchieMCP SA to use Vertex AI (Gemini)
resource "google_project_iam_member" "archiemcp_sa_vertex_ai_user" {
  project = var.project_id
  role    = "roles/aiplatform.user"
  member  = "serviceAccount:${google_service_account.archiemcp_function_sa.email}"
}

# IAM binding: Allow ArchieMCP SA to write logs
resource "google_project_iam_member" "archiemcp_sa_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.archiemcp_function_sa.email}"
}

locals {
    archiemcp_source_dir = "${path.module}/../functions/archiemcp"
}

# Archive the Cloud Function source code
data "archive_file" "archiemcp_function_source_zip" {
  type        = "zip"
  source_dir  = local.archiemcp_source_dir # e.g., ../../functions/archiemcp
  output_path = "$${path.get_temp_dir()}/${var.cloudfunction}-mcp-source.zip"
}

# GCS Bucket to store the ArchieMCP Cloud Function source code
resource "google_storage_bucket" "archiemcp_function_source_bucket" {
  # Bucket names must be globally unique. Incorporate project_id and environment for uniqueness.
  name                        = "${var.cloudfunction}-mcp-src-${var.project_id}"
  project                     = var.project_id
  location                    = var.region # Functions are regional, so source bucket can be regional.
  uniform_bucket_level_access = true
  force_destroy               = true # IMPORTANT: Allows deletion of the bucket even if it contains objects during terraform destroy.
}

# Upload the zipped ArchieMCP function code to GCS
resource "google_storage_bucket_object" "archiemcp_function_source_archive" {
  name   = "${var.cloudfunction}-mcp-source-v${data.archive_file.archiemcp_function_source_zip.output_sha}.zip"
  bucket = google_storage_bucket.archiemcp_function_source_bucket.name
  source = data.archive_file.archiemcp_function_source_zip.output_path # Path to the zipped file
}

# ArchieMCP Cloud Function (2nd Gen)
resource "google_cloudfunctions2_function" "archiemcp_function" {
  name        = var.cloudfunction # e.g., "archiefunct-dev" (This is the primary ID for the function)
  location    = var.region
  project     = var.project_id
  description = "ArchieMCP: Proxies requests to Gemini API (${var.environment} environment)"

  build_config {
    runtime     = var.archiemcp_function_runtime
    entry_point = var.archiemcp_function_entry_point # e.g., "archiemcp"
    environment_variables = {
      "GCP_PROJECT"    = var.project_id
      "GCP_REGION"     = var.region # Function's region
      "GEMINI_MODEL"   = var.archiemcp_gemini_model_id
      "ENVIRONMENT"    = var.environment
    }
    source {
      storage_source {
        bucket = google_storage_bucket.archiemcp_function_source_bucket.name
        object = google_storage_bucket_object.archiemcp_function_source_archive.name
      }
    }
  }

  service_config {
    max_instance_count    = 2
    min_instance_count    = 1
    available_memory      = "512M"
    timeout_seconds       = var.archiemcp_function_timeout_seconds
    service_account_email = google_service_account.archiemcp_function_sa.email
    all_traffic_on_latest_revision = true
    ingress_settings               = "ALLOW_ALL" # Allows public invocation. Secure this for production.
  }

  # Explicitly depend on API services being enabled
  depends_on = [
    google_project_service.cloudfunctions,
    google_project_service.run,
    google_project_service.aiplatform,
    google_project_service.artifactregistry,
    google_project_service.cloudbuild,
    google_project_iam_member.archiemcp_sa_vertex_ai_user # Ensure SA permissions are set before function creation
  ]
}

# IAM: Allow public invocation of the ArchieMCP Cloud Function
# WARNING: For production, restrict this to authenticated users or specific services.
resource "google_cloudfunctions2_function_iam_member" "archiemcp_invoker_public" {
  project        = google_cloudfunctions2_function.archiemcp_function.project
  location       = google_cloudfunctions2_function.archiemcp_function.location
  cloud_function = google_cloudfunctions2_function.archiemcp_function.name
  role           = "roles/run.invoker" # For Cloud Functions 2nd gen
  member         = "allUsers"
}

# --- Enable Necessary APIs ---
# (These ensure the APIs are active, good practice to keep them declared)
resource "google_project_service" "cloudfunctions" {
  project                    = var.project_id
  service                    = "cloudfunctions.googleapis.com"
  disable_dependent_services = false # Keep true if you want to manage dependencies explicitly
  disable_on_destroy         = false # Keep true if you want them to stay enabled after destroy
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
