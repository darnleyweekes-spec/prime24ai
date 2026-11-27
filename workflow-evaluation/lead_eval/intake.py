"""Provider contract: extract facts once, then apply the intake policy locally."""
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


def prepare(text):
    facts = IntakeFacts.model_validate_json(text)
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
