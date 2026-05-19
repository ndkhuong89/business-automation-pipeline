import re

ORDER_KEYWORDS = [
    "order", "purchase", "invoice", "payment", "buy", "request order"
]

IGNORE_KEYWORDS = [
    "unsubscribe", "promotion", "marketing", "newsletter"
]


def classify_email(subject, sender, body):
    text = f"{subject} {sender} {body}".lower()

    if any(k in text for k in IGNORE_KEYWORDS):
        return "IGNORE"

    if any(k in text for k in ORDER_KEYWORDS):
        return "ORDER"

    return "UNKNOWN"