#!/usr/bin/env node
import * as dotenv from 'dotenv';
import { App } from 'aws-cdk-lib';
import { DiscordBotStack } from './stacks/discord-bot-stack'; 
import { ResponseEditorStack } from './stacks/response-editor-stack';

dotenv.config();

const app = new App();

new DiscordBotStack(app, 'DiscordBotStack', {
    env: { account: process.env.AWS_ACCOUNT_ID, region: process.env.AWS_REGION },
});

new ResponseEditorStack(app, 'ResponseEditorStack', {});
