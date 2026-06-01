import { Code, Function, Runtime } from 'aws-cdk-lib/aws-lambda';
import { Duration, Stack, StackProps } from 'aws-cdk-lib/core';
import { Construct } from 'constructs';
import { Effect, PolicyStatement } from 'aws-cdk-lib/aws-iam';
import { execSync } from 'child_process';
import * as path from 'path';

export class ResponseEditorStack extends Stack {
  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    const lambdaFunction = new Function(this, 'ResponseEditorLambda', {
      functionName: 'ResponseEditor',
      runtime: Runtime.PYTHON_3_12,
      handler: 'discord_bot.functions.response_editor.response_editor.handler',
      timeout: Duration.minutes(15),
      memorySize: 512,
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
      environment: {
        BEDROCK_MODEL_ID: process.env.BEDROCK_MODEL_ID || 'anthropic.claude-sonnet-4-5-20251001-v1:0',
      },
    });

    lambdaFunction.addToRolePolicy(new PolicyStatement({
      actions: ['bedrock:InvokeModel'],
      effect: Effect.ALLOW,
      resources: ['*'],
    }));
  }
}
