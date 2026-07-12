import sys
from bs4 import BeautifulSoup

path = sys.argv[1]
with open(path, encoding='utf-8', errors='replace') as f:
    html = f.read()
soup = BeautifulSoup(html, 'lxml')
for tag in soup(['script', 'style']):
    tag.decompose()

# Try to preserve table structure
out = []
for table in soup.find_all('table'):
    out.append('=== TABLE ===')
    for tr in table.find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        out.append(' | '.join(cells))
    out.append('=== /TABLE ===')
    table.decompose()

text = soup.get_text('\n')
lines = [l.strip() for l in text.split('\n')]
lines = [l for l in lines if l]
out.append('=== REST TEXT ===')
out.extend(lines)
print('\n'.join(out))
