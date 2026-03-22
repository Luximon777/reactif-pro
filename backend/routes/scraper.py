from fastapi import APIRouter
import httpx
from bs4 import BeautifulSoup
import re
import logging

router = APIRouter()


@router.get("/scrape/job-offer")
async def scrape_job_offer(url: str):
    """Scrape job offer content from a URL"""
    if not url or not url.startswith("http"):
        return {"success": False, "error": "URL invalide"}

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                return {"success": False, "error": f"Impossible d'accéder à la page (erreur {resp.status_code})"}

            soup = BeautifulSoup(resp.text, "html.parser")

            # Remove scripts, styles, nav, footer, header
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "iframe"]):
                tag.decompose()

            # Try to find job-specific content areas
            text = ""
            # Common job posting containers
            selectors = [
                "article", "[class*='job']", "[class*='offer']", "[class*='description']",
                "[class*='annonce']", "[class*='offre']", "[id*='job']", "[id*='offer']",
                "main", "[role='main']"
            ]
            for sel in selectors:
                els = soup.select(sel)
                if els:
                    text = "\n".join(el.get_text(separator="\n", strip=True) for el in els)
                    if len(text) > 200:
                        break

            # Fallback: get body text
            if len(text) < 200:
                body = soup.find("body")
                text = body.get_text(separator="\n", strip=True) if body else soup.get_text(separator="\n", strip=True)

            # Clean up text
            lines = [line.strip() for line in text.split("\n") if line.strip()]
            cleaned = "\n".join(lines)

            # Limit to reasonable size
            if len(cleaned) > 5000:
                cleaned = cleaned[:5000] + "..."

            if len(cleaned) < 50:
                return {"success": False, "error": "Impossible d'extraire le contenu de l'offre depuis cette page"}

            return {"success": True, "text": cleaned, "source_url": url}

    except httpx.TimeoutException:
        return {"success": False, "error": "La page met trop de temps à répondre"}
    except Exception as e:
        logging.warning(f"Job offer scrape error: {e}")
        return {"success": False, "error": "Erreur lors de la récupération de l'offre"}
