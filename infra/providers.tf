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
    # The 'bucket' and 'prefix' are configured dynamically during 'terraform init'
    # in the CI/CD pipeline using -backend-config arguments.
    # bucket = "will-be-set-by-ci"
    # prefix = "will-be-set-by-ci"
    use_oidc = true
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}