# Model name mappings - short names to full IDs
MODEL_MAPPING = {
    "haiku": "haiku",
    "sonnet": "sonnet",
    "opus": "opus",

}

def get_model_id(model_name: str) -> str:
    """Get the full model ID from a short name."""
    return MODEL_MAPPING.get(model_name, model_name)