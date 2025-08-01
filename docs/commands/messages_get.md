# Command: messages_get

**Request:**

```json
{
  "cmd": "messages_get",
  "channel": "<channel_name>",
  "limit": <optional_limit>
}
```

- `channel`: Channel name.
- `limit`: (Optional) Number of messages to fetch (default 100).

**Response:**

- On success:

```json
{
  "cmd": "messages_get",
  "channel": "<channel_name>",
  "messages": [ ...array of message objects... ]
}
```

- On error: see [common errors](errors.md).

**Notes:**

- User must be authenticated and have access to the channel.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "messages_get":`).
