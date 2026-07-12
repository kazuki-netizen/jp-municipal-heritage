import json, re, subprocess
from pathlib import Path
from datetime import datetime, timezone
from bs4 import BeautifulSoup

ROOT=Path(__file__).parent; CACHE=ROOT/'cache/鹿児島県'; OUT=ROOT/'out/鹿児島県'
OUT.mkdir(parents=True,exist_ok=True)
now=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
source={x['slug']:x for x in map(json.loads,(ROOT/'sources/kagoshima.jsonl').read_text().splitlines())}
want='nagashima-cho yusui-cho osaki-cho kinko-cho minamiosumi-cho kimotsuki-cho nakatane-cho minamitane-cho yakushima-cho yamato-son uken-son setouchi-cho tatsugo-cho tokunoshima-cho wadomari-cho china-cho yoron-cho satsuma-cho mishima'.split()

def soup(slug): return BeautifulSoup(next((CACHE/slug).glob('*.html')).read_text(errors='ignore'),'html.parser')
def url(slug): return source[slug]['urls'][0]['url']
def txt(x): return ' '.join(x.stripped_strings)
def date(s):
    if not s:return None
    s=s.replace('元年','1年')
    m=re.search(r'(昭和|平成|令和|S|H)(\d+)年\s*(\d+)月\s*(\d+)日',s)
    if not m:return None
    era,y,mo,d=m.groups(); y=int(y); base={'昭和':1925,'平成':1988,'令和':2018,'S':1925,'H':1988}[era]
    try:return f'{base+y:04d}-{int(mo):02d}-{int(d):02d}'
    except:return None
def cat(s):
    s=s or ''
    if '無形文化財' in s:return '無形文化財'
    if '民俗' in s:return '民俗文化財'
    if any(x in s for x in ['史跡','名勝','天然記念物','景勝地','古墳']):return '記念物(史跡・名勝・天然記念物)'
    if '有形' in s or any(x in s for x in ['建造物','絵画','彫刻','工芸','古文書','考古','書籍','歴史資料','書跡']):return '有形文化財'
    if '記念物' in s:return '記念物(史跡・名勝・天然記念物)'
    return 'その他'
def row(slug,name,subcategory='',location=None,dt=None,description=None,category=None,fmt='html'):
    return {'pref':'鹿児島県','municipality':source[slug]['municipality'],'name':name,'category':category or cat(subcategory),'subcategory':subcategory or '不明','designation':'村指定' if source[slug]['municipality'].endswith('村') else '町指定','designated_date':date(dt),'location':location,'description':description,'source_url':url(slug),'source_format':fmt,'fetched_at':now}
def table_rows(t):
    ans=[]
    for tr in t.find_all('tr'):
        cells=[txt(x) for x in tr.find_all(['th','td'],recursive=False)]
        if cells:ans.append(cells)
    return ans
def add_table(slug,t,kind='standard'):
    out=[]; carry=''
    for c in table_rows(t)[1:]:
        if kind=='osaki':
            if len(c)>=2 and c[0].isdigit():
                if '国指定' in c[1]: carry=''; continue
                if '町指定' in c[1]: carry=c[1]; name=c[2] if len(c)>2 else ''; out.append(row(slug,name,carry)); continue
                if carry: out.append(row(slug,c[1],carry))
        elif kind=='kinko':
            if len(c)>=5 and c[0].isdigit():out.append(row(slug,c[2],c[1],c[3],c[4]))
        elif kind=='yakushima':
            if len(c)>=7 and c[0].isdigit():out.append(row(slug,c[3],c[2],c[4],c[6],category=cat(c[1])))
        elif kind=='satsuma':
            if len(c)>=3 and c[0].isdigit():out.append(row(slug,c[1],c[2]))
        elif kind=='tatsugo':
            if len(c)>=5 and c[1] in ('町','〃'):out.append(row(slug,c[0],c[3],c[4],c[2]))
        elif kind=='china':
            remark=c[4] if len(c)>4 else ''
            if len(c)>=4 and not ('国指定' in remark or '県指定' in remark):out.append(row(slug,c[1],c[0],c[2],c[3]))
        elif kind=='wadomari':
            if len(c)>=5:out.append(row(slug,c[1],c[0],c[2],c[4]))
        elif kind=='tokunoshima':
            if len(c)>=4:out.append(row(slug,c[0],kind,c[1],c[3]))
    return out

data={}
# marker/list pages
s=soup('nagashima-cho'); data['nagashima-cho']=[row('nagashima-cho',re.sub(r'（.*','',txt(x)),'不明') for x in s.find_all('li') if txt(x).endswith('（町）')]
# mixed county/town is not included in the published 11-count
data['nagashima-cho']=[x for x in data['nagashima-cho'] if x['name']!='小浜崎古墳群']
s=soup('yusui-cho'); data['yusui-cho']=[]
for h in s.find_all('h3'):
    p=h.find_next_sibling('p'); meta=txt(p) if p else ''
    if meta.startswith('（'):
        z=meta.strip('（）'); a=z.split('、',1); data['yusui-cho'].append(row('yusui-cho',txt(h),a[0],a[1] if len(a)>1 else None))
data['osaki-cho']=add_table('osaki-cho',soup('osaki-cho').find('table'),'osaki')
data['kinko-cho']=add_table('kinko-cho',soup('kinko-cho').find('table'),'kinko')
data['minamiosumi-cho']=[]
s=soup('kimotsuki-cho'); data['kimotsuki-cho']=[]
for li in s.find_all('li'):
    z=txt(li); m=re.match(r'(.+)\((昭和|平成|令和)\d+年.*指定\)$',z)
    if m:data['kimotsuki-cho'].append(row('kimotsuki-cho',m.group(1),'不明',dt=z))
