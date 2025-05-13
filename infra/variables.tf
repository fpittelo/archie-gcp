###### Project Variables ######

variable "project_id" {
    description = "The GCP project ID"
    type        = string
}

variable "location" {
  description = "Resource location"
  type        = string
}

variable "tf_state_bucket" {
  type = string
}

variable "storage_bucket" {
  type = string
}

variable "region" {
  description = "The GCP region"
  type        = string
}

variable "environment" {
 type = string 
}

variable "cloudfunction" {
  type = string
}

###### New Variables for ArchieMCP Cloud Function ######

variable "archiemcp_function_entry_point" {
  description = "The entry point (function name in Python code) for the ArchieMCP function."
  type        = string
  default     = "archiemcp"
}

variable "archiemcp_function_runtime" {
  description = "The runtime for the ArchieMCP Cloud Function."
  type        = string
  default     = "python311" # Consider python312 if available and tested
}

variable "archiemcp_function_source_dir" {
    description = "The directory containing the ArchieMCP function source code. Can be a relative or absolute path."
    type        = string
    default     = "../../functions/archiemcp"  # Or a sensible relative default
}

variable "archiemcp_gemini_model_id" {
  description = "The ID of the Gemini model to be used by the ArchieMCP function."
  type        = string
  default     = "gemini-1.0-pro-001" # Update as new models are released/preferred
}

variable "archiemcp_function_memory_mb" {
  description = "Memory allocated to the ArchieMCP function in MiB."
  type        = number
  default     = 512
}

variable "archiemcp_function_timeout_seconds" {
  description = "Timeout for the ArchieMCP function in seconds."
  type        = number
  default     = 120 # Gemini calls can take time
}

variable "archiemcp_sa_id_suffix" {
  description = "Suffix for the ArchieMCP service account ID (prefix will be function name)."
  type        = string
  default     = "sa" # Results in e.g., archiefunct-dev-sa
}