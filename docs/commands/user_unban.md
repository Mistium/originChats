# Command: user_unban

**Request:**
```json
{
  "cmd": "user_unban",
  "user": "<username>"
}
```

- `user`: Username.

**Response:**
- On success:
```json
{
  "cmd": "user_unban",
  "user": "<username>",
  "unbanned": true
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated and have access to the channel.
- User must have permission to unban users. (Only the owner can do this)

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "user_unban":`).