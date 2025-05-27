###### Project Variables ######

variable "project_id" {
    description = "The GCP project ID"
    type        = string
}

#variable "location" {
# description = "Resource location"
# type        = string
#}

variable "storage_bucket" {
  description = "The name of the GCS bucket for general storage (e.g., function source)."
  type        = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}
variable "environment" {
  description = "The deployment environment (e.g., dev, staging, prod)."
  type        = string
}

variable "cloudfunction" {
  description = "Base name for the Cloud Function/Run service and related resources."
  type        = string
}

variable "github_workspace" {
  description = "The value of the GITHUB_WORKSPACE environment variable."
  type        = string
}
variable "github_sha" {
  description = "The GitHub commit SHA, used for tagging or versioning."
  type        = string
}

variable "deployer_service_account_email" {
  description = "The email of the service account used by GitHub Actions to deploy resources."
  type        = string
}

variable "archie_mcp_image_uri" {
  description = "The URI of the Docker image for the archie-mcp service from Artifact Registry."
  type        = string
}

variable "gemini_model_name" {
  description = "The name of the Gemini model to be used."
  type        = string
}

variable "upload_frontend_files" {
  description = "Whether to upload frontend files via Terraform. Set to false if a later step (e.g., in CI/CD) handles frontend file uploads after placeholder replacement."
  type        = bool
  default     = true
}

variable "flask_secret_key" {
  description = "A strong secret key for Flask session management, passed from GitHub Actions secrets."
  type        = string
  sensitive   = true # Important: Marks this as sensitive
}