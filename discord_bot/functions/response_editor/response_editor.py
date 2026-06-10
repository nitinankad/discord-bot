from __future__ import annotations

import json
import os
import time
import uuid
import urllib.request
import urllib.error
import logging

from discord_bot.facade.bedrock_facade import get_bedrock_response
from discord_bot.facade.abliteration_facade import get_abliteration_response

logger = logging.getLogger()
logger.setLevel(logging.INFO)

RUNNINGHUB_BASE = "https://www.runninghub.ai/openapi/v2"
RUNNINGHUB_T2I_ENDPOINT = f"{RUNNINGHUB_BASE}/rhart-image-g/text-to-image"
RUNNINGHUB_T2V_ENDPOINT = f"{RUNNINGHUB_BASE}/rhart-video/wan-2.2/text-to-video"
RUNNINGHUB_I2V_ENDPOINT = f"{RUNNINGHUB_BASE}/rhart-video/ltx-2.3/image-to-video"
RUNNINGHUB_I2I_ENDPOINT = f"{RUNNINGHUB_BASE}/rhart-image-g/image-to-image"
RUNNINGHUB_QUERY_ENDPOINT = f"{RUNNINGHUB_BASE}/query"

POLL_INTERVAL_SECONDS = 5
MAX_POLL_ATTEMPTS = 60  # 5 min max


def handler(event, context):
    task = event.get("task", "")
    application_id = event.get("application_id")
    token = event.get("token")

    logger.info(f'Got a request with task={task}, app_id={application_id}')

    if not all([application_id, token]):
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Missing required fields: application_id, token"}),
        }

    if task == "ask_followup":
        question = event.get("question")
        if not question:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: question"}),
            }
        try:
            logger.info(f"Generating response for question: {question}")
            content = get_bedrock_response(question)
        except Exception as e:
            logger.error(f"Bedrock error: {e}")
            content = "Sorry, I encountered an error while processing your question."
        return _patch_discord_message(application_id, token, content[:2000])

    elif task == "chat_followup":
        message = event.get("message")
        if not message:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: message"}),
            }
        try:
            logger.info(f"Generating chat response for: {message}")
            content = get_abliteration_response(message)
        except Exception as e:
            logger.error(f"Abliteration error: {e}")
            content = "Sorry, I encountered an error while processing your message."
        return _patch_discord_message(application_id, token, content[:2000])

    elif task == "t2v_followup":
        prompt = event.get("prompt")
        if not prompt:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: prompt"}),
            }
        return _handle_t2v(application_id, token, prompt)

    elif task == "t2i_followup":
        prompt = event.get("prompt")
        if not prompt:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: prompt"}),
            }
        return _handle_t2i(application_id, token, prompt)

    elif task == "i2v_followup":
        prompt = event.get("prompt")
        image_url = event.get("image_url")
        if not prompt or not image_url:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required fields: prompt, image_url"}),
            }
        return _handle_i2v(application_id, token, image_url, prompt)

    elif task == "t2s_followup":
        text = event.get("text")
        if not text:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: text"}),
            }
        speaker = event.get("speaker", "Ryan")
        language = event.get("language", "English")
        instruct = event.get("instruct", "")
        return _handle_t2s(application_id, token, text, speaker, language, instruct)

    elif task == "i2i_followup":
        prompt = event.get("prompt")
        image_url = event.get("image_url")
        if not prompt or not image_url:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required fields: prompt, image_url"}),
            }
        return _handle_i2i(application_id, token, image_url, prompt)

    else:
        content = event.get("content")
        if not content:
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing required field: content"}),
            }
        return _patch_discord_message(application_id, token, content[:2000])


