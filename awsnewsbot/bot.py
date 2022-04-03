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

    def run(self) -> None:
        # Get latest entry
        latest = self.db.get_latest()

        if latest is None:
            new_entries = self.feed.entries
        else:
            new_entries = [e for e in self.feed.entries if e["published"] > latest["published"]]

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
