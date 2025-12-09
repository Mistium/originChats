# Command: message_react_add

**Request:**
```json
{
  "cmd": "message_react_add",
  "channel": "<channel_name>",
  "id": "<message_id>",
  "emoji": "<emoji>"
}
```

- `channel`: Channel name.
- `id`: Message ID.
- `emoji`: Emoji to add.

**Response:**
- On success:
```json
{
  "cmd": "message_react_add",
  "id": "<message_id>",
  "channel": "<channel_name>",
  "emoji": "<emoji>",
  "from": "<username>"
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.
- User must have permission to add reactions to the message.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "message_react_add":`).