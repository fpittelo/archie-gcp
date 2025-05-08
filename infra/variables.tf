###### Project Variables ######

variable "project_id" {
    description = "The GCP project ID"
    type        = string
}

variable "location" {
  description = "Resource location"
  type        = string
}

variable "zone_a" {
  description = "Resource location"
  type        = string
}

variable "zone_b" {
  description = "Resource location"
  type        = string
}

variable "zone_C" {
  description = "Resource location"
  type        = string
}

variable "tf_state_bucket" {
  type = string
}

variable "storage_bucket" {
  type = string
}

variable "cloudfunction" {
  type = string
}
