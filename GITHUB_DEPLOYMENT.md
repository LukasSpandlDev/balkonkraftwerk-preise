# GitHub Pages Setup – Schritt für Schritt

Komplette Anleitung, um das Dashboard kostenlos online zu stellen mit täglich automatisch aktualisierten Preisen. **Alles per Browser, keine Kommandozeile.**

Gesamt-Aufwand: einmalig **~15 Minuten**. Danach läuft alles vollautomatisch für immer.

---

## Schritt 1 — GitHub-Account anlegen (überspringen, falls vorhanden)

1. Auf [github.com](https://github.com) gehen
2. Oben rechts auf **„Sign up"** klicken
3. E-Mail eingeben, Passwort wählen, Username wählen (z. B. `4smartpower` oder dein Name)
4. E-Mail bestätigen

Kosten: 0 €. Du brauchst keinen kostenpflichtigen Plan.

---

## Schritt 2 — Neues Repository anlegen

1. Auf github.com einloggen
2. Oben rechts auf das **`+`-Symbol** klicken → **„New repository"**
3. Felder ausfüllen:
   - **Repository name:** `balkonkraftwerk-preise` (oder wie du willst)
   - **Description:** *Preis-Monitor für Balkonkraftwerke* (optional)
   - **Public** auswählen (ist Pflicht für kostenloses GitHub Pages)
   - Den Haken bei **„Add a README file"** kannst du leer lassen – wir laden gleich ein eigenes hoch
4. Unten auf **„Create repository"** klicken

→ Du landest auf einer leeren Repository-Seite.

---

## Schritt 3 — Dateien hochladen

1. Auf der Repository-Seite den Link **„uploading an existing file"** klicken
   - Falls der Link nicht da ist: oben **„Add file"** → **„Upload files"**

2. Im Datei-Explorer den Ordner `balkonkraftwerk-dashboard` auf deinem Rechner öffnen

3. **Alle Inhalte des Ordners** (NICHT den Ordner selbst, sondern was drin ist) markieren mit `Strg + A` und per Drag & Drop in das GitHub-Browser-Fenster ziehen
   - Das sind: `index.html`, `scraper.py`, `requirements.txt`, `README.md`, `GITHUB_DEPLOYMENT.md`, `run_daily.bat`, der `data`-Ordner und der `.github`-Ordner
   - **Wichtig:** Der versteckte Ordner `.github` muss mit hoch! Falls Windows ihn ausblendet: im Datei-Explorer oben **„Anzeigen"** → **„Ausgeblendete Elemente"** anhaken.

4. Unten ein kurzes Commit-Message-Feld ausfüllen (z. B. „initial upload") oder einfach das Vorgegebene lassen

5. Auf den grünen **„Commit changes"**-Button klicken

→ Warten, bis alle Dateien hochgeladen sind. Du siehst dann die Datei-Übersicht.

---

## Schritt 4 — GitHub Pages aktivieren

1. Im Repo oben in der Leiste auf **„Settings"** klicken
2. Im linken Menü unter **„Code and automation"** auf **„Pages"** klicken
3. Bei **„Source"**: **„Deploy from a branch"** wählen (sollte schon ausgewählt sein)
4. Bei **„Branch"**: aus dem Dropdown **„main"** wählen, daneben **„/ (root)"** lassen
5. **„Save"** klicken

→ Oben erscheint nach 1-2 Minuten ein grüner Kasten mit:

> **Your site is live at https://DEIN-USERNAME.github.io/balkonkraftwerk-preise/**

Das ist deine Live-URL! Die kannst du deinem Kunden schicken.

---

## Schritt 5 — Erste Preise scrapen (manueller Start)

Beim Anlegen läuft der Auto-Scraper noch nicht. Lass uns ihn einmal von Hand starten, damit echte Daten da sind:

1. Im Repo oben in der Leiste auf **„Actions"** klicken
2. Falls du gewarnt wirst „Workflows aren't being run on this forked repository", klick **„I understand my workflows, go ahead and enable them"**
3. Links auf **„Daily Price Scrape"** klicken
4. Rechts auf den grauen Button **„Run workflow"** klicken → im Dropdown nochmal **„Run workflow"**
5. Warten – nach ~2 Minuten siehst du einen grünen Haken bei dem Lauf

→ Browser-Tab vom Dashboard (`https://DEIN-USERNAME.github.io/balkonkraftwerk-preise/`) neu laden.
→ Echte Preise sind jetzt drin.

---

## Schritt 6 — Tägliches Update überprüfen (nach 1 Tag)

Der Workflow läuft ab jetzt automatisch jeden Tag um 06:00 UTC (= 08:00 deutsche Sommerzeit, 07:00 Winterzeit).

Nach einem Tag kannst du in den **„Actions"**-Tab gehen und siehst dort einen neuen erfolgreichen Lauf.

Falls du die Uhrzeit ändern willst: in `.github/workflows/scrape.yml` die Zeile `- cron: '0 6 * * *'` editieren. Format: `Minute Stunde Tag Monat Wochentag` (alles in UTC). Beispiel `0 5 * * *` = 05:00 UTC = 07:00 Berlin Sommerzeit.

Editieren geht direkt im GitHub-Webbrowser: Datei öffnen, oben rechts auf das **Stift-Symbol** klicken, ändern, unten „Commit changes".

---

## Was du jetzt hast

- ✅ Live-Dashboard unter `https://DEIN-USERNAME.github.io/balkonkraftwerk-preise/`
- ✅ Vollautomatisches tägliches Preis-Update (1× pro Tag, 06:00 UTC)
- ✅ Kosten: 0 €, dauerhaft
- ✅ Alle Daten unter deiner Kontrolle (du siehst den Verlauf jeder Änderung im „Commits"-Tab)

---

## Was deinem Kunden geben

Schick ihm einfach die Live-URL. Wenn er einen eigenen Bereich auf 4smartpower.de haben will, leitet sein Webmaster z. B. `https://4smartpower.de/preisvergleich/` per Subdomain oder iframe auf deine GitHub-Pages-URL. Stichworte für seinen Webmaster: **CNAME-Eintrag** (Subdomain) oder **iframe-Embedding**.

---

## Probleme?

**„Run workflow"-Button ist grau:** Den Workflow musst du erst einmal in den Settings „autorisieren". GitHub macht das beim ersten Lauf automatisch nach Klick auf den orangen Banner oben.

**„Workflow failed" mit rotem Kreuz:** Klick auf den fehlgeschlagenen Lauf, dann auf den `scrape`-Schritt. Die Fehlermeldung sagt dir meist, welcher Shop sich quergestellt hat. Schick mir den Screenshot, ich passe das Skript an.

**Die Wattzahlen oder Preise sehen falsch aus für einen Shop:** Der CSS-Selektor passt vermutlich nicht. In der `scraper.py` (direkt im GitHub-Web-Editor änderbar) im `SITES`-Dict den passenden Shop suchen und neue Selektoren ergänzen. Auch hier: schick mir den betroffenen Shop, ich tune das.
