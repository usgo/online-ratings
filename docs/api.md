## <a name="resource-game">Game</a>


Loosely based off the example in the README

### Attributes

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **[black_id](#resource-player)** | *integer* | black player's id | `42` |
| **date_played** | *date-time* | time the game was played | `"2015-01-01T12:00:00Z"` |
| **game_record** | *string* | game record in SGF | `"<raw sgf string>"` |
| **game_server** | *string* | game server id | `"KGS"` |
| **id** | *integer* | this could be a uuid to make it db agnostic | `42` |
| **rated** | *boolean* | whether this was a rated game (on the server?) | `true` |
| **[white_id](#resource-player)** | *integer* | white player's id | `42` |

### Game Creation

Report a game result

```
POST /api/v1/games
```

#### Required Parameters

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **black_id** | *integer* | black player's id | `42` |
| **date_played** | *date-time* | time the game was played | `"2015-01-01T12:00:00Z"` |
| **game_record** | *string* | game record in SGF | `"<raw sgf string>"` |
| **game_server** | *string* | game server id | `"KGS"` |
| **rated** | *boolean* | whether this was a rated game (on the server?) | `true` |
| **white_id** | *integer* | white player's id | `42` |



#### Curl Example

```bash
$ curl -n -X POST http://dev.usgo.org/api/v1/games \
  -d '{
  "black_id": 42,
  "white_id": 42,
  "game_server": "KGS",
  "rated": true,
  "date_played": "2015-01-01T12:00:00Z",
  "game_record": "<raw sgf string>"
}' \
  -H "Content-Type: application/json" \
  -H "X-Auth-Server-Token: <secret server token>" \
  -H "X-Auth-Black-Player-Token: <secret token for black player>" \
  -H "X-Auth-White-Player-Token: <secret token for white player>"
```


#### Response Example

```
HTTP/1.1 201 Created
```

```json
{
  "id": 42
}
```

### Game Read

Get a game result by id

```
GET /api/v1/games/{game_id}
```


#### Curl Example

```bash
$ curl -n http://dev.usgo.org/api/v1/games/$GAME_ID
```


#### Response Example

```
HTTP/1.1 200 OK
```

```json
{
  "id": 42,
  "black_id": 42,
  "white_id": 42,
  "game_server": "KGS",
  "rated": true,
  "date_played": "2015-01-01T12:00:00Z",
  "game_record": "<raw sgf string>"
}
```


## <a name="resource-player">Player</a>


I copied the database table here.

### Attributes

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **id** | *integer* | this could be a uuid to make it db agnostic | `42` |
| **name** | *string* | should this be expanded to first_name, last_name? | `"example"` |
| **server_id** | *integer* | not sure if this should be exposed, im just copying the table definition | `42` |
| **token** | *uuid* | im totally guessing that this is a uuid | `"01234567-89ab-cdef-0123-456789abcdef"` |

### Player Read

Get a player by id

```
GET /api/v1/players/{player_id}
```


#### Curl Example

```bash
$ curl -n http://dev.usgo.org/api/v1/players/$PLAYER_ID
```


#### Response Example

```
HTTP/1.1 200 OK
```

```json
{
  "id": 42,
  "name": "example",
  "server_id": 42,
  "token": "01234567-89ab-cdef-0123-456789abcdef"
}
```


