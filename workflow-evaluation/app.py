"""Streamlit presentation only; business logic lives in lead_eval/."""
from dataclasses import replace
import json
import os
from pathlib import Path
import pandas as pd
import streamlit as st
from lead_eval.client import FixtureClient, OpenAIClient
from lead_eval.config import Settings
from lead_eval.db import Database
from lead_eval.evaluation import evaluate, load_cases
from lead_eval.workflow import Workflow

st.set_page_config(page_title='Prime24AI Workflow Evaluation', layout='wide')
st.title('AI Workflow Evaluation Dashboard')
st.caption('Prime24AI portfolio prototype · Fictional inquiries · Local approval only · No messages are sent')
settings = Settings.from_env()
db = Database(os.getenv('DATABASE_PATH','data/dashboard.sqlite'))
cases = load_cases()
key_available = bool(os.getenv('OPENAI_API_KEY','').strip())


def percent(v): return f'{v:.1%}' if v is not None else 'N/A'
def ms(v): return f'{v:.2f} ms' if v is not None else 'N/A'


def show_result(result, context):
    st.write(f"Status: **{result['status']}** · Source: **{result['mode']}** · Retries: **{result['retries']}**")
    if result.get('duplicate_of'): st.info('Duplicate of local record '+result['duplicate_of'])
    if result.get('extraction'):
        extraction=result['extraction']
        st.json({k:v for k,v in extraction.items() if k!='draft_response'})
        st.text_area('Draft for staff review',extraction['draft_response'],height=160,disabled=True,key=context+'_draft_'+result['id'])
    if result.get('error_code'):
        st.error(result['error_code'])
        st.json(result.get('error_details'))
    if result['attempts']: st.dataframe(result['attempts'],hide_index=True,width='stretch')


