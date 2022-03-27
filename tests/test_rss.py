import os
import pytest

from awsnewsbot.rss import FeedReader

FEED_URL = "https://aws.amazon.com/about-aws/whats-new/recent/feed/"

def test_read_data(feed_data):
    feed = FeedReader(feed_data)
    assert len(feed.entries) == 100

@pytest.mark.skipif(not os.environ.get("RUN_ALL_TESTS"), reason="Run only when requested")
def test_read_url():
    feed = FeedReader(FEED_URL)
    print(len(feed.entries))