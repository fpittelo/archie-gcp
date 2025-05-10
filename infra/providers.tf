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
    bucket = "terraform-state-851493899554"
    prefix = "backend"
    use_oidc = true
  }
}
provider "google" {
  project = "archie-458607"
  region  = "europe-west6"
}