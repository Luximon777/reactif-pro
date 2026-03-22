from fastapi import APIRouter
import httpx
from bs4 import BeautifulSoup
import logging
import json
import re

router = APIRouter()


async def _scrape_with_headers(url: str, headers: dict) -> tuple:
    """Try scraping with given headers, return (status_code, text)"""
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        resp = await client.get(url, headers=headers)
        return resp.status_code, resp.text


def _extract_job_text(html: str) -> str:
    """Extract job offer text from HTML"""
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe", "noscript"]):
        tag.decompose()

    # Try JSON-LD structured data first (many job sites use this)
    for script in BeautifulSoup(html, "html.parser").find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                data = next((d for d in data if d.get("@type") == "JobPosting"), data[0] if data else {})
            if data.get("@type") == "JobPosting":
                parts = []
                if data.get("title"):
                    parts.append(f"Poste : {data['title']}")
                if data.get("hiringOrganization", {}).get("name"):
                    parts.append(f"Entreprise : {data['hiringOrganization']['name']}")
                if data.get("jobLocation"):
                    loc = data["jobLocation"]
                    if isinstance(loc, list):
                        loc = loc[0]
                    addr = loc.get("address", {})
                    if isinstance(addr, dict):
                        parts.append(f"Lieu : {addr.get('addressLocality', '')} {addr.get('addressRegion', '')}")
                if data.get("description"):
                    desc = BeautifulSoup(data["description"], "html.parser").get_text(separator="\n", strip=True)
                    parts.append(f"\n{desc}")
                if data.get("qualifications"):
                    parts.append(f"\nQualifications : {data['qualifications']}")
                if data.get("skills"):
                    parts.append(f"Compétences : {data['skills']}")
                text = "\n".join(parts)
                if len(text) > 100:
                    return text[:5000]
        except (json.JSONDecodeError, StopIteration, KeyError):
            continue

    # Try common job posting selectors
    selectors = [
        "[class*='jobDescription']", "[class*='job-description']", "[class*='JobDescription']",
        "[id*='jobDescription']", "[id*='job-description']",
        "[class*='description']", "[class*='offer-description']",
        "[class*='annonce']", "[class*='offre']",
        "article", "[role='main']", "main",
        ".job-details", "#job-details", ".posting-content",
    ]
    for sel in selectors:
        els = soup.select(sel)
        if els:
            text = "\n".join(el.get_text(separator="\n", strip=True) for el in els)
            if len(text) > 150:
                return _clean_text(text)

    # Fallback: body text
    body = soup.find("body")
    text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)
    return _clean_text(text)


def _clean_text(text: str) -> str:
    """Clean extracted text"""
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    # Remove very short lines that are likely navigation
    lines = [l for l in lines if len(l) > 2]
    cleaned = "\n".join(lines)
    return cleaned[:5000] + "..." if len(cleaned) > 5000 else cleaned


@router.get("/scrape/job-offer")
async def scrape_job_offer(url: str):
    """Scrape job offer content from a URL"""
    if not url or not url.startswith("http"):
        return {"success": False, "error": "URL invalide"}

    # Multiple User-Agent strategies
    ua_configs = [
        {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
        },
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9",
        },
        {
            "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
            "Accept": "text/html",
        },
    ]

    last_error = ""
    for headers in ua_configs:
        try:
            status, html = await _scrape_with_headers(url, headers)
            if status == 200 and html:
                text = _extract_job_text(html)
                if text and len(text) > 50:
                    return {"success": True, "text": text, "source_url": url}
                last_error = "Contenu insuffisant extrait de la page"
            else:
                last_error = f"Erreur {status}"
        except httpx.TimeoutException:
            last_error = "La page met trop de temps à répondre"
        except Exception as e:
            last_error = str(e)
            logging.warning(f"Scrape attempt failed: {e}")

    return {
        "success": False,
        "error": f"Impossible d'extraire l'offre. {last_error}. Essayez de copier-coller le texte directement."
    }
