# TEG Oportunități — pagina publicată

Repo-ul conține doar pagina dashboard-ului intern TEG Oportunități (HTML static: `index.html`, `robots.txt`).

- Datele nu sunt în acest repo: pagina le încarcă doar după introducerea PIN-ului.
- Codul sursă e într-un repo privat; pagina se publică de acolo cu `scripts/publica-pages.sh`.
- Pagina nu se indexează (`noindex`).

## vanzari/2026/ și vanzari/2027/ (din 26.10.2026)
Paginile dashboard-ului de vânzări CODRU (2026 încheiat, 2027 deschis). Nici ele nu conțin date: cer dashboard-ul de la un web app Apps Script („CODRU - Dashboard vanzari (web app)”, contul sebastian@teg.ro), doar cu cheia personală din link (`#k=…`); fără cheie validă, web app-ul răspunde „acces refuzat”.

## colector/ (din 27.10.2026)
Copii zilnice ale unor pagini publice care refuză serverele Google (fonduri-structurale.ro — API-ul public al site-ului; primariatm.ro — știrile și achizițiile directe), făcute de workflow-ul `Colector` (GitHub Actions, `colector/colector.py`, fără secrete). Le citesc scripturile Apps Script TEG Oportunități (scraperul Finanțări și hub-ul Licitații). Conțin doar informație publicată deja de acele site-uri.
