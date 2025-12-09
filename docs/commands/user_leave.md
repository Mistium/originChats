# Command: user_leave

**Request:**
When requesting to leave the server, the client should send this command to the server.
The client will then be disconnected and the server will remove the user from the db.

```json
{
  "cmd": "user_leave"
}
```

**Response:**
All connected clients will receive this response.

- On success:
```json
{
  "cmd": "user_leave",
  "user": "<username>",
  "val": "User left server"
}
```
- On error: see [common errors](errors.md).

**Notes:**
- User must be authenticated.
- Any user can request to leave the server.

See implementation: [`handlers/message.py`](../handlers/message.py) (search for `case "user_leave":`).