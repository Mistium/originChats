# Command: message_pin

**Request:**
```json
{
  "cmd": "message_pin",
  "channel": "<channel_name>",
  "id": "<message_id>"
}
```

- `channel`: Channel name.
- `id`: Message ID.

**Response:**
- On success:
```json
{
  "cmd": "message_pin",
  "id": "<message_id>",
  "channel": "<channel_name>",
  "pinned": true
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.
- User must have permission to pin messages in the channel or be the owner.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "message_pin":`).