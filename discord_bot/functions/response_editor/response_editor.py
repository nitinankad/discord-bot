from __future__ import annotations

import json
import urllib.request
import urllib.error
import logging

from discord_bot.facade.bedrock_facade import get_bedrock_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    task = event.get("task", "")
    application_id = event.get("application_id")
    token = event.get("token")
    question = event.get("question")

    logger.info(f'Got a request with task={task}, app_id={application_id}, question={question}')

    if not all([application_id, token]):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing required fields: application_id, token"}),
        }

    if task == "ask_followup" and question:
        try:
            logger.info(f"Generating response for question: {question}")
            answer = get_bedrock_response(question)
            content = answer
        except Exception as e:
            logger.error(f"Bedrock error: {e}")
            content = "Sorry, I encountered an error while processing your question."
    else:
        content = event.get("content")
        if not content:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: content (or question for ask_followup)"}),
            }

    url = f"https://discord.com/api/v10/webhooks/{application_id}/{token}/messages/@original"
    data = json.dumps({"content": content}).encode()
    req = urllib.request.Request(url, data=data, method="PATCH", headers={"User-Agent": "nitinankad/discord-bot"})
    req.add_header("Content-Type", "application/json")

    try:
        response = urllib.request.urlopen(req, timeout=10)
        response.read()
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"message": "Response edited successfully"}),
        }
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        logger.error(f"Discord API error: {e.code} - {error_body}")
        return {
            "statusCode": e.code,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": error_body}),
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error"}),
        }
