Mostly in priority order.

- create interface to allow ratings admins to revoke/create tokens for Players and Game Servers
- allow users to expire/refresh their tokens.
- add elo & elo++ rating stub.
  - debug elo++ algorithm
  - refactor the ratings_math funcs to not use Model objects, just vectors is fine & safer.
  - refactor the create_db and rate_all scripts to not depend on the app...
- set up rq worker as part of docker-compose.  Consider celery for easier integ.
  - not really happy with how many dependencies between rq worker and the flask context. 
  - how to refactor flask app to use models properly outside of app context?
- procedure for associating account with AGA ID:
  - call membership db for json w/ account detail.
  - send e-mail with verification link to e-mail in the usgo member profile
  - create endpoint for verification links
  - http://flask.pocoo.org/snippets/50/
- edit profile page:
  - make list of games sortable by each column (via javascript? React?)
  - add interface for editing profile info
  - add interface for revoking/renewing Player tokens
  - add interface for revoking/renewing Game Server tokens
- impl. sgf fetch -- AMJ
  - needs test; almost better as integration test?
- clean up routes & menu items, they're a little strange
- change the data model to two-rows-per-result
  - instead of "white, black, result, ..."
      - "white, result, ..."
      - "black, result, ..."
- add membership-expiration date sync
-create model for "bad results"/ probably request + error message, e.g. expired token, missing token, no sgf link, unparseable result, etc.  Make post_result create entries in table before throwing exception, make admin view summarizing bad posts.


