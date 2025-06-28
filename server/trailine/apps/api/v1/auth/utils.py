import random
import string
import base64


def generate_verification_code() -> str:
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choices(characters, k=6))


def get_verify_cache_key(purpose: str, email: str) -> str:
    encoded_email = base64.b64encode(email.encode()).decode()
    return f"verify:email:{purpose}:{encoded_email}"
