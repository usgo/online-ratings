## <a name="resource-game">Game</a>


Loosely based off the example in the README

### Attributes

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **[black_id](#resource-player)** | *number* | this could be a uuid to make it db agnostic | `42.0` |
| **date_played** | *date-time* |  | `"2015-01-01T12:00:00Z"` |
| **game_record** | *string* |  | `"<raw sgf string>"` |
| **game_server** | *string* |  | `"KGS"` |
| **rated** | *boolean* |  | `true` |
| **[white_id](#resource-player)** | *number* | this could be a uuid to make it db agnostic | `42.0` |


## <a name="resource-player">Player</a>


I copied the database table here, didn't document any endpoints here.

### Attributes

| Name | Type | Description | Example |
| ------- | ------- | ------- | ------- |
| **id** | *number* | this could be a uuid to make it db agnostic | `42.0` |
| **name** | *string* | should this be expanded to first_name, last_name? | `"example"` |
| **server_id** | *number* | not sure if this should be exposed, im just copying the table definition | `42.0` |
| **token** | *uuid* | im totally guessing that this is a uuid | `"01234567-89ab-cdef-0123-456789abcdef"` |


