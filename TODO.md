Priority order:

- Get Go Servers to start integrating with our API
- Ensure rating async tasks work properly
  - Rating.created field doesn't seem to be getting populated properly.
  - Rating seems to update in the wrong direction? (A win caused a player's ranking to drop)
  - Rating assumes that prior is 1dan. It could cause players with zero games to be initialized at 1dan when ratings algorithm is run for first time.
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


