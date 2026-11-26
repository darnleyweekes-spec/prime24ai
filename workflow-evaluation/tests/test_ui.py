from pathlib import Path
from streamlit.testing.v1 import AppTest
from lead_eval.db import Database

ROOT=Path(__file__).resolve().parents[1]


def click(at,label):
    next(b for b in at.button if b.label==label).click().run(timeout=20)
    assert not at.exception


def test_streamlit_evaluation_and_staff_review(monkeypatch,tmp_path):
    monkeypatch.chdir(ROOT)
    path=tmp_path/'ui.sqlite'
    monkeypatch.setenv('DATABASE_PATH',str(path))
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    at=AppTest.from_file(str(ROOT/'app.py')).run(timeout=20)
    assert not at.exception
    click(at,'Run 30-case fixture evaluation')
    assert any(m.label=='Cases passed / evaluated' and m.value=='30 / 30' for m in at.metric)
    click(at,'Process inquiry')
    assert Database(path).list_inquiries()[0]['status']=='pending_approval'
    next(t for t in at.text_input if t.label=='Staff identifier').set_value('UI Reviewer')
    next(c for c in at.checkbox if c.label=='I have reviewed this exact draft and approve it locally').check()
    click(at,'Mark response approved')
    assert Database(path).list_inquiries()[0]['status']=='approved'
    at.run(timeout=20)
    assert not at.exception
