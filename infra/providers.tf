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
  # Backend configuration is now dynamically set in the workflow
  # Remove the hardcoded backend block
}
provider "google" {
  project = "archie-458607"
  region  = "europe-west6"
}