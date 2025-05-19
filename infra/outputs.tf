output "archiemcp_service_uri" { // Renamed for clarity from archiemcp_function_uri
  description = "The HTTPS URI of the deployed ArchieMCP Cloud Run service."
  value       = google_cloud_run_v2_service.archiemcp_service.uri // Corrected to reference the Cloud Run service
  sensitive   = false
}

output "archiemcp_service_account_email" { // Optionally rename for consistency, e.g., archiemcp_cloud_run_sa_email
  description = "Email of the service account used by the ArchieMCP Cloud Run service." // Updated description
  value       = google_service_account.archiemcp_function_sa.email
}