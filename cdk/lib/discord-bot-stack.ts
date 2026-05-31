import { LambdaRestApi } from 'aws-cdk-lib/aws-apigateway';
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Stack, StackProps } from 'aws-cdk-lib/core';
import { Construct } from 'constructs';

export class DiscordBotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lambdaFunction = new Function(this, 'DiscordBotLambda', {
      runtime: Runtime.PYTHON_3_14,
      handler: 'discord_bot.handler',
      code: Code.fromAsset('../'),
      environment: {
        DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY || '',
      },
    });

    new LambdaRestApi(this, 'DiscordBotApi', {
      handler: lambdaFunction,
      restApiName: 'Discord Bot API',
      description: 'API Gateway endpoint for Discord bot interactions',
      deployOptions: {
        stageName: 'prod',
      },
    });
  }
}