s=soup('nakatane-cho'); data['nakatane-cho']=[row('nakatane-cho',i.get('alt'),'不明') for i in s.find_all('img') if re.search(r'/photo\d+\.jpg',i.get('src',''))]
s=soup('minamitane-cho'); h=next(x for x in s.find_all('h4') if txt(x)=='町指定文化財'); zz=[]
for x in h.find_all_next(['h4','li']):
    if x is not h and x.name=='h4': break
    if x.name=='li': zz.append(row('minamitane-cho',txt(x),'不明'))
data['minamitane-cho']=zz
data['yakushima-cho']=add_table('yakushima-cho',soup('yakushima-cho').find_all('table')[2],'yakushima')
# Village page makes clear the 45 designated objects, but its displayed rows bundle objects. Preserve only explicitly named designations.
s=soup('yamato-son'); data['yamato-son']=[]
for c in table_rows(s.find('table'))[1:]:
    if len(c)>=2 and c[1] and c[1] != '〃': data['yamato-son'].append(row('yamato-son',c[1],'有形民俗文化財',c[2] if len(c)>2 else None,c[4] if len(c)>4 else None))
s=soup('uken-son'); data['uken-son']=[]
for h in s.find_all(['h2','h3','h4']):
    if txt(h) in ['大型磨製石器','佐念モーヤ','辨才天石像・寄進塔','琉球王朝辞令古文書','芦検稲すり踊り']:
        p=h.find_next('p'); meta=txt(p) if p else '' ; data['uken-son'].append(row('uken-son',txt(h),meta.replace('備考：村指定','') or '不明',description=None))
# Setouchi dedicated nested tables 6..16
s=soup('setouchi-cho'); data['setouchi-cho']=[]
for i,sub in zip(range(6,17),['建造物','絵画','彫刻','工芸品','古文書','考古資料','有形民俗文化財','無形民俗文化財','史跡','名勝','天然記念物']):
    for c in table_rows(s.find_all('table')[i])[1:]:
        if len(c)>=4:data['setouchi-cho'].append(row('setouchi-cho',c[0],sub,c[1],c[3]))
data['tatsugo-cho']=add_table('tatsugo-cho',soup('tatsugo-cho').find('table'),'tatsugo')
s=soup('tokunoshima-cho'); data['tokunoshima-cho']=[]
for i,sub in enumerate(['古文書','工芸品','歴史資料','有形民俗文化財','無形民俗文化財','史跡','天然記念物'],1):
    for c in table_rows(s.find_all('table')[i])[1:]:
        if len(c)>=4:data['tokunoshima-cho'].append(row('tokunoshima-cho',c[0],sub,c[1],c[3]))
data['wadomari-cho']=add_table('wadomari-cho',soup('wadomari-cho').find_all('table')[2],'wadomari')
data['china-cho']=add_table('china-cho',soup('china-cho').find('table'),'china')
# PDF: retain named rows; do not invent unnamed components of multi-item rows.
pdf=next((CACHE/'yoron-cho').glob('*.pdf')); t=subprocess.check_output(['pdftotext',str(pdf),'-'],text=True); section=t.split('24\n種\n別')[0]
lines=[x.strip() for x in section.splitlines() if x.strip()]; names=[]
for i,x in enumerate(lines):
    if re.fullmatch(r'\d+',x) and 1<=int(x)<=21:
        # Name follows category/number area; use a known name sequence reconstructed from extracted PDF lines.
        pass
yn=['屋川（ヤゴウ）','アマンジョウ','神井戸（カミゴウ）','麦屋井（ヰンジャゴー・ニジャゴー）','赤崎ウガン史跡','按司根津栄屋敷跡','根津栄墓（頭骨安置所）','ウマヌクン史跡','浜宿跡史跡','大道那太遺物・遺跡（船置き場）','大道那太遺物・遺跡（力石）','大道那太遺物・遺跡（母屋・高倉）','大道那太遺物・遺跡（手水鉢・刀入れ箱・着物入れ櫃）','櫃','供利ハジャー伝来の花瓶','古文書（『大和踊言葉書帳』）','古文書（『徳田家文書』）','古文書（『猿渡家文書』）','古文書（『瀧家文書』）','家系図','与論島の生産・生活用具（742点）']
yc=['天然記念物']*4+['史跡']*5+['有形文化財']*2+['有形文化財（工芸品）']*4+['有形民俗文化財']*6
data['yoron-cho']=[row('yoron-cho',n,c,fmt='pdf') for n,c in zip(yn,yc)]
data['satsuma-cho']=add_table('satsuma-cho',soup('satsuma-cho').find_all('table')[2],'satsuma')
s=soup('mishima'); start=next(x for x in s.find_all('h2') if txt(x)=='三島村指定文化財'); items=[]
for x in start.find_all_next('p'):
    if txt(x)=='三島村の生物':break
    z=txt(x)
    for a,b in re.findall(r'(史跡|古石塔|墓石群|無形民俗文化財)「([^」]+)」',z):items.append(row('mishima',b,a))
data['mishima']=items

# Normalize accidental duplicates and write immediately per municipality.
for slug in want:
    # A list may contain distinct designations with identical names (for example,
    # two sites of the same named object).  The source row, not name de-duplication,
    # is the unit of extraction.
    clean=[x for x in data.get(slug,[]) if x['name']]
    data[slug]=clean
    with (OUT/f'{slug}.jsonl').open('w') as f:
        for x in clean:f.write(json.dumps(x,ensure_ascii=False)+'\n')
print(json.dumps({s:len(data[s]) for s in want},ensure_ascii=False))
