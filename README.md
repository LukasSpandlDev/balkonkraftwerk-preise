# Balkonkraftwerk Preis-Monitor

Tägliches Vergleichs-Dashboard für 4smartpower – zeigt die aktuellen Preise von **Tepto, Kleines Kraftwerk, Yuma, Priwatt** und **Solakon** im direkten Vergleich, inkl. €/Wp-Kennzahl und der Position der eigenen Produkte im Markt.

---

## Inhalt

```
balkonkraftwerk-dashboard/
├── index.html            # Das Dashboard (statisch, einfach hochladen)
├── scraper.py            # Holt täglich neue Preise von den Wettbewerbern
├── requirements.txt      # Python-Abhängigkeiten
├── run_daily.bat         # Wrapper für Windows-Aufgabenplanung
├── data/
│   ├── products.json     # Wird vom Scraper geschrieben (aktuell Demo-Daten)
│   └── last_update.json  # Zeitstempel + Statistik
└── README.md
```

---

## Schnellstart

**1. Dashboard direkt ansehen**

`index.html` einfach im Browser öffnen – das Dashboard läuft sofort mit den enthaltenen Demo-Daten.

> Wenn der Browser die `data/*.json`-Dateien aus Sicherheitsgründen nicht laden will, im Projektordner einen Mini-Webserver starten:
> ```bash
> python -m http.server 8000
> ```
> Dann im Browser `http://localhost:8000` öffnen.

**2. Echte Preise holen (einmalig zum Test)**

```bash
pip install -r requirements.txt
python -m playwright install chromium    # nur einmal nötig
python scraper.py
```

Danach im Browser neu laden – die Demo-Daten sind durch echte ersetzt.

**3. Eigene Produkte einpflegen**

Die Datei `data/products.json` enthält am Ende drei Einträge mit `"brand": "4smartpower"`. Diese kannst du an die echten Preise deines Kunden anpassen. Tipp: Für vollautomatisches Tracking auch der eigenen Seite kannst du in `scraper.py` einen weiteren Eintrag in `SITES` hinzufügen.

---

## Bereitstellung beim Kunden

Da es eine **statische HTML-Datei** ist, gibt es viele Wege:

### Variante A – Auf den Webspace des Kunden hochladen (einfachste Lösung)

1. Den ganzen Ordner `balkonkraftwerk-dashboard/` per FTP/SFTP auf den Webspace laden, z. B. nach `/preisvergleich/`.
2. Das Dashboard ist dann unter `https://www.4smartpower.de/preisvergleich/` erreichbar.
3. Auf dem Server (oder lokal) einen Cronjob einrichten, der `scraper.py` einmal täglich laufen lässt.

### Variante B – Lokal scrapen, nur HTML+JSON hochladen

Falls auf dem Webspace kein Python verfügbar ist:

1. Auf deinem Rechner (oder einem kleinen VPS) `scraper.py` täglich per Aufgabenplanung/Cron laufen lassen.
2. Ein kleines Skript synct anschließend `data/products.json` und `data/last_update.json` per FTP zum Webspace.

### Variante C – GitHub Pages + GitHub Actions (kostenlos & vollautomatisch)

1. Den Ordner als Git-Repo anlegen, zu GitHub pushen, Pages aktivieren.
2. `.github/workflows/scrape.yml` mit einem Cron-Trigger (`0 6 * * *`) der `python scraper.py` ausführt und die aktualisierten JSON-Dateien zurück ins Repo committed.
3. Pages baut sich neu, der Kunde bekommt eine URL wie `https://4smartpower.github.io/preise/`.

---

## Tägliches Update einrichten

### Windows (Aufgabenplanung)

1. Aufgabenplanung öffnen → "Aufgabe erstellen".
2. Trigger: täglich, z. B. 06:00 Uhr.
3. Aktion: Programm starten → `run_daily.bat` (volle Pfadangabe).

### Linux/macOS (Cron)

```cron
0 6 * * *  cd /pfad/zum/balkonkraftwerk-dashboard && /usr/bin/python3 scraper.py >> data/scraper.log 2>&1
```

---

## Was tun, wenn der Scraper ein Shop nicht mehr findet?

Die Shops nutzen Shopify, Shopware, WooCommerce o. ä. – die HTML-Selektoren ändern sich gelegentlich. In `scraper.py` ist pro Site ein `card_selectors`-Array hinterlegt. Wenn ein Shop 0 Produkte liefert:

1. Die Site im Browser öffnen, Rechtsklick → Untersuchen.
2. Den umschließenden Container einer Produktkarte finden (oft `<div class="product-card">`, `<li class="grid__item">` o. ä.).
3. Den Selektor ganz oben in die Liste eintragen.

Für JS-lastige Seiten (z. B. wenn Preise dynamisch nachgeladen werden) `"render_js": True` setzen – dann nutzt der Scraper automatisch Playwright statt einfachem `requests`.

---

## Rechtlicher Hinweis

Beim Scraping fremder Webseiten unbedingt:

- **robots.txt** der Anbieter respektieren,
- **Anfrage-Frequenz niedrig halten** (das Skript wartet 2 s zwischen Sites und läuft nur 1×/Tag),
- die Daten **nicht 1:1 öffentlich republizieren** – das Dashboard ist ein **internes Wettbewerbs-Monitoring-Tool** und sollte z. B. per Login oder unter einer nicht-öffentlichen URL zugänglich gemacht werden.

Wenn du das Dashboard öffentlich auf 4smartpower.de zeigen willst, ist die saubere Variante: **Preisspannen aggregieren** (Min/Max, Ø) und keine direkten Modellvergleiche zeigen, oder dafür offizielle Affiliate-Feeds der Anbieter verwenden.
