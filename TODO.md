Mostly in priority order.

- add elo & elo++ rating stub.
  - refactor the ratings_math funcs to not use Model objects, just vectors is fine & safer.
- set up rq worker as part of docker-compose.  Consider celery for easier integ.
  - not really happy with how many dependencies between rq worker and the flask context. 
  - how to refactor flask app to use models properly outside of app context?
  - impl. sgf fetch as rq task
- edit profile page:
  - make list of games sortable by each column (via javascript? React?)
  - add interface for editing profile info
  - needs test; almost better as integration test?
- change the data model to two-rows-per-result
  - instead of "white, black, result, ..."
      - "white, result, ..."
      - "black, result, ..."
- add membership-expiration date sync


