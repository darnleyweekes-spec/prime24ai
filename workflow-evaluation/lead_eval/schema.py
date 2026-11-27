import re
import unicodedata
from typing import Literal
from pydantic_core import PydanticCustomError
from pydantic import BaseModel, ConfigDict, Field, model_validator

Service = Literal['plumbing', 'electrical', 'hvac', 'cleaning', 'unclear']
Urgency = Literal['urgent', 'soon', 'routine', 'unknown']
MissingField = Literal['contact_name', 'contact_method', 'service', 'location', 'urgency']


def normalize(value: str) -> str:
    return ' '.join(unicodedata.normalize('NFKC', value).casefold().split())


class LeadOutput(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    contact_name: str | None = Field(max_length=120)
    email: str | None = Field(max_length=254)
    phone: str | None = Field(max_length=40)
    service: Service
    location: str | None = Field(max_length=240)
    urgency: Urgency
    missing_information: list[MissingField] = Field(max_length=5)
    ambiguous: bool
    draft_response: str = Field(min_length=20, max_length=2000)

    @model_validator(mode='after')
    def consistent(self):
        for value in [self.contact_name, self.email, self.phone, self.location]:
            if value is not None and (not value.strip() or any(unicodedata.category(c) == 'Cc' for c in value)):
                raise PydanticCustomError('blank_or_control_character', 'Contact fields must be nonempty and have no controls')
        if self.email is not None and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', self.email):
            raise PydanticCustomError('email_format', 'Invalid email')
        if self.phone is not None and not 7 <= len(re.sub(r'\D', '', self.phone)) <= 15:
            raise PydanticCustomError('phone_digit_count', 'Invalid phone')
        missing = set()
        if self.contact_name is None: missing.add('contact_name')
        if self.email is None and self.phone is None: missing.add('contact_method')
        if self.service == 'unclear': missing.add('service')
        if self.location is None: missing.add('location')
        if self.urgency == 'unknown': missing.add('urgency')
        if len(set(self.missing_information)) != len(self.missing_information) or set(self.missing_information) != missing:
            raise PydanticCustomError('missing_information_inconsistent', 'Missing information must agree with extracted fields')
        if self.service == 'unclear' and not self.ambiguous:
            raise PydanticCustomError('unclear_service_requires_ambiguity', 'Unclear service requires ambiguity')
        return self


def validate_grounding(output: LeadOutput, inquiry: str) -> None:
    for field in ['contact_name', 'email', 'phone', 'location']:
        value = getattr(output, field)
        if value is not None:
            candidate, source = normalize(value), normalize(inquiry)
            if field == 'phone':
                candidate, source = re.sub(r'\D', '', candidate), re.sub(r'\D', '', source)
            if candidate not in source:
                raise ValueError(f'{field} is not grounded in the inquiry')
