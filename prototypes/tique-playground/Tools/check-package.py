"""Validate a fresh checkout with the Python standard library only."""
from functools import partial
from hashlib import sha256
from html.parser import HTMLParser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.parse import quote, urlsplit, unquote
from urllib.request import urlopen
import json, struct

ROOT=Path(__file__).resolve().parent.parent
class Links(HTMLParser):
 def __init__(self):super().__init__();self.paths=[]
 def handle_starttag(self,tag,attrs):
  for k,v in attrs:
   if k in ('href','src') and v and not urlsplit(v).scheme and not v.startswith('#'):self.paths.append(unquote(urlsplit(v).path))

manifest=json.loads((ROOT/'asset-manifest.json').read_text(encoding='utf8'))
for entry in manifest:
 data=(ROOT/entry['path']).read_bytes()
 # Git enforces LF for text in this repository; asset hashes remain byte exact.
 assert sha256(data).hexdigest()==entry['sha256'],entry['path']
meta=json.loads((ROOT/'Revisions/10/data.json').read_text(encoding='utf8'))
parser=Links();parser.feed((ROOT/'index.html').read_text(encoding='utf8'))
paths=set(parser.paths+['index.html','Revisions/10/data.json','Scene/limbus.png','Scene/platform-fill.png'])
frames=0
for name,clip in meta['clips'].items():
 assert len(clip['frames'])==len(clip['durations']),name
 for file in clip['frames']:
  raw=(ROOT/file).read_bytes()
  assert raw[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',raw[16:24])==(64,64),file
  paths.add(file);frames+=1
 for file in clip.get('donors',[]):assert (ROOT/file).is_file(),file
 for key in ['sheet','native']:assert (ROOT/clip[key]).is_file(),clip[key]
class QuietHandler(SimpleHTTPRequestHandler):
 def log_message(self,*args):pass
server=ThreadingHTTPServer(('127.0.0.1',0),partial(QuietHandler,directory=str(ROOT)))
thread=Thread(target=server.serve_forever,daemon=True);thread.start()
try:
 for file in sorted(paths):
  with urlopen(f'http://127.0.0.1:{server.server_port}/'+quote(file),timeout=5) as response:
   assert response.status==200 and response.read()==(ROOT/file).read_bytes(),file
finally:
 server.shutdown();server.server_close();thread.join()
report={'manifestFilesVerified':len(manifest),'nativeFrames':frames,'httpResourcesVerified':len(paths),'passed':True}
(ROOT/'QA/package-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
print(json.dumps(report))
