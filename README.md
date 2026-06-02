# discord-bot

A simple serverless Discord bot hosted on AWS that responds to slash commands.

## Updating the Discord command registry

```
curl -X PUT \
  "https://discord.com/api/v10/applications/{APPLICATION_ID}/commands" \
  -H "Authorization: Bot {BOT_TOKEN}" \
  -H "Content-Type: application/json" \
  -d @command_registry.json
```
Where `{APPLICATION_ID}` is your Discord bot's application ID and `{BOT_TOKEN}` is the bot token.
