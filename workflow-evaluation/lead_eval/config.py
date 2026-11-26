import math
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    model: str = 'gpt-4.1-mini'
    timeout_seconds: float = 20.0
    max_retries: int = 2
    backoff_seconds: float = 0.1
    input_usd_per_million: float = 0.40
    output_usd_per_million: float = 1.60

    def __post_init__(self):
        if not 0 < self.timeout_seconds <= 120 or not 0 <= self.max_retries <= 2 or not 0 <= self.backoff_seconds <= 2:
            raise ValueError('Timeout/retry bounds exceeded')
        for rate in [self.input_usd_per_million, self.output_usd_per_million]:
            if not math.isfinite(rate) or rate < 0:
                raise ValueError('Pricing rates must be finite and nonnegative')

    @classmethod
    def from_env(cls):
        return cls(model=os.getenv('OPENAI_MODEL', 'gpt-4.1-mini'),
                   timeout_seconds=float(os.getenv('API_TIMEOUT_SECONDS', '20')),
                   input_usd_per_million=float(os.getenv('INPUT_USD_PER_MILLION', '.40')),
                   output_usd_per_million=float(os.getenv('OUTPUT_USD_PER_MILLION', '1.60')))
