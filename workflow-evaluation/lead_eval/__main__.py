from dataclasses import replace
from getpass import getpass
from .config import Settings
import argparse
import json
import os
from pathlib import Path
from .db import Database
from .evaluation import evaluate


def main():
    parser=argparse.ArgumentParser(description='Evaluate 30 fictional inquiries; fixture mode is free and offline.')
    parser.add_argument('--mode',choices=['fixture','live'],default='fixture')
    parser.add_argument('--db',default=os.getenv('DATABASE_PATH','data/dashboard.sqlite'))
    parser.add_argument('--output',default='reports/evaluation.json')
    parser.add_argument('--prompt-key', action='store_true', help='Prompt privately for the live API key')
    args=parser.parse_args()
    if args.mode=='live' and args.prompt_key and not os.getenv('OPENAI_API_KEY'):
        os.environ['OPENAI_API_KEY']=getpass('OpenAI API key (hidden): ')
    if args.mode=='live' and not os.getenv('OPENAI_API_KEY','').strip():
        parser.error('Live evaluation skipped: OPENAI_API_KEY is unavailable. No calls made.')
    settings=Settings.from_env()
    if args.mode=='live': settings=replace(settings,max_retries=0)
    report=evaluate(Database(args.db),args.mode,settings,live_interval=7 if args.mode=='live' else 0)
    path=Path(args.output)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,indent=2)+'\n')
    m=report['summary']['overall']
    print(f"{args.mode.upper()} benchmark: {m['passed']}/{m['n']} passed; run={report['run_id']}")
    for mode, group in report['summary']['by_measurement'].items():
        print(f"{mode}: n={group['n']}, passed={group['passed']}, extraction={group['extraction_correct']}/{group['extraction_n']}")
    print(f'Report: {path}; SQLite: {args.db}')
    return 0 if m['passed']==m['n'] else 1


if __name__=='__main__':
    raise SystemExit(main())
