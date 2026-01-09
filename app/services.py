"""
Service layer for Unsplash API integration and data processing.

Provides functions to fetch Nigerian tourism images from Unsplash API with
comprehensive error handling, caching, and retry mechanisms. Implements
production-ready patterns for external API integration with observability.
"""

import logging
import os
import time
from functools import lru_cache
from typing import Any, Optional
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, Timeout
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class UnsplashAPIError(Exception):
    """Base exception for Unsplash API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, **context):
        super().__init__(message)
        self.status_code = status_code
        self.context = context


class UnsplashRateLimitError(UnsplashAPIError):
    """Exception raised when Unsplash API rate limit is exceeded."""

    pass


class UnsplashService:
    """
    Service for interacting with Unsplash API.

    Provides methods to fetch Nigerian tourism images with built-in retry logic,
    caching, and comprehensive error handling. Implements connection pooling and
    rate limit handling for production reliability.
    """

    BASE_URL = "https://api.unsplash.com"
    DEFAULT_TIMEOUT = 10
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 0.5
    CACHE_TTL = 3600  # 1 hour

    def __init__(
        self,
        access_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES
    ):
        """
        Initialize Unsplash service with configuration.

        Args:
            access_key: Unsplash API access key. If None, reads from UNSPLASH_ACCESS_KEY env var
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts for failed requests

        Raises:
            ValueError: If access_key is not provided and not in environment
        """
        self.access_key = access_key or os.getenv('UNSPLASH_ACCESS_KEY')
        if not self.access_key:
            raise ValueError(
                "Unsplash access key is required. Set UNSPLASH_ACCESS_KEY "
                "environment variable or pass access_key parameter."
            )

        self.timeout = timeout
        self.session = self._create_session(max_retries)

        logger.info(
            "UnsplashService initialized",
            extra={
                'timeout': timeout,
                'max_retries': max_retries,
                'base_url': self.BASE_URL
            }
        )

    def _create_session(self, max_retries: int) -> requests.Session:
        """
        Create requests session with retry strategy and connection pooling.

        Args:
            max_retries: Maximum number of retry attempts

        Returns:
            Configured requests Session instance
        """
        session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=self.BACKOFF_FACTOR,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )

        session.mount("https://", adapter)
        session.mount("http://", adapter)

        return session

    def _make_request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Make authenticated request to Unsplash API.

        Args:
            endpoint: API endpoint path
            params: Query parameters

        Returns:
            JSON response data

        Raises:
            UnsplashRateLimitError: If rate limit is exceeded
            UnsplashAPIError: For other API errors
            RequestException: For network-related errors
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = {
            "Authorization": f"Client-ID {self.access_key}",
            "Accept-Version": "v1"
        }

        request_params = params or {}

        logger.debug(
            "Making Unsplash API request",
            extra={
                'endpoint': endpoint,
                'params': request_params
            }
        )

        start_time = time.time()

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=request_params,
                timeout=self.timeout
            )

            elapsed_time = time.time() - start_time

            logger.info(
                "Unsplash API request completed",
                extra={
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'elapsed_time': f"{elapsed_time:.2f}s"
                }
            )

            if response.status_code == 429:
                retry_after = response.headers.get('Retry-After', '60')
                raise UnsplashRateLimitError(
                    "Unsplash API rate limit exceeded",
                    status_code=429,
                    retry_after=retry_after
                )

            if response.status_code == 401:
                raise UnsplashAPIError(
                    "Invalid Unsplash API access key",
                    status_code=401
                )

            if response.status_code == 403:
                raise UnsplashAPIError(
                    "Access forbidden. Check API key permissions",
                    status_code=403
                )

            if not response.ok:
                raise UnsplashAPIError(
                    f"Unsplash API request failed: {response.text}",
                    status_code=response.status_code
                )

            return response.json()

        except Timeout as e:
            logger.error(
                "Unsplash API request timeout",
                exc_info=True,
                extra={
                    'endpoint': endpoint,
                    'timeout': self.timeout
                }
            )
            raise UnsplashAPIError(
                f"Request timeout after {self.timeout}s",
                timeout=self.timeout
            ) from e

        except RequestException as e:
            logger.error(
                "Unsplash API request failed",
                exc_info=True,
                extra={
                    'endpoint': endpoint,
                    'error_type': type(e).__name__
                }
            )
            raise

    @lru_cache(maxsize=128)
    def search_photos(
        self,
        query: str,
        per_page: int = 10,
        page: int = 1,
        orientation: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Search for photos on Unsplash.

        Results are cached to minimize API calls and improve performance.

        Args:
            query: Search query string
            per_page: Number of results per page (max 30)
            page: Page number
            orientation: Photo orientation ('landscape', 'portrait', 'squarish')

        Returns:
            List of photo data dictionaries

        Raises:
            ValueError: If parameters are invalid
            UnsplashAPIError: If API request fails
        """
        if per_page < 1 or per_page > 30:
            raise ValueError("per_page must be between 1 and 30")

        if page < 1:
            raise ValueError("page must be >= 1")

        if orientation and orientation not in ['landscape', 'portrait', 'squarish']:
            raise ValueError(
                "orientation must be 'landscape', 'portrait', or 'squarish'"
            )

        params = {
            'query': query,
            'per_page': per_page,
            'page': page
        }

        if orientation:
            params['orientation'] = orientation

        logger.info(
            "Searching Unsplash photos",
            extra={
                'query': query,
                'per_page': per_page,
                'page': page,
                'orientation': orientation
            }
        )

        try:
            data = self._make_request('/search/photos', params)
            results = data.get('results', [])

            logger.info(
                "Photo search completed",
                extra={
                    'query': query,
                    'total_results': data.get('total', 0),
                    'returned_results': len(results)
                }
            )

            return results

        except Exception as e:
            logger.error(
                "Photo search failed",
                exc_info=True,
                extra={
                    'query': query,
                    'error': str(e)
                }
            )
            raise

    def get_nigerian_tourism_images(
        self,
        count: int = 10,
        orientation: str = 'landscape'
    ) -> list[dict[str, Any]]:
        """
        Fetch Nigerian tourism images from Unsplash.

        Searches for images related to Nigerian tourism, landscapes, and culture.
        Implements fallback queries if primary search returns insufficient results.

        Args:
            count: Number of images to fetch (max 30)
            orientation: Image orientation preference

        Returns:
            List of processed image data dictionaries with keys:
                - id: Unsplash photo ID
                - url: Regular size image URL
                - thumb_url: Thumbnail image URL
                - alt_description: Alt text for accessibility
                - photographer: Photographer name
                - photographer_url: Photographer profile URL
                - download_location: URL for tracking downloads

        Raises:
            ValueError: If count is invalid
            UnsplashAPIError: If API requests fail
        """
        if count < 1 or count > 30:
            raise ValueError("count must be between 1 and 30")

        logger.info(
            "Fetching Nigerian tourism images",
            extra={
                'count': count,
                'orientation': orientation
            }
        )

        queries = [
            'Nigeria tourism',
            'Nigeria landscape',
            'Nigerian culture',
            'Lagos Nigeria',
            'Abuja Nigeria'
        ]

        all_images = []
        images_per_query = max(count // len(queries), 3)

        for query in queries:
            if len(all_images) >= count:
                break

            try:
                results = self.search_photos(
                    query=query,
                    per_page=images_per_query,
                    orientation=orientation
                )

                processed = self._process_image_results(results)
                all_images.extend(processed)

                logger.debug(
                    "Query results processed",
                    extra={
                        'query': query,
                        'results_count': len(processed)
                    }
                )

            except UnsplashAPIError as e:
                logger.warning(
                    f"Failed to fetch images for query: {query}",
                    extra={
                        'query': query,
                        'error': str(e)
                    }
                )
                continue

        unique_images = self._deduplicate_images(all_images)
        final_images = unique_images[:count]

        logger.info(
            "Nigerian tourism images fetched",
            extra={
                'requested_count': count,
                'fetched_count': len(final_images)
            }
        )

        return final_images

    def _process_image_results(
        self,
        results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Process raw Unsplash API results into standardized format.

        Args:
            results: Raw API response results

        Returns:
            List of processed image dictionaries
        """
        processed = []

        for photo in results:
            try:
                processed_photo = {
                    'id': photo.get('id', ''),
                    'url': photo.get('urls', {}).get('regular', ''),
                    'thumb_url': photo.get('urls', {}).get('thumb', ''),
                    'alt_description': photo.get('alt_description') or photo.get('description') or 'Nigerian tourism image',
                    'photographer': photo.get('user', {}).get('name', 'Unknown'),
                    'photographer_url': photo.get('user', {}).get('links', {}).get('html', ''),
                    'download_location': photo.get('links', {}).get('download_location', ''),
                    'width': photo.get('width', 0),
                    'height': photo.get('height', 0)
                }

                if processed_photo['url']:
                    processed.append(processed_photo)

            except Exception as e:
                logger.warning(
                    "Failed to process photo",
                    extra={
                        'photo_id': photo.get('id', 'unknown'),
                        'error': str(e)
                    }
                )
                continue

        return processed

    def _deduplicate_images(
        self,
        images: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Remove duplicate images based on ID.

        Args:
            images: List of image dictionaries

        Returns:
            Deduplicated list of images
        """
        seen_ids = set()
        unique_images = []

        for image in images:
            image_id = image.get('id')
            if image_id and image_id not in seen_ids:
                seen_ids.add(image_id)
                unique_images.append(image)

        return unique_images

    def trigger_download(self, download_location: str) -> None:
        """
        Trigger download tracking for Unsplash photo.

        Required by Unsplash API guidelines to track photo usage.

        Args:
            download_location: Download location URL from photo data

        Raises:
            UnsplashAPIError: If tracking request fails
        """
        if not download_location:
            logger.warning("No download location provided for tracking")
            return

        try:
            logger.debug(
                "Triggering download tracking",
                extra={'download_location': download_location}
            )

            response = self.session.get(
                download_location,
                headers={"Authorization": f"Client-ID {self.access_key}"},
                timeout=self.timeout
            )

            if response.ok:
                logger.info("Download tracking successful")
            else:
                logger.warning(
                    "Download tracking failed",
                    extra={'status_code': response.status_code}
                )

        except Exception as e:
            logger.error(
                "Download tracking error",
                exc_info=True,
                extra={'error': str(e)}
            )

    def close(self) -> None:
        """Close the requests session and cleanup resources."""
        if self.session:
            self.session.close()
            logger.info("UnsplashService session closed")


def get_unsplash_service() -> UnsplashService:
    """
    Factory function to create UnsplashService instance.

    Returns:
        Configured UnsplashService instance

    Raises:
        ValueError: If UNSPLASH_ACCESS_KEY is not set
    """
    return UnsplashService()