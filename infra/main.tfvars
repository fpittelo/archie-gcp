environment         = "main"
project_id          = "archie-458607"
location            = "europe-west6"
region              = "europe-west6"
tf_state_bucket     = "terraform-state-main-851493899554"
storage_bucket      = "archiemcp-main"
cloudfunction       = "archiefunct-main"

// New variables for ArchieMCP function (defaults are in variables.tf, override here if needed)
archiemcp_function_entry_point          = "archiemcp-main"
archiemcp_function_runtime              = "python311"
archiemcp_function_source_dir           = "/home/runner/work/archie-gcp/archie-gcp/functions/archiemcp" # Absolute path
archiemcp_gemini_model_id               = "gemini-2.0-flash-001"
archiemcp_function_memory_mb            = 512
archiemcp_function_timeout_seconds      = 180
archiemcp_sa_id_suffix = "sa"