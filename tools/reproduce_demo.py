#!/usr/bin/env python3
"""Reproduce the recorded 3 -> 2 review without overwriting historical evidence."""
import json
import sys
import tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.checkers import run_all
from src.schema import make_report
from src.compare import compare_reports, write_comparison_html
from src.reporter import write_json,write_html
root=Path(__file__).resolve().parents[1]
out=Path(sys.argv[1]) if len(sys.argv)>1 else Path(tempfile.mkdtemp(prefix='sitecheck-verified-'))
out.mkdir(parents=True,exist_ok=True)
page=root/'demo-site/index.html'
after_source=page.read_text()
label='<label for="email-input">Email address</label>'
assert label in after_source,'Demo label not found; update this reproduction explicitly.'
before_source=after_source.replace(label,'',1)
before=make_report(run_all(before_source,str(page)), 'demo-site/index.html')
after=make_report(run_all(after_source,str(page)), 'demo-site/index.html')
for r in [before,after]:
 for f in r['findings']:f['file']='demo-site/index.html';f['evidence']=f['evidence'].replace(str(root)+'/','')
comparison=compare_reports(before,after)
assert (before['total_findings'],after['total_findings'])==(3,2)
assert comparison['comparison_summary']=={'fixed':1,'still_open':2,'regressed':0}
for name,r in [('before',before),('after',after),('comparison',comparison)]:
 write_json(r,out/(name+'.json'))
 (write_comparison_html if name=='comparison' else write_html)(r,out/(name+'.html'))
print(json.dumps({'before':3,'after':2,**comparison['comparison_summary'],'output':str(out)},indent=2))
