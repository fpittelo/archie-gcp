output "archiemcp_function_uri" {
  description = "The HTTPS URI of the deployed ArchieMCP Cloud Function."
  value       = google_cloudfunctions2_function.archiemcp_function.uri
  sensitive   = false # URIs are generally not sensitive but can be if they imply internal structure
}

output "archiemcp_function_service_account_email" {
  description = "Email of the service account used by the ArchieMCP function."
  value       = google_service_account.archiemcp_function_sa.email
}