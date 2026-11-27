"""Provider contract: extract facts once, then apply the intake policy locally."""
import re

from pydantic import BaseModel, ConfigDict, Field, field_validator
from .schema import LeadOutput, Service, Urgency


class IntakeFacts(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    contact_name: str | None = Field(max_length=120)
    email: str | None = Field(max_length=254)
    phone: str | None = Field(max_length=40)
    location: str | None = Field(max_length=240)
    service: Service
    urgency: Urgency
    ambiguous: bool

    @field_validator('contact_name', 'email', 'phone', 'location')
    @classmethod
    def clean_optional(cls, value):
        return (value.strip() or None) if value is not None else None


# Conservative English evidence rules for this four-service intake prototype.
SERVICE_TERMS = {
    'plumbing': r'plumb(?:er|ing)?|pipes?|drains?|faucets?|toilets?|leak(?:s|ing)?',
    'electrical': r'electric(?:al|ian)?|wir(?:e|es|ing)|outlets?|sockets?|sparks?|breakers?',
    'hvac': r'hvac|air condition(?:er|ing)|heating|furnace|heat pump|thermostat',
    'cleaning': r'clean(?:er|ers|ing)?|housekeeping|janitorial',
}
URGENT_TERMS = r'urgent(?:ly)?|emergency|immediate(?:ly)?|today|asap|right now|sparks?|active leak|burst pipe'


def prepare(text, inquiry):
    facts = IntakeFacts.model_validate_json(text)
    if facts.service in SERVICE_TERMS and not re.search(
        rf'\b(?:{SERVICE_TERMS[facts.service]})\b', inquiry, re.I
    ):
        facts.service = 'unclear'
    if facts.urgency == 'urgent' and not re.search(rf'\b(?:{URGENT_TERMS})\b', inquiry, re.I):
        facts.urgency = 'unknown'
    # Recover a phone specifically in an email/phone contact list. Avoid guessing
    # which number to use when several candidates occur in the message.
    phone_pattern = r'(?<!\w)(?:\+?1[ .-])?(?:\(\d{3}\)|\d{3})[ .-]\d{3}[ .-]\d{4}(?!\w)'
    phones = re.findall(phone_pattern, inquiry)
    if facts.phone is None and facts.email and len(phones) == 1:
        pair = re.escape(facts.email) + r'\s*[,;|]\s*' + re.escape(phones[0])
        if re.search(pair, inquiry, re.I):
            facts.phone = phones[0]
    absent = {
        'contact_name': facts.contact_name is None,
        'contact_method': facts.email is None and facts.phone is None,
        'location': facts.location is None,
        'service': facts.service == 'unclear',
        'urgency': facts.urgency == 'unknown',
    }
    questions = {
        'contact_name': 'What is your name?',
        'contact_method': 'Which email or phone number should we use?',
        'location': 'What is the service address?',
        'service': 'Which service do you need?',
        'urgency': 'How soon do you need help?',
    }
    missing = [field for field, needed in absent.items() if needed]
    greeting = f'Hello {facts.contact_name},' if facts.contact_name else 'Hello,'
    subject = facts.service if facts.service != 'unclear' else 'service'
    parts = [greeting, f'Thank you for your {subject} inquiry.']
    parts.extend(questions[field] for field in missing)
    if facts.ambiguous and not missing:
        parts.append('Could you clarify the details of your request?')
    parts.append('Our staff will review your request.')
    if facts.urgency == 'urgent':
        parts.append('If there is immediate danger, contact local emergency services.')
    fields = facts.model_dump()
    fields['ambiguous'] |= facts.service == 'unclear'
    return LeadOutput(**fields, missing_information=missing, draft_response=' '.join(parts))
