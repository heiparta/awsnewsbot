#!/usr/bin/env python3
from typing import Dict
import boto3
import click
import os

SSM_PREFIX = os.environ.get("SSM_PREFIX", "/test/feeds")

def ssm_put_feed(feed: Dict[str, str]):
    feed_prefix = os.path.join(SSM_PREFIX, feed.pop('name'))
    ssm = boto3.client("ssm")

    for key, value in feed.items():
        ssm.put_parameter(
            Name=os.path.join(feed_prefix, key),
            Value=value,
            Type="SecureString" if "secret" in key else "String",
            DataType="text",
            Overwrite=True,
            Tier="Standard",
        )

@click.group()
def cli():
    pass

@cli.command()
@click.option('--name', prompt=True)
@click.option('--url', prompt=True)
@click.password_option('--access-key', prompt=True)
@click.password_option('--access-key-secret', prompt=True)
def add_feed(**params: Dict[str, str]):
    ssm_put_feed(params)

if __name__ == "__main__":
    cli()