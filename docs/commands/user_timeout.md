# Command: user_timeout

**Request:**
```json
{
  "cmd": "user_timeout",
  "user": "<username>",
  "timeout": "<timeout_in_seconds>"
}
```

- `user`: Username.
- `timeout`: Timeout in seconds.

**Response:**
- On success:
```json
{
  "cmd": "user_timeout",
  "user": "<username>",
  "timeout": "<timeout_in_seconds>"
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.
- User must have permission to timeout users.
- This command sets the ratelimit for a user.
- The timeout is cleared when the server restarts.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "user_timeout":`).