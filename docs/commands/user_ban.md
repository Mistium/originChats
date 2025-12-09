# Command: user_ban

**Request:**
```json
{
  "cmd": "user_ban",
  "user": "<username>"
}
```

- `user`: Username.

**Response:**
- On success:
```json
{
  "cmd": "user_ban",
  "user": "<username>",
  "banned": true
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.
- User must have permission to ban users. (Only the owner can do this)

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "user_ban":`).