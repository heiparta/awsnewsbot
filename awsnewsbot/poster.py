from requests_oauthlib import OAuth1
from typing import List, Optional, Dict, Any
from awsnewsbot.rss import FeedEntry

import logging
import requests

TWEET_URL = "https://api.twitter.com/2/tweets"


class Poster:
    def __init__(self, api_key: str, api_secret: str, access_token: str, access_token_secret: str):
        self.auth = OAuth1(api_key, api_secret, access_token, access_token_secret)

    def post_entries(self, entries: List[FeedEntry]) -> None:
        if not entries:
            return
        previous_id: Optional[str] = None
        for i, entry in enumerate(entries, start=1):
            thread_suffix = ""
            if len(entries) > 1:
                thread_suffix = f" {i}/{len(entries)}"
            payload: Dict[str, Any] = {
                "text": f"{entry['title']} {entry['link']}{thread_suffix}",
            }
            if previous_id:
                payload["reply"] = {
                    "in_reply_to_tweet_id": previous_id,
                }
            response = requests.post(auth=self.auth, url=TWEET_URL, json=payload)
            if not response.ok:
                logging.debug("Post response: %s: %s", response, response.json())
            response.raise_for_status()
            previous_id = response.json()["data"]["id"]
