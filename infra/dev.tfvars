environment         = "dev"
project_id          = "archie-458607"
location            = "europe-west6"
region              = "europe-west6"
tf_state_bucket     = "terraform-state-dev-851493899554"
storage_bucket      = "archiemcp-dev"
cloudfunction       = "archiefunct-dev"

// New variables for ArchieMCP function (defaults are in variables.tf, override here if needed)
archiemcp_function_entry_point          = "app" # Corrected entrypoint
archiemcp_function_runtime              = "python311"
archiemcp_function_source_dir           = "../functions/archiemcp"
archiemcp_gemini_model_id               = "gemini-2.0-flash-001"
archiemcp_function_memory_mb            = 512
archiemcp_function_timeout_seconds      = 180
archiemcp_sa_id_suffix = "sa"