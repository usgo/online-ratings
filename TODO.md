Priority order:

- Ensure rating async tasks work properly
  - Rating.created field doesn't seem to be getting populated properly.
  - Rating seems to update in the wrong direction? (A win caused a player's ranking to drop)
  - Rating assumes that prior is 1dan. It could cause players with zero games to be initialized at 1dan when ratings algorithm is run for first time.
- Ensure player signup UI (to obtain a secret_key) works properly
- Announce to game servers that they can start telling players to go sign up with us and bring their secret_keys to them.
- Tune our rating system. In addition to returning 'rating': -1.2392, we'd like to also return 'rank': 2d. This might be more subtle than it seems; how are we to know that 1 stone's difference ends up being 1.0 in our rating system? Are there parameters we have to tune in order to ensure accurate spacing? Are handicap games going to naturally tune our ratings for us? goratings.org completely glosses over the issue; maybe that's the right approach.

- As we scale up:
  - Make sgf fetch async (use redis-queue, maybe celery?)

- Back burner:
  - add membership-expiration date sync
- change the data model to two-rows-per-result
  - instead of "white, black, result, ..."
      - "white, result, ..."
      - "black, result, ..."


