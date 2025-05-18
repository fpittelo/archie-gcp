
resource "google_storage_bucket" "archiemcp_bucket" {
  name                        = var.storage_bucket
  project                     = var.project_id
  location                    = var.location
  
  uniform_bucket_level_access = true
  force_destroy = true
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
