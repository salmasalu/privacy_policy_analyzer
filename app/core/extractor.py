import requests
from bs4 import BeautifulSoup
import PyPDF2

# HEADERS — rotate user agents to avoid blocks

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

# Tags to remove before extracting text
REMOVE_TAGS = [
    "script", "style", "nav", "footer", "header",
    "aside", "noscript", "button", "form", "input",
    "svg", "img", "figure", "figcaption", "iframe"
]

# Tags most likely to contain policy text
CONTENT_TAGS = [
    "article", "main", "section", "div",
    "p", "li", "td", "span"
]


def extract_text_from_url(url: str) -> str:
    """
    Extracts clean text from a privacy policy URL.
    
    Strategy:
    1. Try targeted extraction from content tags first
    2. Fall back to full page extraction
    3. Increase limit to 10000 chars to capture more clauses
    
    Design decision:
    - 10000 char limit balances coverage vs DeBERTa processing time
    - Targeting content tags reduces navigation/menu noise
    - Chrome user-agent reduces bot-blocking on major sites
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove noise tags
        for tag in soup(REMOVE_TAGS):
            tag.decompose()

        # Try to find main content area first
        content = None
        for selector in ["main", "article", '[role="main"]', ".privacy-policy", "#privacy", ".content", "#content"]:
            content = soup.select_one(selector)
            if content:
                break

        if content:
            text = content.get_text(separator=" ")
        else:
            # Fall back to full page
            text = soup.get_text(separator=" ")

        # Clean whitespace
        clean = " ".join(text.split())

        # Return up to 10000 chars for better coverage
        return clean[:10000]
    except Exception as e:
       raise Exception(
        f"Could not extract from this URL. "
        f"This site may use JavaScript rendering. "
        f"Please use 'Paste Text' option instead. ({str(e)})"
    )

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from all pages of a PDF file."""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + " "
        return text.strip()[:10000]
    except Exception as e:
        return f"ERROR: Unable to extract from PDF → {str(e)}"


def extract_text_from_input(raw_text: str) -> str:
    """Clean and return pasted raw text."""
    return raw_text.strip()