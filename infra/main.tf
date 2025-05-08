
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
  bucket = var.storage_bucket
  source = data.archive_file.default.output_path
}

resource "google_cloudfunctions_function" "archiefunct" {
  name        = var.cloudfunction
  project     = var.project_id
  description = "A function to process Pub/Sub events"
  runtime     = "python311"

}

resource "google_project_iam_member" "cloud_function_invoker" {
  project = var.project_id
  role    = "roles/cloudfunctions.invoker"
  member  = "allUsers"
}
