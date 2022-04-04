#!/usr/bin/env python3

import aws_cdk as cdk
import yaml

from deploy.bot_stack import BotStack

app = cdk.App()

config_name = app.node.try_get_context("config")
with open(f"config/{config_name}.yaml") as f:
    config = yaml.safe_load(f.read())

infra = BotStack(app, "BotStack", config)

app.synth()
