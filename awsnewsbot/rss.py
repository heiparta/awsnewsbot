from datetime import datetime
from time import mktime
from typing import List, TypedDict

import feedparser


class FeedEntry(TypedDict):
    id: str
    title: str
    summary: str
    link: str
    published: str


class FeedReader:
    def __init__(self, feed: str) -> None:
        self._data = feedparser.parse(feed)
        self.entries = self._get_entries()

    def _get_entries(self) -> List[FeedEntry]:
        entries = []
        for parsed_entry in self._data.get("entries", []):
            entry: FeedEntry = {
                "id": parsed_entry["id"],
                "title": parsed_entry["title"],
                "link": parsed_entry["link"],
                "published": str(datetime.fromtimestamp(
                    mktime(parsed_entry["published_parsed"]))
                ),
            }
            entries.append(entry)
        # We want to handle entries in ascending order
        entries.sort(key=lambda e: (e['published'], e['id']))
        return entries
