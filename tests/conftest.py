import pytest
from pathlib import Path

FEED_FILE_NAME = Path(__file__).parent / Path("data_aws.xml")

@pytest.fixture
def feed_data():
    with open(FEED_FILE_NAME, "r") as f:
        yield f.read()