terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.32.0"
    }
    http = {
      source  = "terraform-aws-modules/http"
      version = "~> 2.0"
    }
  }
  backend "gcs" {
    bucket = var.tf_state_bucket
    prefix = "terraform-state"
  }
}
provider "google" {
  project = var.project_id
  region  = var.location
}