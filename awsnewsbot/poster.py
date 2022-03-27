from typing import List
from awsnewsbot.rss import FeedEntry


class Poster:
    def __init__(self):
        pass

    def post_entries(self, entries: List[FeedEntry]) -> None:
        print(len(entries))