benchmark, intake, approvals, method = st.tabs(['Evaluation dashboard','Process inquiry','Staff approval','Scoring and sources'])
with benchmark:
    st.warning('30 fictional cases test a bounded workflow. Fixture agreement does not measure live model quality or establish production reliability.')
    cols=st.columns(2)
    if cols[0].button('Run 30-case fixture evaluation',type='primary'):
        with st.spinner('Running fixture and separately labeled failure scenarios…'):
            report=evaluate(db,'fixture',settings)
        st.session_state['selected_run']=report['run_id']
        st.success('Fixture evaluation saved to SQLite. No model API calls made.')
    if cols[1].button('Run live evaluation (20 cases, one call each)',disabled=not key_available):
        with st.spinner('Evaluating live model; injected failures use a separate client…'):
            report=evaluate(db,'live',replace(settings,max_retries=0),live_interval=7)
        st.session_state['selected_run']=report['run_id']
    if not key_available: st.caption('Live evaluation unavailable: OPENAI_API_KEY is absent. Fixture mode is fully usable.')
    runs=db.runs()
    if not runs:
        st.info('Run the fixture evaluation to populate the dashboard and run history.')
    else:
        ids=[r['id'] for r in runs]
        wanted=st.session_state.get('selected_run',ids[0])
        run_id=st.selectbox('Saved evaluation run',ids,index=ids.index(wanted) if wanted in ids else 0,
                            format_func=lambda id: next(f"{r['mode'].upper()} · {r['started_at']} · {id[:8]}" for r in runs if r['id']==id))
        selected=next(r for r in runs if r['id']==run_id)
        rows=db.results(run_id)
        if not selected['summary_json']:
            st.warning(f'Incomplete run: {len(rows)}/30 cases persisted. Excluded from complete-run summaries.')
        else:
            summary=json.loads(selected['summary_json'])
            overall=summary['overall']
            a,b,c=st.columns(3)
            a.metric('Overall acceptance pass rate',percent(overall['pass_rate']))
            b.metric('Cases passed / evaluated',f"{overall['passed']} / {overall['n']}")
            c.metric('Simulated failure scenarios',summary['by_measurement']['simulated']['n'])
            st.caption('A case passes when the observed behavior matches its expected result. An expected, safely handled error can pass.')
            category_rows=[{'category':name,'passed':m['passed'],'n':m['n'],'pass_rate':m['pass_rate']} for name,m in summary['by_category'].items()]
            st.subheader('Acceptance by category')
            left,right=st.columns([1,1])
            left.bar_chart(pd.DataFrame(category_rows).set_index('category')[['pass_rate']],horizontal=True)
            right.dataframe(category_rows,hide_index=True,width='stretch')
            st.subheader('Measurements by source')
            st.caption('Sources remain separate. API latency below includes only cases with an attempted call; full workflow timing includes duplicate checks and SQLite writes. p95 uses nearest rank.')
            for source,m in summary['by_measurement'].items():
                if not m['n']: continue
                with st.expander(f"{source.upper()} · n={m['n']} · {m['passed']} passed",expanded=True):
                    c1,c2,c3=st.columns(3)
                    c1.metric('Extraction accuracy',percent(m['extraction_accuracy']))
                    c1.caption(f"{m['extraction_correct']}/{m['extraction_n']} field checks across {m['extraction_case_n']} extraction cases")
                    c2.metric('Median attempted-call workflow',ms(m['attempted_median_ms']))
                    c3.metric('p95 attempted-call workflow',ms(m['attempted_p95_ms']))
                    st.caption(f"Timing sample n={m['attempted_latency_n']}; full workflow n={m['workflow_latency_n']}, median {ms(m['workflow_median_ms'])}, p95 {ms(m['workflow_p95_ms'])}. Total retries: {m['retries']}.")
                    if source=='live':
                        st.write({'known_input_tokens':m['known_input_tokens'],'known_output_tokens':m['known_output_tokens'],
                                  'known_estimated_cost_usd':m['known_estimated_cost_usd'],
                                  'usage_reported_case_n':m['usage_reported_case_n'],'usage_complete_case_n':m['usage_complete_case_n'],
                                  'attempted_case_n':m['live_usage_case_n'],'cost_case_n':m['cost_case_n']})
                        if m['usage_complete_case_n'] < m['live_usage_case_n']:
                            st.warning('Usage is incomplete. Known token totals and cost estimates may exclude chargeable unsuccessful calls.')
                    else:
                        st.caption('Token usage and API cost: N/A. No live calls in this population. Timings measure local fixture/injection behavior only.')
            metadata=json.loads(selected['metadata_json'])
            rates=metadata['settings']
            st.caption(f"Stored pricing assumptions: input ${rates['input_usd_per_million']:.2f}, output ${rates['output_usd_per_million']:.2f} per million tokens. Estimate = (input × input rate + output × output rate) / 1,000,000. Verify current provider pricing before live use; no cached/batch discounts assumed.")
            available=[source for source,m in summary['by_measurement'].items() if m['n']]
            source=st.selectbox('Field accuracy source',available)
            st.dataframe([{'field':f,**m} for f,m in summary['by_measurement'][source]['fields'].items()],hide_index=True,width='stretch')
            st.subheader('Expected versus actual')
            category=st.selectbox('Case category',['all',*summary['by_category']])
            filtered=[r for r in rows if category=='all' or r['category']==category]
            st.dataframe([{'case':r['case_id'],'category':r['category'],'source':r['actual']['mode'],'passed':r['passed'],
                           'status':r['actual']['status'],'error':r['actual']['error_code'],'retries':r['actual']['retries'],
                           'response_ms':r['actual']['response_ms']} for r in filtered],hide_index=True,width='stretch')
            picked=st.selectbox('Inspect case',[r['case_id'] for r in filtered])
            detail=next(r for r in filtered if r['case_id']==picked)
            st.text(detail['inquiry'])
            st.dataframe([{'field':f, 'expected':json.dumps(v['expected']), 'actual':json.dumps(v['actual']), 'passed':v['passed']} for f,v in detail['fields'].items()],hide_index=True,width='stretch')
            if detail['runtime_checks']: st.json({'runtime_checks':detail['runtime_checks']})
            if detail['draft_checks']: st.json({'draft_checks':detail['draft_checks']})
            show_result(detail['actual'], 'evaluation')
            with st.expander('Run provenance and configuration'): st.json(metadata)
            export={'run_id':run_id,'mode':selected['mode'],'metadata':metadata,'summary':summary,'results':rows}
            st.download_button('Download evaluation JSON',json.dumps(export,indent=2),file_name=f'evaluation-{run_id[:8]}.json',mime='application/json')
        st.subheader('SQLite run history')
        history=[]
        for run in runs:
            agg=json.loads(run['summary_json'])['overall'] if run['summary_json'] else {}
            history.append({'run':run['id'],'source':run['mode'],'started_utc':run['started_at'],
                            'finished_utc':run['finished_at'],'n':agg.get('n'),'passed':agg.get('passed')})
        st.dataframe(history,hide_index=True,width='stretch')

