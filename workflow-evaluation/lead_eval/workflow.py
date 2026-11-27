import hashlib
import re
import time
import unicodedata
from pydantic import ValidationError
from .client import APIError, ModelClient
from .config import Settings
from .db import Database
from .guards import QUESTIONS, draft_checks
from .schema import LeadOutput, normalize, validate_grounding


def fingerprint(inquiry: str) -> str:
    canonical = re.sub(r'[^\w]+', ' ', normalize(inquiry), flags=re.UNICODE).strip()
    return hashlib.sha256(canonical.encode()).hexdigest()


def valid_input(inquiry) -> bool:
    return (isinstance(inquiry, str) and 10 <= len(inquiry.strip()) <= 4000
            and bool(re.search(r'\w', inquiry))
            and all(unicodedata.category(c) != 'Cc' or c in '\t\n\r' for c in inquiry))


class Workflow:
    def __init__(self, db: Database, client: ModelClient, settings=None, *, sleep=time.sleep):
        self.db, self.client = db, client
        self.settings, self.sleep = settings or Settings(), sleep

    def process(self, inquiry, *, scope='manual:fixture') -> dict:
        started = time.perf_counter()
        valid = valid_input(inquiry)
        # Invalid content is not retained; all other inputs in this demo must be fictional.
        stored = inquiry.strip() if valid else '[invalid input omitted]'
        id, duplicate_of = self.db.claim(stored, scope, fingerprint(stored) if valid else None,
                                         self.client.mode, status='processing' if valid else 'invalid')
        result = dict(id=id, mode=self.client.mode, status='processing', duplicate_of=duplicate_of,
                      extraction=None, error_code=None, error_details=None, attempts=[], retries=0,
                      input_tokens=None, output_tokens=None, usage_complete=None, estimated_cost_usd=None,
                      response_ms=None, requested_model=self.settings.model if self.client.mode == 'live' else None,
                      actual_model=None)
        if not valid:
            result.update(status='invalid', error_code='invalid_input', error_details='Use 10–4000 text characters without control characters.')
        elif duplicate_of:
            result['status'] = 'duplicate'
        else:
            input_tokens, output_tokens = 0, 0
            known_input = known_output = 0
            usage_missing = False
            for attempt in range(1, self.settings.max_retries + 2):
                attempt_start = time.perf_counter()
                entry = dict(attempt=attempt, error_code=None, elapsed_ms=None, input_tokens=None, output_tokens=None)
                transient = False
                try:
                    reply = self.client.complete(stored)
                    result['actual_model'] = reply.model
                    entry.update(input_tokens=reply.input_tokens, output_tokens=reply.output_tokens)
                    if reply.input_tokens is not None:
                        input_tokens += reply.input_tokens
                        known_input += 1
                    if reply.output_tokens is not None:
                        output_tokens += reply.output_tokens
                        known_output += 1
                    usage_missing |= reply.input_tokens is None or reply.output_tokens is None
                    decode = getattr(self.client, "decode", LeadOutput.model_validate_json)
                    output = decode(reply.text)
                    validate_grounding(output, stored)
                    checks = draft_checks(output.draft_response, [QUESTIONS[f] for f in output.missing_information])
                    if not all(checks.values()):
                        raise ValueError('Draft guardrail failure: ' + ', '.join(k for k,v in checks.items() if not v))
                    result.update(status='pending_approval', extraction=output.model_dump())
                except APIError as exc:
                    entry['error_code'] = exc.code
                    transient = exc.transient
                    # Usage on unsuccessful transport/status calls is unknown, never assumed free.
                    usage_missing = True
                    result.update(error_code=exc.code, error_details='Model API call failed; see attempt log.')
                except ValidationError as exc:
                    entry['error_code'] = 'malformed_output'
                    # Do not retain Pydantic's input values; store locations and error types.
                    detail = [{'field':[part if isinstance(part, int) or part in LeadOutput.model_fields else '<unknown>' for part in e['loc']], 'type':e['type']} for e in exc.errors(include_input=False, include_context=False)]
                    result.update(error_code='malformed_output', error_details=detail)
                except ValueError as exc:
                    entry['error_code'] = 'output_guardrail'
                    # ValueError text here is authored by local guards, never raw API content.
                    result.update(error_code='output_guardrail', error_details=str(exc))
                entry['elapsed_ms'] = (time.perf_counter()-attempt_start)*1000
                result['attempts'].append(entry)
                result['retries'] = attempt - 1
                if result['status'] == 'pending_approval':
                    result.update(error_code=None, error_details=None)
                    break
                result['status'] = 'error'
                if not transient or attempt > self.settings.max_retries:
                    break
                self.sleep(min(self.settings.backoff_seconds * 2**(attempt-1), 2))
            if self.client.mode == 'live':
                result['input_tokens'] = input_tokens if known_input else None
                result['output_tokens'] = output_tokens if known_output else None
                result['usage_complete'] = not usage_missing
                if known_input and known_output:
                    result['estimated_cost_usd'] = (input_tokens*self.settings.input_usd_per_million + output_tokens*self.settings.output_usd_per_million)/1_000_000
        result['response_ms'] = (time.perf_counter()-started)*1000
        self.db.finish(result)
        # Include final result persistence in the measured workflow elapsed time.
        result['response_ms'] = (time.perf_counter()-started)*1000
        self.db.finish(result)
        return result
