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

variable "github_workspace" {
  description = "The value of the GITHUB_WORKSPACE environment variable."
  type        = string
}

variable "github_sha" {
  type = string
}