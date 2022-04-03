from abc import abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any

import boto3
import json

from awsnewsbot.rss import FeedEntry


class DatabaseBase:
    latest: Optional[FeedEntry]

    @abstractmethod
    def get_entries(self, count: int) -> List[FeedEntry]:
        pass

    @abstractmethod
    def add_entries(self, entries: List[FeedEntry]) -> None:
        pass

    @abstractmethod
    def get_latest(self) -> Optional[FeedEntry]:
        pass


class FileDatabase(DatabaseBase):
    def __init__(self, filename: Optional[str] = "data.json") -> None:
        self.filename: Optional[Path] = Path(filename) if filename else None
        self.data: Dict[str, FeedEntry] = {}
        self.latest = None

        if self.filename and self.filename.exists():
            with open(self.filename, "r") as f:
                raw_data = f.read() or "{}"
                data = json.loads(raw_data)
            for entry in data.get("entries", []):
                self.data[entry['id']] = entry

    def get_entries(self, count: int = 5) -> List[FeedEntry]:
        entries = []
        for id in reversed(self.data):
            entries.append(self.data[id])
            if len(entries) >= count:
                break
        return entries

    def add_entries(self, entries: List[FeedEntry]) -> None:
        if not entries:
            return
        # Assume entries are sorted
        entries = entries[-5:]
        oldest = entries[0]
        for entry in entries:
            self.data[entry['id']] = entry

        # Delete older entries, leave just 5 newest ones, or possibly less
        # if the oldest one had multiple entries with same timestamp
        def keep(entry):
            return entry["id"] == oldest["id"] or entry["published"] > oldest["published"]

        self.data = {e['id']: e for e in self.data.values() if keep(e)}

        self.latest = max(self.data.values(), key=lambda e: (e['published'], e['id']))

        if self.filename:
            # Back up existing database file
            if self.filename.exists():
                self.filename.replace(self.filename.with_suffix(".bak"))
            with open(self.filename, "w") as f:
                json.dump({"entries": [e for e in self.data.values()]}, f)

    def get_latest(self) -> Optional[FeedEntry]:
        return self.latest


class ParameterStoreDatabase(DatabaseBase):
    def __init__(self, ssm_prefix: str, feed_id: str) -> None:
        self.ssm = boto3.client("ssm")
        self.ssm_prefix = ssm_prefix
        self.feed_id = feed_id

        self.latest_key = f"{self.ssm_prefix}/{self.feed_id}/latest"
        self.latest = None

    def get_latest(self) -> Optional[FeedEntry]:
        # Avoid refreshing self.latest if it's alredy initialized
        if self.latest is None:
            try:
                response = self.ssm.get_parameter(Name=self.latest_key)
                raw_data: Dict[str, Any] = json.loads(response["Parameter"]["Value"])
                self.latest = FeedEntry(**raw_data)  # type: ignore
            except self.ssm.exceptions.ParameterNotFound:
                return None
        return self.latest

    def add_entries(self, entries: List[FeedEntry]) -> None:
        if not entries:
            return
        latest_candidate = max(entries, key=lambda e: (e['published'], e['id']))

        latest = self.get_latest()
        if latest and latest["published"] > latest_candidate["published"]:
            # New entries were older than currently known latest
            return

        self.latest = latest_candidate
        self.ssm.put_parameter(
            Name=self.latest_key,
            Value=json.dumps(latest_candidate),
            Type="String",
            DataType="text",
            Overwrite=True,
            Tier="Standard",
        )
