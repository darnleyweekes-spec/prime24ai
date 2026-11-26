"""Local adapter for alpha.js assessment fields. Never opens Gmail."""

def assessment_to_inquiry(fields: dict) -> str:
    allowed = {'name', 'email', 'company', 'workflow', 'service'}
    if set(fields) - allowed or any(not isinstance(v, str) or len(v) > 3000 for v in fields.values()):
        raise ValueError('Expected Prime24AI assessment text fields')
    # Preserve supplied values; the model, schema and grounding handle uncertainty.
    labels = {'name': 'I am', 'email': 'Email', 'company': 'Company',
              'workflow': 'Customer inquiry', 'service': 'Prime24AI offer selected'}
    return '\n'.join(f'{labels[k]}: {fields[k].strip()}' for k in labels if fields.get(k, '').strip())
