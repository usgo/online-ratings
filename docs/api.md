## <a name="resource-game">Game</a>


A game played between two players

### Attributes

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **black_id** | *integer* | black player id | `42` |
| **date_played** | *date-time* | time the game was played | `"2015-01-01T12:00:00Z"` |
| **game_record** | *string* | game record in SGF | `"<raw sgf string>"` |
| **game_server** | *string* | game server id | `"KGS"` |
| **id** | *integer* | game id | `42` |
| **white_id** | *integer* | white player id | `42` |

### Game Creation

Report a game result

```
POST /api/v1/games
```

#### Required Parameters

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **black_id** | *integer* | black player id | `42` |
| **date_played** | *date-time* | time the game was played | `"2015-01-01T12:00:00Z"` |
| **game_server** | *string* | game server id | `"KGS"` |
| **white_id** | *integer* | white player id | `42` |


#### Optional Parameters

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **game_record** | *string* | game record in SGF | `"<raw sgf string>"` |
| **game_url** | *string* | game url | `"http://example.com/game.sgf"` |


#### Curl Example

```bash
$ curl -n -X POST http://dev.usgo.org/api/v1/games \
  -d '{
  "black_id": 42,
  "white_id": 42,
  "game_server": "KGS",
  "date_played": "2015-01-01T12:00:00Z",
  "game_record": "<raw sgf string>",
  "game_url": "http://example.com/game.sgf"
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
  "date_played": "2015-01-01T12:00:00Z",
  "game_record": "<raw sgf string>"
}
```

### Game SGF

Fetch a link to the sgf contents

```
GET /api/v1/games/{game_id}/sgf
```


#### Curl Example

```bash
$ curl -n http://dev.usgo.org/api/v1/games/$GAME_ID/sgf
```


#### Response Example

```
HTTP/1.1 200 OK
```

```json
<sgf contents>
```


## <a name="resource-player">Player</a>


An online player

### Attributes

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **id** | *integer* | player id | `42` |
| **name** | *string* | name of the player | `"example"` |

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
  "name": "example"
}
```


