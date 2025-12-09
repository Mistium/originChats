# Command: messages_pinned

**Request:**
```json
{
  "cmd": "messages_pinned",
  "channel": "<channel_name>"
}
```

- `channel`: Channel name.

**Response:**
- On success:
```json
{
  "cmd": "messages_pinned",
  "channel": "<channel_name>",
  "messages": [ ...array of message objects... ]
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "messages_pinned":`).