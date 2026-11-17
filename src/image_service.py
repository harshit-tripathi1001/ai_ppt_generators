"""Image retrieval and processing service.

Supports multiple image providers:
1. Wikimedia Commons / Wikipedia (Public Domain / CC - No API key required!)
2. Pexels API (Requires Pexels API Key)
3. Unsplash API (Requires Unsplash Access Key)
4. Pixabay API (Requires Pixabay API Key)

Validates content types, dimensions, and integrity using Pillow.
Always handles network issues or missing credentials gracefully without breaking presentation generation.
"""

import io
import os
import logging
from typing import Optional, NamedTuple
from PIL import Image
import requests

logger = logging.getLogger(__name__)


class ImageResult(NamedTuple):
    """Result container for retrieved and processed image."""
    image_bytes: io.BytesIO
    format: str
    width: int
    height: int
    photographer: str
    attribution_url: str


class ImageService:
    """Service for safely querying and fetching presentation visual assets."""

    def __init__(self, api_key: Optional[str] = None, provider: str = "wikimedia", *args, **kwargs):
        """Initialize with optional API key and provider choice."""
        chosen_provider = kwargs.get("provider", provider)
        chosen_api_key = kwargs.get("api_key", api_key)

        self.provider = (chosen_provider or os.getenv("IMAGE_PROVIDER", "wikimedia")).strip().lower()
        self.api_key = (
            chosen_api_key
            or os.getenv("IMAGE_API_KEY", "")
            or os.getenv("PEXELS_API_KEY", "")
            or os.getenv("UNSPLASH_ACCESS_KEY", "")
            or os.getenv("PIXABAY_API_KEY", "")
        ).strip()
        self.timeout_seconds = 8
        self.max_bytes = 8 * 1024 * 1024  # 8 MB limit

    @property
    def is_configured(self) -> bool:
        """Check if an image provider can be queried."""
        if self.provider in ("wikimedia", "wikipedia", "open", "auto"):
            return True
        return bool(self.api_key)

    def fetch_image_for_query(self, query: str) -> Optional[ImageResult]:
        """Fetch a royalty-free image matching the search term from the active provider.

        Args:
            query: Keyword or short description to search.

        Returns:
            ImageResult if successful and validated, or None.
        """
        if not query or not query.strip():
            return None

        clean_query = query.strip()[:60]

        # 1. Dispatch to chosen provider
        result = None
        if self.provider == "pexels" and self.api_key:
            result = self._fetch_pexels(clean_query)
        elif self.provider == "unsplash" and self.api_key:
            result = self._fetch_unsplash(clean_query)
        elif self.provider == "pixabay" and self.api_key:
            result = self._fetch_pixabay(clean_query)
        else:
            result = self._fetch_wikimedia(clean_query)

        # 2. Smart fallback to Wikimedia Commons if keyed provider failed or lacked key
        if not result and self.provider != "wikimedia":
            logger.info("Provider '%s' unavailable. Falling back to Wikimedia Commons for query '%s'...", self.provider, clean_query)
            result = self._fetch_wikimedia(clean_query)

        return result

    def _fetch_wikimedia(self, query: str) -> Optional[ImageResult]:
        """Fetch a relevant open-access public domain image from Wikimedia / Wikipedia (Zero API Key needed)."""
        headers = {
            "User-Agent": "AIPPTGenerator/1.0 (Educational and Professional Presentation Builder; mailto:info@example.com)"
        }

        # Step 1: Check Wikipedia page image
        try:
            url = "https://en.wikipedia.org/w/api.php"
            params = {
                "action": "query",
                "format": "json",
                "prop": "pageimages",
                "generator": "search",
                "gsrsearch": query,
                "gsrlimit": 3,
                "pithumbsize": 1280
            }
            resp = requests.get(url, params=params, headers=headers, timeout=self.timeout_seconds)
            if resp.status_code == 200:
                pages = resp.json().get("query", {}).get("pages", {})
                for page in pages.values():
                    thumb = page.get("thumbnail", {})
                    img_url = thumb.get("source")
                    if img_url:
                        page_title = page.get("title", "Wikimedia")
                        res = self._download_and_process_image(
                            url=img_url,
                            photographer=f"Wikimedia Commons ({page_title})",
                            attribution_url=f"https://en.wikipedia.org/wiki/{page_title.replace(' ', '_')}"
                        )
                        if res:
                            return res
        except Exception as e:
            logger.debug("Wikipedia page image lookup skipped: %s", e)

        # Step 2: Search Wikimedia Commons files directly
        try:
            commons_url = "https://commons.wikimedia.org/w/api.php"
            c_params = {
                "action": "query",
                "format": "json",
                "generator": "search",
                "gsrsearch": f"{query} filetype:bitmap",
                "gsrnamespace": 6,
                "gsrlimit": 5,
                "prop": "imageinfo",
                "iiprop": "url",
                "iiurlwidth": 1280
            }
            c_resp = requests.get(commons_url, params=c_params, headers=headers, timeout=self.timeout_seconds)
            if c_resp.status_code == 200:
                c_pages = c_resp.json().get("query", {}).get("pages", {})
                for c_page in c_pages.values():
                    infos = c_page.get("imageinfo", [])
                    if infos:
                        u = infos[0].get("thumburl") or infos[0].get("url")
                        if u and any(u.lower().endswith(ext) or (ext + "?") in u.lower() for ext in [".jpg", ".jpeg", ".png", ".webp"]):
                            c_title = c_page.get("title", "Wikimedia Commons").replace("File:", "")
                            res = self._download_and_process_image(
                                url=u,
                                photographer=f"Wikimedia ({c_title[:30]})",
                                attribution_url=infos[0].get("descriptionurl", "https://commons.wikimedia.org")
                            )
                            if res:
                                return res
        except Exception as e:
            logger.warning("Wikimedia Commons files search failed for '%s': %s", query, e)

        return None

    def _fetch_pexels(self, query: str) -> Optional[ImageResult]:
        """Fetch an image using Pexels REST API."""
        try:
            headers = {
                "Authorization": self.api_key,
                "User-Agent": "AIPPTGenerator/1.0"
            }
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape"
            }
            resp = requests.get("https://api.pexels.com/v1/search", headers=headers, params=params, timeout=self.timeout_seconds)
            if resp.status_code != 200:
                logger.warning("Pexels API status %s for '%s'", resp.status_code, query)
                return None

            data = resp.json()
            photos = data.get("photos", [])
            if not photos:
                return None

            photo = photos[0]
            src_url = photo.get("src", {}).get("large") or photo.get("src", {}).get("medium")
            if not src_url:
                return None

            return self._download_and_process_image(
                url=src_url,
                photographer=photo.get("photographer", "Pexels Contributor"),
                attribution_url=photo.get("url", "https://www.pexels.com")
            )
        except Exception as e:
            logger.warning("Pexels fetch error: %s", e)
            return None

    def _fetch_unsplash(self, query: str) -> Optional[ImageResult]:
        """Fetch an image using Unsplash REST API."""
        try:
            headers = {
                "Authorization": f"Client-ID {self.api_key}",
                "User-Agent": "AIPPTGenerator/1.0"
            }
            params = {
                "query": query,
                "per_page": 1,
                "orientation": "landscape"
            }
            resp = requests.get("https://api.unsplash.com/search/photos", headers=headers, params=params, timeout=self.timeout_seconds)
            if resp.status_code != 200:
                return None

            data = resp.json()
            results = data.get("results", [])
            if not results:
                return None

            photo = results[0]
            src_url = photo.get("urls", {}).get("regular") or photo.get("urls", {}).get("small")
            if not src_url:
                return None

            user_name = photo.get("user", {}).get("name", "Unsplash Contributor")
            return self._download_and_process_image(
                url=src_url,
                photographer=user_name,
                attribution_url=photo.get("links", {}).get("html", "https://unsplash.com")
            )
        except Exception as e:
            logger.warning("Unsplash fetch error: %s", e)
            return None

    def _fetch_pixabay(self, query: str) -> Optional[ImageResult]:
        """Fetch an image using Pixabay REST API."""
        try:
            params = {
                "key": self.api_key,
                "q": query,
                "image_type": "photo",
                "orientation": "horizontal",
                "per_page": 3
            }
            resp = requests.get("https://pixabay.com/api/", params=params, timeout=self.timeout_seconds)
            if resp.status_code != 200:
                return None

            data = resp.json()
            hits = data.get("hits", [])
            if not hits:
                return None

            hit = hits[0]
            src_url = hit.get("largeImageURL") or hit.get("webformatURL")
            if not src_url:
                return None

            return self._download_and_process_image(
                url=src_url,
                photographer=hit.get("user", "Pixabay Contributor"),
                attribution_url=hit.get("pageURL", "https://pixabay.com")
            )
        except Exception as e:
            logger.warning("Pixabay fetch error: %s", e)
            return None

    def _download_and_process_image(self, url: str, photographer: str, attribution_url: str) -> Optional[ImageResult]:
        """Download raw image stream, sanitize with Pillow, and convert to PowerPoint-ready JPEG."""
        try:
            headers = {"User-Agent": "AIPPTGenerator/1.0"}
            img_resp = requests.get(url, headers=headers, timeout=self.timeout_seconds, stream=True)
            if img_resp.status_code != 200:
                return None

            raw_bytes = io.BytesIO()
            downloaded = 0
            for chunk in img_resp.iter_content(chunk_size=16384):
                downloaded += len(chunk)
                if downloaded > self.max_bytes:
                    return None
                raw_bytes.write(chunk)

            raw_bytes.seek(0)

            # Pillow validation
            with Image.open(raw_bytes) as pil_img:
                pil_img.verify()

            raw_bytes.seek(0)
            with Image.open(raw_bytes) as pil_img:
                w, h = pil_img.size
                processed_bytes = io.BytesIO()
                if pil_img.mode in ("RGBA", "P", "LA"):
                    rgb_img = pil_img.convert("RGB")
                    rgb_img.save(processed_bytes, format="JPEG", quality=88)
                else:
                    pil_img.save(processed_bytes, format="JPEG", quality=88)
                processed_bytes.seek(0)

                return ImageResult(
                    image_bytes=processed_bytes,
                    format="JPEG",
                    width=w,
                    height=h,
                    photographer=photographer,
                    attribution_url=attribution_url
                )
        except Exception as e:
            logger.warning("Error processing image from '%s': %s", url, e)
            return None
