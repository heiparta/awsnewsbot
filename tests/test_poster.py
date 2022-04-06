from unittest.mock import MagicMock

import pytest

from awsnewsbot.rss import FeedEntry
from awsnewsbot.poster import requests, Poster

TEST_ENTRIES = [
    FeedEntry(dict(id="123", title="hei", summary="foo", link="http", published=1)),
    FeedEntry(dict(id="456", title="moi", summary="bar", link="http", published=2)),
    FeedEntry(dict(id="789", title="oi", summary="baz", link="http", published=3)),
]

def test_post_entries(monkeypatch):
    mock = MagicMock()
    response = MagicMock()
    response.json.return_value = {"data": {"id": "first"}}
    mock.return_value = response
    monkeypatch.setattr(requests, "post", mock)
    poster = Poster("", "", "", "")
    poster.post_entries(TEST_ENTRIES)
    assert mock.call_count == 3
    assert mock.call_args_list[1].kwargs["json"]["reply"]["in_reply_to_tweet_id"] == "first"
    assert mock.call_args_list[2].kwargs["json"]["reply"]["in_reply_to_tweet_id"] == "first"


    
