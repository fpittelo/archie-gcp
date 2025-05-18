terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.32.0"
    }
    hashicorp = {
      source  = "hashicorp/http"
      version = "~> 3.5.0"
    }
  }
  backend "gcs" {
    bucket = "terraform-state-851493899554"
    prefix = "backend"
    use_oidc = true
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}