import json
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from django.conf import settings


class AIServiceError(Exception):
    """Raised when the AI provider cannot return valid product details."""


def generate_product_details(name: str, category: str) -> tuple[str, Decimal]:
    """Generate a concise product description and a positive suggested price."""
    endpoint = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": settings.OLLAMA_MODEL,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are an e-commerce merchandising assistant. Suggest a "
                    "professional, factual product description and a reasonable "
                    "price in Indian rupees (INR). Never invent specific product features not "
                    "provided. Return only a JSON object with a non-empty "
                    '"description" string and a positive numeric "price" in INR.'
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Product name: {name}\n"
                    f"Category: {category}\n"
                    "Provide a concise description and a suitable price in INR."
                ),
            },
        ],
    }
    request = Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=120) as response:
            response_body = response.read()
    except HTTPError as exc:
        if exc.code == 404:
            message = (
                f"Ollama model '{settings.OLLAMA_MODEL}' is not installed. "
                f"Run: ollama pull {settings.OLLAMA_MODEL}"
            )
        else:
            message = f"Ollama returned HTTP {exc.code}. Check the local Ollama service."
        raise AIServiceError(message) from exc
    except (URLError, OSError, TimeoutError) as exc:
        raise AIServiceError(
            "Could not connect to Ollama. Start Ollama and verify OLLAMA_BASE_URL."
        ) from exc

    try:
        result = json.loads(response_body.decode("utf-8"))
        content = result["message"]["content"]
        details = json.loads(content)
        description = details["description"].strip()
        price = Decimal(str(details["price"])).quantize(Decimal("0.01"))
    except (
        json.JSONDecodeError,
        KeyError,
        TypeError,
        AttributeError,
        InvalidOperation,
        UnicodeDecodeError,
    ) as exc:
        raise AIServiceError("Ollama returned invalid product details.") from exc

    if not description or not price.is_finite() or price <= 0 or price >= Decimal("100000000"):
        raise AIServiceError("Ollama returned invalid product details.")

    return description, price
