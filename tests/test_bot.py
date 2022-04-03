from tempfile import NamedTemporaryFile
from unittest.mock import MagicMock

import boto3
import pytest

from awsnewsbot.bot import Bot
from awsnewsbot.db import FileDatabase, ParameterStoreDatabase
from awsnewsbot.rss import FeedReader

@pytest.fixture
def test_db_file() -> str:
    with NamedTemporaryFile() as f:
        yield f.name

PARAMETER_STORE_PREFIX = "/test/feeds"
@pytest.fixture
def test_db_parameter() -> str:
    ssm = boto3.client("ssm")
    feed_id = "foo"
    yield feed_id

    # Clean up parameter
    feed_latest_key = f"{PARAMETER_STORE_PREFIX}/{feed_id}/latest"
    ssm.delete_parameter(Name=feed_latest_key)


def test_run_file(test_db_file, feed_data):
    feed = FeedReader(feed_data)
    db = FileDatabase(test_db_file)
    poster = MagicMock()

    bot = Bot(feed, db, poster)

    all_entries = [e for e in feed.entries]
    # First put the 50 first items
    feed.entries = all_entries[:50]
    bot.run()
    assert len(db.data) == 5
    assert db.latest["published"] == all_entries[49]["published"]
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 50

    # Next put all items
    feed.entries = all_entries[:]
    poster.reset_mock()
    bot.run()
    assert len(db.data) == 5
    assert db.latest["published"] == all_entries[-1]["published"]
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 50

    # No more entries added after rerun
    poster.reset_mock()
    bot.run()
    assert len(db.data) == 5
    assert db.latest["published"] == all_entries[-1]["published"]
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 0
    

def test_run_parameter_store(test_db_parameter, feed_data):
    feed = FeedReader(feed_data)
    db = ParameterStoreDatabase(PARAMETER_STORE_PREFIX, test_db_parameter)
    poster = MagicMock()

    bot = Bot(feed, db, poster)

    all_entries = [e for e in feed.entries]
    # First put the 50 first items
    feed.entries = all_entries[:50]
    bot.run()
    assert db.latest["published"] == all_entries[49]["published"]
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 50

    # Next put all items
    feed.entries = all_entries[:]
    poster.reset_mock()
    bot.run()
    assert db.latest["published"] == all_entries[-1]["published"]
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 50

    # No more entries added after rerun
    poster.reset_mock()
    bot.run()
    assert db.latest["published"] == all_entries[-1]["published"]
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 0