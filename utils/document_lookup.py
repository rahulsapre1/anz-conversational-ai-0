from pathlib import Path
from typing import Dict, Optional

_METADATA_CACHE: Dict[str, Optional[str]] = {}


def _load_metadata_map() -> Dict[str, Optional[str]]:
    if _METADATA_CACHE:
        return _METADATA_CACHE

    base_dir = Path(__file__).resolve().parent.parent / "scraped_docs"
    if not base_dir.exists():
        return _METADATA_CACHE

    for path in base_dir.glob("*.md"):
        try:
            title = None
            source_url = None
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped.startswith("Title:"):
                        title = stripped.replace("Title:", "").strip()
                    elif stripped.startswith("Source URL:"):
                        source_url = stripped.replace("Source URL:", "").strip()
                    elif stripped.startswith("Original URL:") and not source_url:
                        source_url = stripped.replace("Original URL:", "").strip()
                    if title and source_url:
                        break
            _METADATA_CACHE[path.name] = source_url
        except Exception:
            _METADATA_CACHE[path.name] = None

    return _METADATA_CACHE


def get_url_for_filename(filename: Optional[str]) -> Optional[str]:
    if not filename:
        return None
    metadata_map = _load_metadata_map()
    return metadata_map.get(filename)
