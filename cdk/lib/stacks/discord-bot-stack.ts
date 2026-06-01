import { LambdaRestApi } from 'aws-cdk-lib/aws-apigateway';
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Stack, StackProps } from 'aws-cdk-lib/core';
import { Construct } from 'constructs';

export class DiscordBotStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lambdaFunction = new Function(this, 'DiscordBotLambda', {
      functionName: 'DiscordBot',
      runtime: Runtime.PYTHON_3_14,
      handler: 'discord_bot.handler',
      code: Code.fromAsset('../', {
        bundling: {
          image: Runtime.PYTHON_3_14.bundlingImage,
          command: [
            'bash',
            '-c',
            'pip install --no-cache -r requirements.txt -t /asset-output && cp -au --exclude=cdk --exclude=node_modules --exclude=.git --exclude="*.md" --exclude="*.egg-info" --exclude=__pycache__ --exclude=backup --exclude=token.txt --exclude=login.txt . /asset-output',
          ],
        },
      }),
      memorySize: 512,
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
