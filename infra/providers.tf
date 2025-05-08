terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.20.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.20.0"
    }
    http = {
      source  = "terraform-aws-modules/http"
      version = "~> 2.0"
    }
  }

  backend "gcs" {
    bucket = var.tf_state_bucket
    prefix = "terraform/state"
  }
}

provider "google" {
  project = var.project_id
  region  = var.location
}

provider "google-beta" {
  project = var.project_id
  region  = var.location
}

variable "tf_state_bucket" {
  type = string
}