"""Deterministic draft guardrails; staff semantic review is still required."""
import re
from .schema import normalize

QUESTIONS = {
    'contact_name': 'your name',
    'contact_method': 'email or phone',
    'service': 'which service',
    'location': 'service address',
    'urgency': 'how soon',
}


def draft_checks(draft: str, required: list[str]) -> dict[str, bool]:
    text = normalize(draft)
    checks = {f'contains:{term}': normalize(term) in text for term in required}
    checks['staff_review_notice'] = 'staff will review' in text
    checks['no_links_or_prices'] = re.search(r'https?://|www\.|\$\s*\d|\b\d+\s*(?:usd|dollars)\b', text) is None
    checks['no_action_claims'] = re.search(r'\b(?:sent|booked|scheduled|approved|confirmed appointment)\b|\b(?:we|i)\s+(?:will|can)\s+(?:arrive|attend|visit)', text) is None
    return checks
