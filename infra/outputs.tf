output "archiemcp_function_uri" {
  description = "The HTTPS URI of the deployed ArchieMCP Cloud Function."
  value       = google_cloudfunctions2_function.archiemcp_function.service_config[0].uri
  sensitive   = false # URIs are generally not sensitive but can be if they imply internal structure
}

output "archiemcp_function_service_account_email" {
  description = "Email of the service account used by the ArchieMCP function."
  value       = google_service_account.archiemcp_function_sa.email
}

output "archiemcp_function_source_code_bucket_name" {
  description = "Name of the GCS bucket storing the ArchieMCP function's source code."
  value       = google_storage_bucket.archiemcp_function_source_bucket.name
}