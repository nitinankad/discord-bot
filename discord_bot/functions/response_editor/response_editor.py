from __future__ import annotations

import json
import urllib.request
import urllib.error
import logging

from discord_bot.facade.bedrock_facade import get_bedrock_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handle(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
    except (json.JSONDecodeError, TypeError):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Invalid JSON body"}),
        }

    task = body.get("task", "")
    application_id = body.get("application_id")
    token = body.get("token")
    question = body.get("question")

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
        content = body.get("content")
        if not content:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: content (or question for ask_followup)"}),
            }

    url = f"https://discord.com/api/v10/webhooks/{application_id}/{token}/messages/@original"
    data = json.dumps({"content": content}).encode()
    req = urllib.request.Request(url, data=data, method="PATCH")
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
