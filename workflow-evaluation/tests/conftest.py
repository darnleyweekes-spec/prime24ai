import json
import pytest
from lead_eval.client import FixtureClient
from lead_eval.config import Settings
from lead_eval.db import Database
from lead_eval.evaluation import load_cases
from lead_eval.workflow import Workflow


@pytest.fixture
def db(tmp_path): return Database(tmp_path/'test.sqlite')

@pytest.fixture
def cases(): return load_cases()

@pytest.fixture
def workflow(db): return Workflow(db,FixtureClient(),Settings(),sleep=lambda _:None)
