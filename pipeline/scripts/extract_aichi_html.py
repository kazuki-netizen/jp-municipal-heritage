#!/usr/bin/env python3
"""Conservative table extractor for Aichi municipal designation lists.

It intentionally leaves fields null when a page does not expose a tabular
value.  It writes one municipality at a time so partial runs remain useful.
"""
import json, os, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREF='愛知県'
CATS=['有形文化財','無形文化財','民俗文化財','記念物(史跡・名勝・天然記念物)','その他']
SUB_TO_CAT={
 '建造物':'有形文化財','絵画':'有形文化財','彫刻':'有形文化財','工芸品':'有形文化財','工芸':'有形文化財','書跡':'有形文化財','典籍':'有形文化財','古文書':'有形文化財','考古資料':'有形文化財','考古':'有形文化財','歴史資料':'有形文化財','美術工芸品':'有形文化財',
 '無形文化財':'無形文化財','無形民俗':'民俗文化財','無形民俗文化財':'民俗文化財','有形民俗':'民俗文化財','有形民俗文化財':'民俗文化財','民俗文化財':'民俗文化財',
 '史跡':'記念物(史跡・名勝・天然記念物)','名勝':'記念物(史跡・名勝・天然記念物)','天然記念物':'記念物(史跡・名勝・天然記念物)',
}
def clean(s): return re.sub(r'\s+',' ',s.replace('\xa0',' ')).strip()
def era(s):
 s=clean(s).replace(' ','')
 m=re.search(r'(明治|大正|昭和|平成|令和)(元|\d+)年(\d+)月(\d+)日',s)
 if not m:
  m=re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日',s)
  if not m:return None
  y,mo,d=map(int,m.groups())
 else:
  base={'明治':1867,'大正':1911,'昭和':1925,'平成':1988,'令和':2018}[m[1]]
  y=base+(1 if m[2]=='元' else int(m[2]));mo=int(m[3]);d=int(m[4])
 try:return f'{datetime(y,mo,d):%Y-%m-%d}'
 except ValueError:return None
def cat(sub,context):
 for k,v in SUB_TO_CAT.items():
  if k in (sub or ''): return v
 if '無形民俗' in context or '民俗' in context:return '民俗文化財'
 if any(x in context for x in ['史跡','名勝','天然記念物']):return '記念物(史跡・名勝・天然記念物)'
 if '無形文化財' in context:return '無形文化財'
 if '有形文化財' in context:return '有形文化財'
 return 'その他'
def header_index(headers, words):
 for i,h in enumerate(headers):
  if any(w in h for w in words):return i
 return None
def extract(src):
 slug,muni=src['slug'],src['municipality']; d=f'{ROOT}/cache/{PREF}/{slug}'
 manifest=json.load(open(f'{d}/manifest.json'))
 out=[]; seen=set(); designation='町指定' if muni.endswith('町') else '村指定' if muni.endswith('村') else '市指定'
 for entry in manifest.values():
  if entry.get('http_status')!=200 or entry.get('format')!='html':continue
  path=f"{d}/{entry['filename']}"
  if not os.path.exists(path):continue
  soup=BeautifulSoup(open(path,errors='ignore').read(),'html.parser')
  for table in soup.find_all('table'):
   trs=table.find_all('tr');
   if len(trs)<2:continue
   # Many municipal CMS tables start with a one-cell caption row.  Locate the
   # actual column header rather than assuming the first tr is it.
   hi=None; headers=[]
   for j,tr0 in enumerate(trs[:4]):
    candidate=[clean(x.get_text(' ',strip=True)) for x in tr0.find_all(['th','td'])]
    if any('名称' in x or '名 称' in x or '名　称' in x or '文化財名' in x for x in candidate):
     hi=j;headers=candidate;break
   if hi is None:continue
   ni=header_index(headers,['名称','文化財名','名 称','名　称']); si=header_index(headers,['種別','種類','区分','分類']); di=header_index(headers,['指定年月日','指定日','指定・登録年月日']); li=header_index(headers,['所在地','場所']); oi=header_index(headers,['所有','管理者','保管先']); ai=header_index(headers,['員数'])
   desi=next((i for i,h in enumerate(headers) if h in ('指定','指定・登録','指定区分','指定別')),None)
   if ni is None:continue
   # closest preceding heading supplies a category / designation where omitted.
   prev=table.find_previous(['h1','h2','h3','h4','h5','h6','p','strong'])
   context=clean(prev.get_text(' ',strip=True)) if prev else ''
   for tr in trs[hi+1:]:
    cells=[clean(x.get_text(' ',strip=True)) for x in tr.find_all(['th','td'])]
    if len(cells)<=ni:continue
    name=cells[ni]
    if not name or name in ['合計','計'] or re.fullmatch(r'\d+',name) or ('名 称' in name and '種別' in name):continue
    # tables with an explicit designation column: retain municipal only.
    if desi is not None and desi!=ni and len(cells)>desi:
     dv=cells[desi]
     if any(x in dv for x in ['国指定','県指定','国登録','県登録']) or dv in ['国','県']:continue
     if dv and not any(x in dv for x in ['市','町','村']): continue
    sub=cells[si] if si is not None and len(cells)>si else None
    # suppress statistics tables and table-of-contents rows
    if '指定' in name and re.search(r'\d', name) and len(cells)<4:continue
    desc=[]
    if ai is not None and len(cells)>ai and cells[ai]:desc.append('員数: '+cells[ai])
    if oi is not None and len(cells)>oi and cells[oi]:desc.append('所有者又は管理者: '+cells[oi])
    key=(name,sub or '',entry['url'])
    if key in seen:continue
    seen.add(key)
    out.append({'pref':PREF,'municipality':muni,'name':name,'category':cat(sub,context),'subcategory':sub,'designation':designation,'designated_date':era(cells[di]) if di is not None and len(cells)>di else None,'location':cells[li] if li is not None and len(cells)>li else None,'description':'；'.join(desc) or None,'source_url':entry['url'],'source_format':'html','fetched_at':entry.get('fetched_at') or datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')})
 return out
def main():
 sources=[json.loads(x) for x in open(f'{ROOT}/sources/aichi.jsonl') if x.strip()]
 for src in sources:
  if src['strategy']!='html':continue
  rows=extract(src); p=f'{ROOT}/out/{PREF}';os.makedirs(p,exist_ok=True)
  with open(f"{p}/{src['slug']}.jsonl",'w') as f:
   for x in rows:f.write(json.dumps(x,ensure_ascii=False)+'\n')
  print(src['slug'],len(rows))
if __name__=='__main__':main()
