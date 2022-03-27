from abc import abstractmethod
from collections import OrderedDict
from pathlib import Path
from typing import List, Optional

import json

from awsnewsbot.rss import FeedEntry


class DatabaseBase:
    data: List[FeedEntry]
    latest: FeedEntry

    @abstractmethod
    def get_entries(self, num: int = 10) -> List[FeedEntry]:
        pass

    @abstractmethod
    def add_entries(self, entries: List[FeedEntry]) -> None:
        pass


class FileDatabase(DatabaseBase):
    def __init__(self, filename: Optional[str] = "data.json"):
        self.filename: Optional[Path] = Path(filename) if filename else ''
        self.data = OrderedDict()

        if self.filename and self.filename.exists():
            with open(self.filename, "r") as f:
                data = json.loads(f.read())
            for entry in data.get("entries", []):
                self.data[entry['id']] = entry

    def get_entries(self, num: int = 10) -> List[FeedEntry]:
        entries = []
        for id in reversed(self.data):
            entries.append(self.data[id])
            num -= 1
            if num <= 0:
                break
        return entries

    def add_entries(self, entries: List[FeedEntry]) -> None:
        # Assumes entries are already sorted
        for entry in entries:
            self.data[entry['id']] = entry
        if self.filename:
            # Back up existing database file
            if self.filename.exists():
                self.filename.replace(self.filename.with_suffix(".bak"))
            with open(self.filename, "w") as f:
                json.dump({"entries": [e for e in self.data.values()]}, f)
