from requests_oauthlib import OAuth1
from typing import List, Optional, Dict, Any
from awsnewsbot.rss import FeedEntry

import logging
import requests

TWEET_URL = "https://api.twitter.com/2/tweets"

logger = logging.getLogger(__name__)

class Poster:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        self.auth = OAuth1(api_key, api_secret, access_token, access_token_secret)

    def post_entries(self, entries: List[FeedEntry]) -> None:
        if not entries:
            return
        root_post_id: Optional[str] = None
        for i, entry in enumerate(entries, start=1):
            thread_suffix = ""
            if len(entries) > 1:
                thread_suffix = f" {i}/{len(entries)}"
            payload: Dict[str, Any] = {
                "text": f"{entry['title']} {entry['link']}{thread_suffix} #aws",
            }
            if root_post_id:
                payload["reply"] = {
                    "in_reply_to_tweet_id": root_post_id,
                }
            response = requests.post(auth=self.auth, url=TWEET_URL, json=payload)
            if not response.ok:
                logger.debug("Post response: %s: %s", response, response.json())
            elif response.status_code == 403:
                if "duplicate content" in response.json()["detail"]:
                    logger.info(f"Ignoring duplicate post: {payload}")
                    continue
            response.raise_for_status()
            if root_post_id is None:
                root_post_id = response.json()["data"]["id"]
