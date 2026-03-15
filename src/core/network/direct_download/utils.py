from core.utils.logging.logs import consoleLog
from urllib.parse import urlparse, unquote
from typing import Optional
import requests
import os

def sanitize_filename(name: str) -> str:
    # Remove or replace dangerous characters
    keepchars = (" ", ".", "_", "-")
    cleaned = "".join(c for c in name if c.isalnum() or c in keepchars).strip()
    while "  " in cleaned:
        cleaned = cleaned.replace("  ", " ")
    return cleaned or "download"


def extract_filename_from_url(url: str) -> Optional[str]:
    parsed = urlparse(url)
    path = unquote(parsed.path)
    basename = os.path.basename(path)
    if basename and "." in basename and len(basename) < 256:
        return basename
    return None


def detect_filename_from_headers(url: str, user_agent: str) -> Optional[str]:
    try:
        resp = requests.head(
            url,
            headers={"User-Agent": user_agent},
            allow_redirects=True,
            timeout=15,
        )
        cd = resp.headers.get("content-disposition", "")
        if "filename=" in cd:
            parts = cd.split("filename=")
            if len(parts) > 1:
                fname = parts[-1].strip().strip('"').strip("'")
                if fname:
                    return fname
    except Exception as e:
        consoleLog(f"Exception while retrieving filename from headers: {e}")
    return None

def format_size(size_bytes: int) -> str:
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if abs(size_bytes) < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PiB"
