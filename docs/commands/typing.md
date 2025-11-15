# Command: typing

**Request:**
```json
{
  "cmd": "typing",
  "channel": "roturTW"
}
```

**Response:**
- On success it sends globally:
```json
{
  "cmd": "typing",
  "user": "rotur",
  "channel": "roturTW"
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated.
- This command is used to indicate that the user is typing in a channel.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "typing":`).