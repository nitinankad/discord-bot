import json
import base64
import os
from cryptography.hashes import NaCl
from cryptography.exceptions import InvalidTag


def verify_discord_signature(timestamp, signature, event_body, public_key):
    """Verify the request signature from Discord."""
    msg = f"{timestamp}{event_body}"
    signature_bytes = base64.b64decode(signature)

    try:
        verifier = NaCl.SigningVerifier(base64.b64decode(public_key))
        verifier.verify(msg.encode(), signature_bytes)
        return True
    except (InvalidTag, Exception):
        return False


def handle_ping():
    """Handle the initial interaction ping from Discord."""
    return {
        "statusCode": 200,
        "body": json.dumps({"type": 1}),
        "headers": {
            "Content-Type": "application/json"
        }
    }


def handle_slash_command(interaction):
    """Handle slash command interactions."""
    data = interaction.get("data", {})
    command = data.get("name", "")
    options = data.get("options", [])

    if command == "hello":
        content = "Hello! I'm a Discord bot running on AWS Lambda."
    elif command == "info":
        content = f"Bot is running on AWS Lambda. Command: `{command}`"
    else:
        content = f"Unknown command: `{command}`. Try `/hello` or `/info`"

    return {
        "statusCode": 200,
        "body": json.dumps({
            "type": 4,
            "data": {
                "content": content
            }
        }),
        "headers": {
            "Content-Type": "application/json"
        }
    }


def handler(event, context):
    """Main Lambda handler for Discord interactions."""
    # Discord interaction request
    timestamp = event.get("headers", {}).get("x-signature-timestamp", "")
    signature = event.get("headers", {}).get("x-signature-ed25519", "")
    public_key = os.environ.get("DISCORD_PUBLIC_KEY", "")
    body = event.get("body", "")

    # Handle unencrypted body (API Gateway v2)
    if isinstance(body, str):
        event_body = body
    else:
        event_body = body.decode("utf-8") if body else ""

    # Verify signature if public key is configured
    if public_key and timestamp and signature:
        if not verify_discord_signature(timestamp, signature, event_body, public_key):
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Invalid signature"}),
                "headers": {"Content-Type": "application/json"}
            }

    # Parse the interaction
    try:
        interaction = json.loads(event_body) if event_body else {}
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"}),
            "headers": {"Content-Type": "application/json"}
        }

    # Route based on interaction type
    interaction_type = interaction.get("type", 0)

    if interaction_type == 1:
        return handle_ping()
    elif interaction_type == 2:
        return handle_slash_command(interaction)
    else:
        return {
            "statusCode": 200,
            "body": json.dumps({"type": 1}),
            "headers": {"Content-Type": "application/json"}
        }
