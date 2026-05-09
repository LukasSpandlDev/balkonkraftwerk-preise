@echo off
REM Tägliches Update der Preisdaten - mit Windows-Aufgabenplanung verknüpfen
cd /d "%~dp0"
python scraper.py >> data\scraper.log 2>&1
