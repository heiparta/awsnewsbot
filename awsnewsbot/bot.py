#!/usr/bin/env python3

import boto3
import os
from typing import Any, Dict
from awsnewsbot.db import DatabaseBase, FileDatabase, ParameterStoreDatabase
from awsnewsbot.rss import FeedReader
from awsnewsbot.poster import Poster

import logging


def init_logging() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logging.getLogger("boto3").setLevel(logging.WARNING)
    logging.getLogger("boto-core").setLevel(logging.WARNING)
    return logger


def get_bot_ssm_params(auth_prefix: str, feed_prefix: str, feed_id: str) -> Dict[str, str]:
    ssm = boto3.client('ssm')
    params = {}
    params["api_key"] = ssm.get_parameter(Name=f"{auth_prefix}/consumer_key", WithDecryption=True)["Parameter"]["Value"]
    params["api_secret"] = ssm.get_parameter(Name=f"{auth_prefix}/consumer_secret", WithDecryption=True)["Parameter"]["Value"]
    params["access_token"] = ssm.get_parameter(Name=f"{feed_prefix}/{feed_id}/access_key", WithDecryption=True)["Parameter"]["Value"]
    params["access_token_secret"] = ssm.get_parameter(
        Name=f"{feed_prefix}/{feed_id}/access_key_secret", WithDecryption=True)["Parameter"]["Value"]
    params["feed_url"] = ssm.get_parameter(Name=f"{feed_prefix}/{feed_id}/url")["Parameter"]["Value"]
    return params


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
        new_entries = new_entries[:2]

        # Post new entries
        self.poster.post_entries(new_entries)
        self.db.add_entries(new_entries)


def handler(event: Dict[str, str] = None, context: Any = None) -> None:
    logger = init_logging()
    logger.info("Starting handler")
    params = get_bot_ssm_params(
        os.environ["AUTH_PREFIX"],
        os.environ["FEED_PREFIX"],
        os.environ["FEED_ID"],
    )
    feed = FeedReader(params["feed_url"])
    db = ParameterStoreDatabase(os.environ["FEED_PREFIX"], os.environ["FEED_ID"])
    poster = Poster(params["api_key"], params["api_secret"], params["access_token"], params["access_token_secret"])
    bot = Bot(feed, db, poster)
    bot.run()


def main() -> None:

    feed = FeedReader("./tests/data_aws.xml")
    db = FileDatabase()

    api_key = os.environ.get("CONSUMER_KEY")
    api_secret = os.environ.get("CONSUMER_SECRET")
    access_token = os.environ.get("ACCESS_TOKEN")
    access_token_secret = os.environ.get("ACCESS_TOKEN_SECRET")
    poster = Poster(api_key, api_secret, access_token, access_token_secret)

    bot = Bot(feed, db, poster)
    bot.run()


if __name__ == "__main__":
    handler({}, {})
