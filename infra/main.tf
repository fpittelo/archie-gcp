resource "google_service_account" "archiemcp_function_sa" {
  project      = var.project_id
  account_id   = "${var.cloudfunction}-sa"
  display_name = "Service Account for ArchieMCP Function"
}

# Cloud Run v2 Service resource
resource "google_cloud_run_v2_service" "archiemcp_service" {
  name     = var.cloudfunction // e.g., "archiefunct-dev"
  project  = var.project_id
  location = var.location 

  template {
    service_account = google_service_account.archiemcp_function_sa.email // Runtime SA
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" // Placeholder, will be replaced by source build
      ports {
        container_port = 8080
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

resource "google_storage_bucket" "archiemcp_bucket" {
  name                        = var.storage_bucket
  project                     = var.project_id
  location                    = var.location
  
  uniform_bucket_level_access = true
  force_destroy = true
}

resource "google_storage_bucket_object" "archiemcp_function_source" {
  name   = "function-source-${data.archive_file.function_source.output_md5}.zip"
  bucket = google_storage_bucket.archiemcp_bucket.name
  source = data.archive_file.function_source.output_path
  # Setting content_type is necessary to prevent issues with Google Cloud Functions deployments
  content_type = "application/zip"
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

data "archive_file" "function_source" {
  type        = "zip"
  output_path = "${path.module}/tmp/function_source.zip"
  source_dir  = "${var.github_workspace}/functions/archiemcp"
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

resource "google_storage_bucket_iam_member" "function_sa_can_read_source_bucket" {
  bucket = google_storage_bucket.archiemcp_bucket.name // This is your "archiemcp-dev" bucket
  role   = "roles/storage.objectViewer"
  member = google_service_account.archiemcp_function_sa.member // Grants permission to "archiefunct-dev-sa@..."
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