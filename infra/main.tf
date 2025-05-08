
resource "google_storage_bucket" "archiemcp_bucket" {
  name                        = var.storage_bucket
  project                     = var.project_id
  location                    = var.location
  uniform_bucket_level_access = true
}

data "archive_file" "default" {
  type        = "zip"
  output_path = "/tmp/function-source.zip"
  source_dir  = "../function"
}

#### Create Storage bucked object ####
resource "google_storage_bucket_object" "function" {
  name   = "function-source.zip"
  bucket = google_storage_bucket.archiemcp_bucket.name
  source = data.archive_file.default.output_path
}

resource "google_cloudfunctions2_function" "archiefunct" {
  name        = var.cloudfunction
  project     = var.project_id
  location    = var.location
  description = "A function to process Pub/Sub events"

  build_config {
    runtime     = "python311"
    entry_point = "main"
    source {
        storage_source {
          bucket = google_storage_bucket.archiemcp_bucket.name
          object = google_storage_bucket_object.function.name
        }
    }
  }
  
  service_config {
    max_instance_count = 3
    available_memory   = "256M"
    environment_variables = {
      PROJECT_ID = var.project_id
      LOCATION   = var.location
      ZONE       = var.zone_a
    }
  }
}

resource "google_project_iam_member" "cloud_function_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "allUsers"
}
