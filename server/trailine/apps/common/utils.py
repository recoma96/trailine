import base64


def get_verify_success_email_cache_key(email: str, purpose: str):
    encoded_email = base64.b64encode(email.encode()).decode()
    return f"verify:email:{purpose}:{encoded_email}:success"
