#!/usr/bin/env python3

from awsnewsbot.db import DatabaseBase, FileDatabase
from awsnewsbot.rss import FeedReader
from awsnewsbot.poster import Poster

from unittest.mock import MagicMock


class Bot:
    def __init__(self, feed: FeedReader, db: DatabaseBase, poster: Poster) -> None:
        self.feed = feed
        self.db = db
        self.poster = poster

    def run(self) -> None:
        # Get existing entries
        existing = [e['id'] for e in self.db.get_entries()]

        new_entries = []
        for entry in self.feed.entries:
            if entry["id"] in existing:
                # Any entries appended BEFORE an existing entry also exist, so clear them
                new_entries.clear()
                continue
            new_entries.append(entry)

        # Post new entries
        self.poster.post_entries(new_entries)
        self.db.add_entries(new_entries)


if __name__ == "__main__":
    feed = FeedReader("./tests/data_aws.xml")
    db = FileDatabase()
    poster = MagicMock()

    bot = Bot(feed, db, poster)
    feed.entries = feed.entries[:1]
    bot.run()
