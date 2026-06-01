import { LambdaRestApi } from 'aws-cdk-lib/aws-apigateway';
import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Duration, Stack, StackProps } from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import { execSync } from 'child_process';
import * as path from 'path';
import { Effect, PolicyStatement } from 'aws-cdk-lib/aws-iam';

interface DiscordBotStackProps extends StackProps {
  responseEditorLambdaArn: string;
}

export class DiscordBotStack extends Stack {
  constructor(scope: Construct, id: string, props?: DiscordBotStackProps) {
    super(scope, id, props);

    const lambdaFunction = new Function(this, 'DiscordBotLambda', {
      functionName: 'DiscordBot',
      runtime: Runtime.PYTHON_3_12,
      handler: 'discord_bot.handler.handler',
      timeout: Duration.minutes(3),
      code: Code.fromAsset('../', {
        bundling: {
          image: Runtime.PYTHON_3_12.bundlingImage,
          local: {
            tryBundle(outputDir: string) {
              const src = path.resolve(__dirname, '../../../');
              execSync(
                `pip3 install --no-cache -r requirements.txt --platform manylinux2014_x86_64 --python-version 3.12 --implementation cp --abi cp312 --only-binary=:all: -t ${outputDir}`,
                { cwd: src, stdio: 'inherit' }
              );
              execSync(
                `cp -r ${src}/discord_bot ${outputDir}/`,
                { stdio: 'inherit' }
              );
              return true;
            },
          },
          command: [],
        },
      }),
      memorySize: 256,
      environment: {
        DISCORD_PUBLIC_KEY: process.env.DISCORD_PUBLIC_KEY || '',

      },
    });

    lambdaFunction.addToRolePolicy(new PolicyStatement({
      actions: ['lambda:InvokeFunction'],
      effect: Effect.ALLOW,
      resources: ['*'],
    }));

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
