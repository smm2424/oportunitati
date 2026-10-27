#!/usr/bin/env python3
"""Colectorul TEG Oportunități (GitHub Actions, zilnic) — paginile publice care refuză serverele Google (Apps Script).

Scrie în colector/:
  fs1.json  = apelurile active / programate de pe fonduri-structurale.ro (API-ul public al site-ului), aceleași câmpuri ca scraperul Finanțări (FSNEXT)
  fs2.json  = ultimele 50 de știri fonduri-structurale.ro
  s20.html  = prima pagină primariatm.ro (știrile) · pmtm.html = cumpărări directe · pmtm2.html = procedură proprie
  stare.json = ora colectării și rezultatul fiecărei ținte
Paginile HTML: fără scripturi / stiluri, linkuri absolute, <meta name="colectat"> cu ora. La o eroare fișierul vechi rămâne neatins
(scraperul și hub-ul văd data veche și raportează eroarea). Doar biblioteca standard Python.
"""
import json, re, sys, time, datetime, urllib.request, urllib.parse, os

AICI = os.path.dirname(os.path.abspath(__file__))
UA = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36'
FS_API = 'https://admin.fonduri-structurale.ro/api/'
ACUM = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z')

def ia(url, timeout=60):
    cer = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': 'text/html,application/json;q=0.9,*/*;q=0.8', 'Accept-Language': 'ro-RO,ro;q=0.9,en;q=0.5'})
    with urllib.request.urlopen(cer, timeout=timeout) as r:
        return r.status, r.read()

def scrie(nume, continut):
    with open(os.path.join(AICI, nume), 'wb') as f:
        f.write(continut if isinstance(continut, bytes) else continut.encode('utf-8'))

def fs1():
    campuri = ['title', 'slug', 'callStatus', 'endDate', 'startDate', 'dateStartPublicConsultation', 'dateEndPublicConsultation', 'shortDescription', 'updatedAt']
    f = '&'.join('fields%5B{}%5D={}'.format(k, x) for k, x in enumerate(campuri))
    q = ('fundings?' + f + '&populate%5Bprogramme%5D%5Bfields%5D%5B0%5D=title&filters%5BcallStatus%5D%5B%24in%5D%5B0%5D=Activ'
         '&filters%5BcallStatus%5D%5B%24in%5D%5B1%5D=Programat&pagination%5BpageSize%5D=100&sort=updatedAt%3Adesc&pagination%5Bpage%5D=')
    date, p, maxp = [], 1, 1
    while p <= maxp and p <= 8:
        cod, b = ia(FS_API + q + str(p))
        j = json.loads(b.decode('utf-8'))
        date += j.get('data') or []
        maxp = ((j.get('meta') or {}).get('pagination') or {}).get('pageCount') or 1
        p += 1
        time.sleep(1)
    if not date:
        raise RuntimeError('API-ul a întors 0 apeluri')
    scrie('fs1.json', json.dumps({'data': date, 'meta': {'colectat': ACUM, 'pagini': p - 1}}, ensure_ascii=False))
    return {'http': 200, 'n': len(date)}

def fs2():
    cod, b = ia(FS_API + 'articles?fields%5B0%5D=title&fields%5B1%5D=slug&fields%5B2%5D=publishedAt&fields%5B3%5D=shortDescription'
                '&pagination%5BpageSize%5D=50&sort=publishedAt%3Adesc')
    j = json.loads(b.decode('utf-8'))
    if not j.get('data'):
        raise RuntimeError('API-ul a întors 0 știri')
    j.setdefault('meta', {})['colectat'] = ACUM
    scrie('fs2.json', json.dumps(j, ensure_ascii=False))
    return {'http': cod, 'n': len(j['data'])}

def pagina(url, nume):
    cod, b = ia(url)
    h = b.decode('utf-8', 'replace')
    if cod != 200 or len(h) < 2000:
        raise RuntimeError('HTTP {} · {} caractere'.format(cod, len(h)))
    h = re.sub(r'<(script|style|noscript|svg|iframe)\b[\s\S]*?</\1\s*>', ' ', h, flags=re.I)
    h = re.sub(r'<!--[\s\S]*?-->', ' ', h)
    def absolut(m):
        v = m.group(3).strip()
        if re.match(r'^(mailto:|tel:|javascript:|#|data:)', v, re.I):
            return m.group(0)
        return '{}={}{}{}'.format(m.group(1), m.group(2), urllib.parse.urljoin(url, v), m.group(2))
    h = re.sub(r'\b(href|src)\s*=\s*(["\'])(.*?)\2', absolut, h, flags=re.I)
    meta = '<meta name="colectat" content="{}"><meta name="sursa" content="{}">'.format(ACUM, url)
    h = re.sub(r'<head(\s[^>]*)?>', lambda m: m.group(0) + meta, h, count=1, flags=re.I) if re.search(r'<head(\s[^>]*)?>', h, re.I) else meta + h
    scrie(nume, h)
    return {'http': cod, 'caractere': len(h), 'linkuri': len(re.findall(r'<a\s', h, re.I))}

TINTE = [
    ('fs1', fs1),
    ('fs2', fs2),
    ('s20', lambda: pagina('https://www.primariatm.ro/', 's20.html')),
    ('pmtm', lambda: pagina('https://www.primariatm.ro/anunturi/cumparari-directe', 'pmtm.html')),
    ('pmtm2', lambda: pagina('https://www.primariatm.ro/anunturi/procedura-proprie', 'pmtm2.html')),
]

def main():
    stare = {'colectat': ACUM, 'tinte': {}}
    for nume, fn in TINTE:
        for incercare in (1, 2):
            try:
                stare['tinte'][nume] = fn()
                break
            except Exception as e:
                stare['tinte'][nume] = {'eroare': '{}: {}'.format(type(e).__name__, str(e)[:200]), 'incercari': incercare}
                time.sleep(5)
        print(nume, stare['tinte'][nume])
    scrie('stare.json', json.dumps(stare, ensure_ascii=False, indent=1))
    return 0

if __name__ == '__main__':
    sys.exit(main())