with intake:
    mode=st.radio('Inquiry processing mode',['fixture','live'],horizontal=True)
    st.caption('Fixture mode supports the 20 curated sample inquiries below. Edited or new text requires live mode; an unknown fixture is recorded as fixture_not_found.')
    sample_cases=[c for c in cases if c['category'] in ('complete','missing','ambiguous')]
    def load_sample():
        st.session_state['inquiry_text']=next(c['inquiry'] for c in sample_cases if c['id']==st.session_state['sample_case'])
    st.selectbox('Load fictional sample',[c['id'] for c in sample_cases],key='sample_case',on_change=load_sample)
    if 'inquiry_text' not in st.session_state: st.session_state['inquiry_text']=sample_cases[0]['inquiry']
    with st.form('process_inquiry'):
        text=st.text_area('Fictional customer inquiry',key='inquiry_text',height=140)
        submit=st.form_submit_button('Process inquiry',disabled=mode=='live' and not key_available)
    if submit:
        client=FixtureClient() if mode=='fixture' else OpenAIClient(settings)
        try:
            with st.spinner('Processing…'):
                result=Workflow(db,client,settings).process(text,scope=f'manual:{mode}')
            st.session_state['latest_inquiry']=result['id']
        finally:
            if isinstance(client,OpenAIClient): client.close()
    if 'latest_inquiry' in st.session_state:
        stored=db.get_inquiry(st.session_state['latest_inquiry'])
        if stored and stored['result_json']: show_result(json.loads(stored['result_json']), 'intake')
    st.caption('Live mode sends the fictional inquiry only to OpenAI for processing. Nothing is sent to a customer or written to an external business system.')

with approvals:
    st.write('Read the inquiry, extracted details and draft before approving. This records a local decision and never sends the response.')
    approval_mode=st.selectbox('Approval queue source',['fixture','live'])
    queue=db.list_inquiries(f'manual:{approval_mode}')
    if not queue:
        st.info('Process an inquiry first to create a draft for review.')
    else:
        chosen=st.selectbox('Local inquiry record',[r['id'] for r in queue],format_func=lambda id: next(f"{r['status']} · {r['created_at']} · {id[:8]}" for r in queue if r['id']==id))
        record=db.get_inquiry(chosen)
        st.text(record['inquiry'])
        if record['result_json']: show_result(json.loads(record['result_json']), 'approval')
        # Unique widget keys let two tabs safely render the same result.
        with st.form('approve_form_'+chosen):
            staff=st.text_input('Staff identifier',key='staff_'+chosen)
            confirmed=st.checkbox('I have reviewed this exact draft and approve it locally',key='confirmed_'+chosen)
            approve=st.form_submit_button('Mark response approved',disabled=record['status']!='pending_approval')
        if approve:
            try:
                db.approve(chosen,staff,confirmed=confirmed)
                st.success('Approved locally. No message was sent. Refresh the queue to see the saved state.')
            except ValueError as exc: st.error(str(exc))
        if record['approved_at']: st.caption(f"Approved by {record['approved_by']} at {record['approved_at']} UTC")
    st.caption('Staff identifiers provide attribution in this local prototype; there is no authentication or role enforcement.')

with method:
    st.markdown(Path('docs/acceptance-criteria.md').read_text())
    with st.expander('Prime24AI source reuse'): st.markdown(Path('docs/source-review.md').read_text())
    st.caption('Source files: data/cases.json (independent expected labels), data/fixtures.json (curated canned responses). Evaluation never asks a model to grade its output.')
