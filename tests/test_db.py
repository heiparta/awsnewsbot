from awsnewsbot.db import FileDatabase
from awsnewsbot.rss import FeedReader

def test_add_nothing() -> None:
    db = FileDatabase("test.json")
    db.add_entries([])
    assert len(db.get_entries()) == 0
    assert db.get_latest() is None

def test_add_entries(feed_data) -> None:
    feed = FeedReader(feed_data)
    db = FileDatabase("test.json")
    db.add_entries(feed.entries[:10])
    # Only 5 newest entries are stored
    assert len(db.get_entries()) == 5
    assert db.get_latest()['published'] is feed.entries[9]['published']

    db.add_entries(feed.entries[6:13])
    # Only 5 newest entries are stored
    assert len(db.get_entries()) == 5
    assert db.get_latest()['published'] is feed.entries[12]['published']