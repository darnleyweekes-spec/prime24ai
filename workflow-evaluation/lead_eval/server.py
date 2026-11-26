"""Small loopback-only HTTP API. No web framework or external write integrations."""
import argparse
import json
import os
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator
from .client import FixtureClient, OpenAIClient
from .config import Settings
from .db import Database
from .prime24 import assessment_to_inquiry
from .workflow import Workflow


class LeadRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    inquiry: str | None = None
    assessment: dict[str,str] | None = None
    mode: Literal['fixture','live'] = 'fixture'

    @model_validator(mode='after')
    def one_input(self):
        if (self.inquiry is None) == (self.assessment is None):
            raise ValueError('Supply inquiry or Prime24AI assessment, exactly one')
        return self


class ApprovalRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    staff: str = Field(min_length=1,max_length=120)
    confirmed: bool


def make_server(db: Database, settings=None, *, port=8765):
    settings = settings or Settings.from_env()
    class Handler(BaseHTTPRequestHandler):
        server_version = 'LeadEvaluationPrototype/1'
        def log_message(self, *_): pass

        def reply(self, status, body):
            data=json.dumps(body).encode()
            self.send_response(status)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.end_headers()
            self.wfile.write(data)

        def local_request(self):
            # No browser integration is needed. Refuse cross-origin/browser requests
            # and unrecognized Host values to reduce localhost cross-site access.
            host=self.headers.get('Host','').split(':')[0]
            if host not in ('localhost','127.0.0.1') or self.headers.get('Origin'):
                self.reply(403,{'error':'loopback_cli_only'})
                return False
            return True

        def read_json(self):
            if self.headers.get_content_type()!='application/json' or self.headers.get('Transfer-Encoding'):
                raise ValueError('Use application/json with a Content-Length')
            size=int(self.headers.get('Content-Length','0'))
            if not 1 <= size <= 16384: raise ValueError('Body must be 1–16384 bytes')
            self.connection.settimeout(5)
            return json.loads(self.rfile.read(size))

        def do_GET(self):
            if not self.local_request(): return
            if self.path=='/health':
                self.reply(200,{'status':'ok','default_mode':'fixture','live_configured':bool(os.getenv('OPENAI_API_KEY','').strip()),'sends_messages':False})
                return
            match=re.fullmatch(r'/api/leads/([a-f0-9]{32})',self.path)
            if match:
                row=db.get_inquiry(match[1])
                if row:
                    self.reply(200,json.loads(row['result_json']) if row['result_json'] else {'id':row['id'],'status':row['status']})
                else: self.reply(404,{'error':'not_found'})
                return
            self.reply(404,{'error':'not_found'})

        def do_POST(self):
            if not self.local_request(): return
            try:
                payload=self.read_json()
                if self.path=='/api/leads':
                    request=LeadRequest.model_validate(payload)
                    text=request.inquiry if request.inquiry is not None else assessment_to_inquiry(request.assessment)
                    if request.mode=='live' and not os.getenv('OPENAI_API_KEY','').strip():
                        self.reply(503,{'error':'live_not_configured'})
                        return
                    client=FixtureClient() if request.mode=='fixture' else OpenAIClient(settings)
                    try:
                        result=Workflow(db,client,settings).process(text,scope=f'manual:{request.mode}')
                    finally:
                        if isinstance(client,OpenAIClient): client.close()
                    # Business errors are persisted and returned as typed workflow results.
                    self.reply(201 if result['status']=='pending_approval' else 200,result)
                    return
                match=re.fullmatch(r'/api/leads/([a-f0-9]{32})/approve',self.path)
                if match:
                    request=ApprovalRequest.model_validate(payload)
                    if not db.get_inquiry(match[1]):
                        self.reply(404,{'error':'not_found'})
                        return
                    try:
                        db.approve(match[1],request.staff,confirmed=request.confirmed is True)
                    except ValueError:
                        self.reply(409,{'error':'approval_transition_rejected'})
                        return
                    self.reply(200,json.loads(db.get_inquiry(match[1])['result_json']))
                    return
                self.reply(404,{'error':'not_found'})
            except (ValueError,ValidationError,TimeoutError,UnicodeError):
                self.reply(400,{'error':'invalid_request','detail':'Check JSON, input fields, confirmation and body size.'})
            except Exception:
                # Never expose headers, credentials, raw provider errors or stack traces.
                self.reply(500,{'error':'internal_error'})
    return ThreadingHTTPServer(('127.0.0.1',port),Handler)


def main():
    parser=argparse.ArgumentParser(description='Local-only AI lead backend. No authentication; do not expose publicly.')
    parser.add_argument('--port',type=int,default=8765)
    parser.add_argument('--db',default=os.getenv('DATABASE_PATH','data/dashboard.sqlite'))
    args=parser.parse_args()
    server=make_server(Database(args.db),port=args.port)
    print(f'Local lead API: http://127.0.0.1:{server.server_port}; no messages are sent',flush=True)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    finally: server.server_close()


if __name__=='__main__': main()
