import aws_cdk as cdk
from aws_cdk import (
    Stack,
)
from aws_cdk.aws_cloudwatch import TreatMissingData
from aws_cdk.aws_cloudwatch_actions import SnsAction
from aws_cdk.aws_lambda import Function, AssetCode, Runtime
from aws_cdk.aws_iam import PolicyStatement, Effect
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_events_targets import LambdaFunction
from constructs import Construct
from pathlib import Path

from typing import Dict

class BotStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, config: Dict[str, str], **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        asset = AssetCode.from_asset(str(Path(__file__).parent.parent / "awsnewsbot/dist"))
        self.bot = Function(
            self, "Botfunction",
            code=asset,
            runtime=Runtime.PYTHON_3_9,
            handler="awsnewsbot.bot.handler",
            environment=dict(
                FEED_ID=config["feed_id"],
                FEED_PREFIX=config['ssm']['feed_prefix'],
                AUTH_PREFIX=config['ssm']['auth_prefix'],
            ),
            timeout=cdk.Duration.seconds(30),
        )
        self.bot.add_to_role_policy(
            PolicyStatement(
                effect=Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                ],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{config['ssm']['feed_prefix']}/*",
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{config['ssm']['auth_prefix']}/*",
                ],
            ),
        )
        self.bot.add_to_role_policy(
            PolicyStatement(
                effect=Effect.ALLOW,
                actions=[
                    "ssm:PutParameter",
                ],
                resources=[
                    f"arn:aws:ssm:{self.region}:{self.account}:parameter{config['ssm']['feed_prefix']}/{config['feed_id']}/latest",
                ],
            )
        )

        lambda_target = LambdaFunction(handler=self.bot)
        self.rule = Rule(
            self,
            "BotSchedule",
            schedule=Schedule.cron(minute="42", hour="0/2"),
            targets=[lambda_target],
        )

        self.sns_topic = Topic(self, "AlertTopic")
        self.errors_alarm = self.bot.metric_errors().create_alarm(
            self,
            "LambdaErrorAlarm",
            evaluation_periods=3,
            threshold=1,
            treat_missing_data=TreatMissingData.NOT_BREACHING,
        )
        self.errors_alarm.add_alarm_action(SnsAction(self.sns_topic))
        self.errors_alarm.add_ok_action(SnsAction(self.sns_topic))
