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
    args=parser.parse_args()
    if args.mode=='live' and not os.getenv('OPENAI_API_KEY','').strip():
        parser.error('Live evaluation skipped: OPENAI_API_KEY is unavailable. No calls made.')
    report=evaluate(Database(args.db),args.mode)
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
