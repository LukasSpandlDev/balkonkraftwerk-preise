"""
Balkonkraftwerk Preis-Scraper
=============================
Scraped die Produktseiten der wichtigsten Wettbewerber und extrahiert
Modellname, Wattzahl, Preis und Speicher-Info in eine JSON-Datei,
die das Dashboard (index.html) laedt.

Aufruf:  python scraper.py
Output:  data/products.json + data/last_update.json

Dependencies:
    pip install requests beautifulsoup4 lxml playwright
    playwright install chromium  (nur falls JS-Rendering noetig)
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "de-DE,de;q=0.9,en;q=0.5",
}
TIMEOUT = 20
OUT_DIR = Path(__file__).parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class Product:
    brand: str
    name: str
    watts: int | None
    price_eur: float | None
    has_battery: bool
    url: str
    eur_per_wp: float | None = None

    def __post_init__(self) -> None:
        if self.price_eur and self.watts:
            self.eur_per_wp = round(self.price_eur / self.watts, 3)


def fetch(url: str, render_js: bool = False) -> str:
    if render_js:
        try:
            from playwright.sync_api import sync_playwright

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(user_agent=HEADERS["User-Agent"])
                page.goto(url, wait_until="networkidle", timeout=30_000)
                html = page.content()
                browser.close()
                return html
        except Exception as exc:
            print(f"  ! Playwright-Fehler ({exc}); falle auf requests zurueck.")

    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.text


PRICE_RE = re.compile(
    r"(?P<value>\d{1,3}(?:[.\s]\d{3})*(?:,\d{1,2})?|\d+(?:\.\d{1,2})?)\s*€"
)
WATT_RE = re.compile(r"(\d{2,4})\s*(?:Wp|W\b|Watt)", re.IGNORECASE)
BATTERY_KEYWORDS = ("speicher", "akku", "batterie", "storage", "battery")


def parse_price(text: str) -> float | None:
    if not text:
        return None
    match = PRICE_RE.search(text)
    if not match:
        return None
    raw = match.group("value").replace(" ", "")
    if "," in raw and "." in raw:
        raw = raw.replace(".", "").replace(",", ".")
    elif "," in raw:
        raw = raw.replace(",", ".")
    elif "." in raw:
        parts = raw.split(".")
        if len(parts[-1]) == 3:
            raw = raw.replace(".", "")
    try:
        return round(float(raw), 2)
    except ValueError:
        return None


def parse_watts(text: str) -> int | None:
    if not text:
        return None
    match = WATT_RE.search(text)
    if match:
        try:
            value = int(match.group(1))
            if 200 <= value <= 3000:
                return value
        except ValueError:
            pass
    return None


def has_battery(text: str) -> bool:
    text = text.lower()
    return any(keyword in text for keyword in BATTERY_KEYWORDS)


def extract_jsonld_products(soup: BeautifulSoup) -> list[dict]:
    products: list[dict] = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except (json.JSONDecodeError, TypeError):
            continue
        nodes = data if isinstance(data, list) else [data]
        for node in nodes:
            if not isinstance(node, dict):
                continue
            graph = node.get("@graph", [node])
            for item in graph:
                if isinstance(item, dict) and item.get("@type") in ("Product", "ProductGroup"):
                    products.append(item)
    return products


SITES: dict[str, dict] = {
    "Tepto": {
        "url": "https://tepto.de/collections/balkonkraftwerke",
        "card_selectors": ["li.grid__item", "div.product-card", "article.product"],
        "render_js": False,
    },
    "Kleines Kraftwerk": {
        "url": "https://www.kleines-kraftwerk.de/products",
        "card_selectors": ["div.product-card", "article.product-card", "div[data-product-id]"],
        "render_js": True,
    },
    "Yuma": {
        "url": "https://yuma.de/collections/balkonkraftwerke",
        "card_selectors": ["div.product-card", "li.grid__item", "div[data-product-handle]"],
        "render_js": False,
    },
    "Priwatt": {
        "url": "https://priwatt.de/produkte/",
        "card_selectors": ["div.product-card", "article.product", "div.card"],
        "render_js": True,
    },
    "Solakon": {
        "url": "https://solakon.de/collections/balkonkraftwerke",
        "card_selectors": ["li.grid__item", "div.product-card", "article"],
        "render_js": False,
    },
}


def scrape_site(brand: str, cfg: dict) -> list[Product]:
    print(f"-> {brand}: lade {cfg['url']}")
    try:
        html = fetch(cfg["url"], render_js=cfg.get("render_js", False))
    except Exception as exc:
        print(f"  ! Fehler beim Laden: {exc}")
        return []

    soup = BeautifulSoup(html, "lxml")
    found: list[Product] = []

    for item in extract_jsonld_products(soup):
        name = item.get("name", "").strip()
        if not name:
            continue
        offer = item.get("offers") or {}
        if isinstance(offer, list):
            offer = offer[0] if offer else {}
        price = parse_price(str(offer.get("price", "") or offer.get("lowPrice", "")))
        url = item.get("url", cfg["url"])
        text = f"{name} {item.get('description','')}"
        product = Product(
            brand=brand,
            name=name,
            watts=parse_watts(text),
            price_eur=price,
            has_battery=has_battery(text),
            url=url if url.startswith("http") else cfg["url"],
        )
        if product.price_eur:
            found.append(product)

    if not found:
        cards: list = []
        for sel in cfg["card_selectors"]:
            cards = soup.select(sel)
            if cards:
                break

        for card in cards[:50]:
            text = " ".join(card.stripped_strings)
            price = parse_price(text)
            watts = parse_watts(text)
            if not price:
                continue
            link = card.find("a", href=True)
            url = link["href"] if link else cfg["url"]
            if url.startswith("/"):
                from urllib.parse import urljoin
                url = urljoin(cfg["url"], url)
            name_el = card.find(["h2", "h3", "h4"])
            name = (name_el.get_text(" ", strip=True) if name_el else text[:80]).strip()
            found.append(
                Product(
                    brand=brand,
                    name=name,
                    watts=watts,
                    price_eur=price,
                    has_battery=has_battery(text),
                    url=url,
                )
            )

    unique: dict[tuple, Product] = {}
    for p in found:
        key = (p.name.lower()[:60], p.watts)
        if key not in unique or (p.price_eur and not unique[key].price_eur):
            unique[key] = p

    print(f"  + {len(unique)} Produkt(e) gefunden")
    return list(unique.values())


def main() -> None:
    all_products: list[Product] = []
    for brand, cfg in SITES.items():
        try:
            all_products.extend(scrape_site(brand, cfg))
            time.sleep(2)
        except Exception as exc:
            print(f"  !! {brand} fehlgeschlagen: {exc}")

    all_products.sort(key=lambda p: (p.brand, p.watts or 0, p.price_eur or 0))

    out_file = OUT_DIR / "products.json"
    out_file.write_text(
        json.dumps([asdict(p) for p in all_products], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    meta_file = OUT_DIR / "last_update.json"
    meta_file.write_text(
        json.dumps(
            {
                "last_update": datetime.now().isoformat(timespec="seconds"),
                "product_count": len(all_products),
                "brands": sorted({p.brand for p in all_products}),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(f"\nFertig. {len(all_products)} Produkte -> {out_file}")


if __name__ == "__main__":
    main()
