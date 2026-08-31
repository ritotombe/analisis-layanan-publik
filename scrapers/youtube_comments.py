"""
YouTube Comments Scraper — user-generated content dari komentar video YouTube.

Dua mode:
1. Dengan API key: YouTube Data API v3 (lebih reliable)
2. Tanpa API key: fallback sederhana via web scraping (terbatas)
"""

from typing import Optional
from urllib.parse import quote_plus

from bs4 import BeautifulSoup

from scrapers.base import BaseScraper, Article
from config.settings import YOUTUBE_API_KEY


class YouTubeCommentsScraper(BaseScraper):
    """Scraper komentar YouTube."""

    SEARCH_API = "https://www.googleapis.com/youtube/v3/search"
    COMMENTS_API = "https://www.googleapis.com/youtube/v3/commentThreads"

    def __init__(self):
        super().__init__(source_type="youtube", delay=1)
        self.has_api_key = bool(YOUTUBE_API_KEY)
        if self.has_api_key:
            self.logger.info("YouTube API key tersedia ✓")
        else:
            self.logger.info("YouTube API key tidak ada — menggunakan mode terbatas")

    def _search_videos_api(
        self, keyword: str, max_results: int = 10
    ) -> list[dict]:
        """Cari video via YouTube Data API v3."""
        params = {
            "part": "snippet",
            "q": keyword,
            "type": "video",
            "regionCode": "ID",
            "relevanceLanguage": "id",
            "maxResults": min(max_results, 50),
            "order": "relevance",
            "key": YOUTUBE_API_KEY,
        }
        response = self._fetch(self.SEARCH_API, params=params)
        if not response:
            return []

        data = response.json()
        videos = []
        for item in data.get("items", []):
            videos.append({
                "video_id": item["id"]["videoId"],
                "title": item["snippet"]["title"],
                "channel": item["snippet"]["channelTitle"],
                "published": item["snippet"]["publishedAt"],
                "description": item["snippet"].get("description", ""),
            })
        return videos

    def _get_comments_api(
        self, video_id: str, max_comments: int = 50
    ) -> list[dict]:
        """Ambil komentar video via YouTube Data API v3."""
        params = {
            "part": "snippet",
            "videoId": video_id,
            "maxResults": min(max_comments, 100),
            "order": "relevance",
            "textFormat": "plainText",
            "key": YOUTUBE_API_KEY,
        }
        response = self._fetch(self.COMMENTS_API, params=params)
        if not response:
            return []

        data = response.json()
        comments = []
        for item in data.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "text": snippet["textDisplay"],
                "author": snippet["authorDisplayName"],
                "date": snippet["publishedAt"],
                "likes": snippet.get("likeCount", 0),
            })
        return comments

    def _search_videos_web(
        self, keyword: str, max_results: int = 5
    ) -> list[dict]:
        """Fallback: cari video via web scraping (tanpa API key)."""
        encoded = quote_plus(keyword)
        url = f"https://www.youtube.com/results?search_query={encoded}&sp=EgIIAQ%253D%253D"
        response = self._fetch(url)
        if not response:
            return []

        # YouTube render client-side, jadi kita parse dari initial data
        # Ini terbatas tapi bisa dapat beberapa video
        import re
        import json

        videos = []
        match = re.search(r"var ytInitialData = ({.*?});", response.text)
        if match:
            try:
                data = json.loads(match.group(1))
                contents = (
                    data.get("contents", {})
                    .get("twoColumnSearchResultsRenderer", {})
                    .get("primaryContents", {})
                    .get("sectionListRenderer", {})
                    .get("contents", [{}])[0]
                    .get("itemSectionRenderer", {})
                    .get("contents", [])
                )
                for item in contents[:max_results]:
                    renderer = item.get("videoRenderer", {})
                    if not renderer:
                        continue
                    video_id = renderer.get("videoId", "")
                    title_runs = renderer.get("title", {}).get("runs", [])
                    title = title_runs[0]["text"] if title_runs else ""
                    if video_id and title:
                        videos.append({
                            "video_id": video_id,
                            "title": title,
                            "channel": (
                                renderer.get("ownerText", {})
                                .get("runs", [{}])[0]
                                .get("text", "")
                            ),
                            "published": "",
                            "description": "",
                        })
            except (json.JSONDecodeError, KeyError, IndexError):
                pass

        return videos

    def scrape(
        self,
        keywords: list[str],
        days_back: int = 365,
        max_results: int = 30,
    ) -> list[Article]:
        """
        Scrape komentar YouTube dari video yang relevan.
        
        Strategi:
        1. Cari video berdasarkan keyword
        2. Ambil komentar dari video yang ditemukan
        3. Setiap komentar jadi satu Article
        """
        articles = []
        seen_videos = set()

        for i, keyword in enumerate(keywords, 1):
            self.logger.info(
                f"[{i}/{len(keywords)}] YouTube keyword: '{keyword}'"
            )

            # Cari video
            if self.has_api_key:
                videos = self._search_videos_api(keyword, max_results=5)
            else:
                videos = self._search_videos_web(keyword, max_results=3)

            for video in videos:
                vid = video["video_id"]
                if vid in seen_videos:
                    continue
                seen_videos.add(vid)

                self.logger.info(f"  Video: {video['title'][:60]}...")

                # Ambil komentar
                if self.has_api_key:
                    comments = self._get_comments_api(vid, max_comments=30)
                else:
                    # Tanpa API key, kita hanya simpan info video
                    comments = []
                    self.logger.info(
                        "  → Tanpa API key, komentar tidak bisa diambil"
                    )

                if comments:
                    # Bundle komentar per video sebagai satu Article
                    comments_text = "\n---\n".join(
                        f"[{c['author']}] (♥ {c['likes']}): {c['text']}"
                        for c in comments
                    )
                    article = Article(
                        title=f"Komentar: {video['title']}",
                        body=comments_text,
                        url=f"https://www.youtube.com/watch?v={vid}",
                        source_type="youtube",
                        source_name=f"YouTube - {video['channel']}",
                        source_category="user_generated",
                        published_date=video.get("published", ""),
                        extra_data={
                            "keyword": keyword,
                            "video_id": vid,
                            "channel": video["channel"],
                            "comment_count": len(comments),
                        },
                    )
                    articles.append(article)
                else:
                    # Tanpa komentar, simpan video sebagai referensi
                    article = Article(
                        title=video["title"],
                        body=video.get("description", ""),
                        url=f"https://www.youtube.com/watch?v={vid}",
                        source_type="youtube",
                        source_name=f"YouTube - {video['channel']}",
                        source_category="user_generated",
                        published_date=video.get("published", ""),
                        extra_data={
                            "keyword": keyword,
                            "video_id": vid,
                            "channel": video["channel"],
                        },
                    )
                    articles.append(article)

            self._rate_limit()

        self.logger.info(f"Total: {len(articles)} items dari YouTube")
        return articles
