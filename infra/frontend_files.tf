locals {
  # Define common MIME types. You can expand this map as needed.
  mime_types = {
    "html" = "text/html",
    "css"  = "text/css",
    "js"   = "application/javascript",
    "json" = "application/json",
    "png"  = "image/png",
    "jpg"  = "image/jpeg",
    "jpeg" = "image/jpeg",
    "gif"  = "image/gif",
    "svg"  = "image/svg+xml",
    "ico"  = "image/x-icon",
    "txt"  = "text/plain"
  }
}

resource "google_storage_bucket_object" "frontend_files" {
  for_each = var.upload_frontend_files ? fileset("${var.github_workspace}/frontend/", "**/*") : toset([]) # Get all files recursively
  name         = "frontend/${each.value}"                             # Destination path: frontend/path/to/file.ext
  bucket       = google_storage_bucket.archiemcp_bucket.name                                   # Bucket name from variables (e.g., dev.tfvars)
  source       = "${var.github_workspace}/frontend/${each.value}"     # Full path to the local source file
  content_type = lookup(local.mime_types, regex("\\.([^.]+)$", each.value)[0], "application/octet-stream") # Set Content-Type
}