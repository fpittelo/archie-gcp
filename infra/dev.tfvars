environment         = "dev"
project_id          = "archie-458607"
location            = "europe-west6"
region              = "europe-west6"
tf_state_bucket     = "terraform-state-dev-851493899554"
storage_bucket      = "archiemcp-dev"
cloudfunction       = "archiefunct-dev"
archiefunct_image_uri = "europe-west6-docker.pkg.dev/archie-458607/archie-backend:${{ github.sha }}" # Replace with actual SHA if known