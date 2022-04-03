#!/usr/bin/env python3

import aws_cdk as cdk

from deploy.infra_stack import InfraStack


app = cdk.App()
infra = InfraStack(app, "InfraStack")

app.synth()