def _handle_t2s(application_id: str, token: str, text: str, speaker: str, language: str, instruct: str):
    payload = json.dumps({
        "text": text,
        "speaker": speaker,
        "language": language,
        "instruct": instruct,
    }).encode()
    tts_endpoint = os.environ.get("TTS_ENDPOINT_URL", "")
    if not tts_endpoint:
        logger.error("TTS_ENDPOINT_URL is not set")
        return _patch_discord_message(application_id, token, "Speech generation is not configured.")
    req = urllib.request.Request(
        tts_endpoint,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "nitinankad/discord-bot",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            audio_bytes = resp.read()
            content_type = resp.headers.get("Content-Type", "audio/wav").split(";")[0].strip()
    except Exception as e:
        logger.error(f"TTS endpoint error: {e}")
        return _patch_discord_message(application_id, token, f"Speech generation failed: {e}")

    return _patch_discord_message_with_file(application_id, token, audio_bytes, content_type, text)


def _handle_t2i(application_id: str, token: str, prompt: str):
    api_key = os.environ.get("RUNNINGHUB_API_KEY", "")
    if not api_key:
        logger.error("RUNNINGHUB_API_KEY is not set")
        return _patch_discord_message(application_id, token, "Image generation is not configured.")

    # Submit the generation job
    try:
        task_id = _submit_t2i_job(api_key, prompt)
    except Exception as e:
        logger.error(f"RunningHub submit error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to start image generation: {e}")

    logger.info(f"RunningHub task submitted: {task_id}")

    # Poll until complete
    try:
        image_url = _poll_t2i_job(api_key, task_id)
    except Exception as e:
        logger.error(f"RunningHub poll error: {e}")
        return _patch_discord_message(application_id, token, f"Image generation failed: {e}")

    logger.info(f"RunningHub image ready: {image_url}")

    # Download image bytes
    try:
        image_bytes, content_type = _download_image(image_url)
    except Exception as e:
        logger.error(f"Image download error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to download image: {e}")

    # Send to Discord as file attachment
    return _patch_discord_message_with_file(application_id, token, image_bytes, content_type, prompt)


def _handle_t2v(application_id: str, token: str, prompt: str):
    api_key = os.environ.get("RUNNINGHUB_API_KEY", "")
    if not api_key:
        logger.error("RUNNINGHUB_API_KEY is not set")
        return _patch_discord_message(application_id, token, "Video generation is not configured.")

    try:
        task_id = _submit_t2v_job(api_key, prompt)
    except Exception as e:
        logger.error(f"RunningHub submit error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to start video generation: {e}")

    logger.info(f"RunningHub task submitted: {task_id}")

    try:
        video_url = _poll_t2i_job(api_key, task_id)
    except Exception as e:
        logger.error(f"RunningHub poll error: {e}")
        return _patch_discord_message(application_id, token, f"Video generation failed: {e}")

    logger.info(f"RunningHub video ready: {video_url}")

    try:
        video_bytes, content_type = _download_image(video_url)
    except Exception as e:
        logger.error(f"Video download error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to download video: {e}")

    return _patch_discord_message_with_file(application_id, token, video_bytes, content_type, prompt)


def _handle_i2v(application_id: str, token: str, image_url: str, prompt: str):
    api_key = os.environ.get("RUNNINGHUB_API_KEY", "")
    if not api_key:
        logger.error("RUNNINGHUB_API_KEY is not set")
        return _patch_discord_message(application_id, token, "Video generation is not configured.")

    try:
        task_id = _submit_i2v_job(api_key, image_url, prompt)
    except Exception as e:
        logger.error(f"RunningHub i2v submit error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to start video generation: {e}")

    logger.info(f"RunningHub i2v task submitted: {task_id}")

    try:
        video_url = _poll_t2i_job(api_key, task_id)
    except Exception as e:
        logger.error(f"RunningHub i2v poll error: {e}")
        return _patch_discord_message(application_id, token, f"Video generation failed: {e}")

    logger.info(f"RunningHub i2v video ready: {video_url}")

    try:
        video_bytes, content_type = _download_image(video_url)
    except Exception as e:
        logger.error(f"i2v video download error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to download video: {e}")

    return _patch_discord_message_with_file(application_id, token, video_bytes, content_type, prompt)


def _submit_i2v_job(api_key: str, image_url: str, prompt: str) -> str:
    payload = json.dumps({
        "imageUrl": image_url,
        "prompt": prompt,
        "resolution": "480p",
        "aspectRatio": "16:9",
        "duration": 5,
    }).encode()
    req = urllib.request.Request(
        RUNNINGHUB_I2V_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "nitinankad/discord-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())

    logger.info(f"RunningHub i2v submit response: {body}")

    task_id = body.get("taskId")
    if not task_id:
        raise ValueError(f"No taskId in i2v submit response: {body}")
    return task_id


def _handle_i2i(application_id: str, token: str, image_url: str, prompt: str):
    api_key = os.environ.get("RUNNINGHUB_API_KEY", "")
    if not api_key:
        logger.error("RUNNINGHUB_API_KEY is not set")
        return _patch_discord_message(application_id, token, "Image transformation is not configured.")

    try:
        task_id = _submit_i2i_job(api_key, image_url, prompt)
    except Exception as e:
        logger.error(f"RunningHub i2i submit error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to start image transformation: {e}")

    logger.info(f"RunningHub i2i task submitted: {task_id}")

    try:
        result_url = _poll_t2i_job(api_key, task_id)
    except Exception as e:
        logger.error(f"RunningHub i2i poll error: {e}")
        return _patch_discord_message(application_id, token, f"Image transformation failed: {e}")

    logger.info(f"RunningHub i2i image ready: {result_url}")

    try:
        image_bytes, content_type = _download_image(result_url)
    except Exception as e:
        logger.error(f"i2i image download error: {e}")
        return _patch_discord_message(application_id, token, f"Failed to download transformed image: {e}")

    return _patch_discord_message_with_file(application_id, token, image_bytes, content_type, prompt)


def _submit_i2i_job(api_key: str, image_url: str, prompt: str) -> str:
    payload = json.dumps({
        "model": "g-4.2",
        "prompt": prompt,
        "imageUrl": image_url,
    }).encode()
    req = urllib.request.Request(
        RUNNINGHUB_I2I_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "nitinankad/discord-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())

    logger.info(f"RunningHub i2i submit response: {body}")

    task_id = body.get("taskId")
    if not task_id:
        raise ValueError(f"No taskId in i2i submit response: {body}")
    return task_id


def _submit_t2v_job(api_key: str, prompt: str) -> str:
    payload = json.dumps({
        " resolution": "832×480",
        "duration": "5",
        "prompt": prompt,
        "negativePrompt": None,
    }).encode()
    req = urllib.request.Request(
        RUNNINGHUB_T2V_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "nitinankad/discord-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())

    logger.info(f"RunningHub t2v submit response: {body}")

    task_id = body.get("taskId")
    if not task_id:
        raise ValueError(f"No taskId in submit response: {body}")
    return task_id


def _submit_t2i_job(api_key: str, prompt: str) -> str:
    payload = json.dumps({
        "model": "g-4.2",
        "prompt": prompt,
    }).encode()
    req = urllib.request.Request(
        RUNNINGHUB_T2I_ENDPOINT,
        data=payload,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "nitinankad/discord-bot",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode())

    logger.info(f"RunningHub submit response: {body}")

    task_id = body.get("taskId")
    if not task_id:
        raise ValueError(f"No taskId in submit response: {body}")
    return task_id


def _poll_t2i_job(api_key: str, task_id: str) -> str:
    payload = json.dumps({"taskId": task_id}).encode()
    for attempt in range(MAX_POLL_ATTEMPTS):
        time.sleep(POLL_INTERVAL_SECONDS)
        req = urllib.request.Request(
            RUNNINGHUB_QUERY_ENDPOINT,
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "nitinankad/discord-bot",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            error_body = e.read().decode()
            raise ValueError(f"Poll HTTP {e.code}: {error_body}")

        logger.info(f"RunningHub poll attempt {attempt + 1}: {body}")

        status = body.get("status", "")

        if status == "SUCCESS":
            results = body.get("results") or []
            if results and results[0].get("url"):
                return results[0]["url"]
            raise ValueError(f"Status SUCCESS but no result URL found: {body}")

        if status not in ("RUNNING", "PENDING", "QUEUED"):
            error = body.get("errorMessage") or body.get("failedReason") or status
            raise ValueError(f"Task {task_id} failed with status={status!r}, full body: {body}")

    raise TimeoutError(f"Task {task_id} did not complete after {MAX_POLL_ATTEMPTS} polls")


def _download_image(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "nitinankad/discord-bot"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        content_type = resp.headers.get("Content-Type", "image/png").split(";")[0].strip()
        return resp.read(), content_type


_CONTENT_TYPE_MAP = {
    "image/png": ("image", "png"),
    "image/jpeg": ("image", "jpg"),
    "image/jpg": ("image", "jpg"),
    "image/webp": ("image", "webp"),
    "image/gif": ("image", "gif"),
    "video/mp4": ("video", "mp4"),
    "video/webm": ("video", "webm"),
    "video/quicktime": ("video", "mov"),
    "audio/wav": ("audio", "wav"),
    "audio/x-wav": ("audio", "wav"),
    "audio/mpeg": ("audio", "mp3"),
}


def _filename_for_content_type(content_type: str) -> str:
    kind, ext = _CONTENT_TYPE_MAP.get(content_type, ("file", "bin"))
    return f"{kind}.{ext}"


def _patch_discord_message_with_file(
    application_id: str,
    token: str,
    file_bytes: bytes,
    content_type: str,
    prompt: str,
) -> dict:
    filename = _filename_for_content_type(content_type)

    boundary = uuid.uuid4().hex
    payload_json = json.dumps({
        "content": f"> {prompt[:1800]}",
        "attachments": [{"id": 0, "filename": filename}],
    }).encode()

    # Build multipart/form-data body
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="payload_json"\r\n'
        f"Content-Type: application/json\r\n\r\n"
    ).encode()
    body += payload_json
    body += (
        f"\r\n--{boundary}\r\n"
        f'Content-Disposition: form-data; name="files[0]"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode()
    body += file_bytes
    body += f"\r\n--{boundary}--\r\n".encode()

    url = f"https://discord.com/api/v10/webhooks/{application_id}/{token}/messages/@original"
    req = urllib.request.Request(
        url,
        data=body,
        method="PATCH",
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "nitinankad/discord-bot",
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"message": "Image sent"})}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        logger.error(f"Discord API error: {e.code} - {error_body}")
        return {"statusCode": e.code, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": error_body})}
    except Exception as e:
        logger.error(f"Unexpected error patching Discord message with image: {e}")
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": str(e)})}


def _patch_discord_message(application_id: str, token: str, content: str) -> dict:
    url = f"https://discord.com/api/v10/webhooks/{application_id}/{token}/messages/@original"
    data = json.dumps({"content": content}).encode()
    req = urllib.request.Request(
        url,
        data=data,
        method="PATCH",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "nitinankad/discord-bot",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"message": "Response edited successfully"})}
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        logger.error(f"Discord API error: {e.code} - {error_body}")
        return {"statusCode": e.code, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": error_body})}
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {"statusCode": 500, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Internal server error"})}
