Priority order:

- Ensure that game submission + player lookup is working. This is so that Go servers can start integrating. Anticipated workflow:
  - Find out what their server's secret_key is (via UI + login)
  - Get a player's ID by his secret_key
  - Look up a player's basic info (rating, name) by his ID
  - Submit game result with server secret_key and both players' secret_keys.
    - For now, use a blocking HTTP request to fetch the sgf if a URL is provided, instead of trying to get an async sgf fetch working.
- Deploy.
  - Figure out hosting
  - Figure out SSL
- Get Go Servers to start integrating with our API
- Ensure rating async tasks work properly
- Ensure player signup UI (to obtain a secret_key) works properly
- Announce to game servers that they can start telling players to go sign up with us and bring their secret_keys to them.

- As we scale up:
  - Make sgf fetch async (use redis-queue, maybe celery?)

- Back burner:
  - add membership-expiration date sync
- change the data model to two-rows-per-result
  - instead of "white, black, result, ..."
      - "white, result, ..."
      - "black, result, ..."


