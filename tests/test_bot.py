from unittest.mock import MagicMock

from awsnewsbot.bot import Bot
from awsnewsbot.db import FileDatabase
from awsnewsbot.rss import FeedReader

def test_run(feed_data):
    feed = FeedReader(feed_data)
    db = FileDatabase("")
    poster = MagicMock()

    bot = Bot(feed, db, poster)

    all_entries = [e for e in feed.entries]
    # First put the 50 first items
    feed.entries = all_entries[:50]
    bot.run()
    assert len(db.data) == 50
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 50

    # Next put all items
    feed.entries = all_entries[:]
    poster.reset_mock()
    bot.run()
    assert len(db.data) == 100
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 50

    # No more entries added after rerun
    poster.reset_mock()
    bot.run()
    assert len(db.data) == 100
    assert poster.post_entries.called
    assert len(poster.post_entries.call_args_list[0].args[0]) == 0
    