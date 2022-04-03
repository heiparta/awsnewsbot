#!/usr/bin/env python3

import os
from awsnewsbot.db import DatabaseBase, FileDatabase
from awsnewsbot.rss import FeedReader
from awsnewsbot.poster import Poster


class Bot:
    def __init__(self, feed: FeedReader, db: DatabaseBase, poster: Poster) -> None:
        self.feed = feed
        self.db = db
        self.poster = poster

    def run(self, max_new_entries: int = 5) -> None:
        # Get existing entries
        existing = [e['id'] for e in self.db.get_entries()]

        new_entries = []
        for entry in self.feed.entries:
            if entry["id"] in existing:
                # Any entries appended BEFORE an existing entry also exist, so clear them
                new_entries.clear()
                continue
            new_entries.append(entry)
            if len(new_entries) >= max_new_entries:
                break

        # Post new entries
        self.poster.post_entries(new_entries)
        self.db.add_entries(new_entries)

def main():

    feed = FeedReader("./tests/data_aws.xml")
    db = FileDatabase()

    api_key = os.environ.get("CONSUMER_KEY")
    api_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    poster = Poster(api_key, api_secret, access_token, access_token_secret)

    bot = Bot(feed, db, poster)
    feed.entries = feed.entries
    bot.run()

if __name__ == "__main__":
    main()