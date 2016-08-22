# Online Ratings

[![Travis Build Status](https://travis-ci.org/usgo/online-ratings.svg?branch=master)](https://travis-ci.org/usgo/online-ratings)

AGA Online Ratings protocol and implementation

The goal of the AGA Online Ratings Protocol is to provide Go Servers with a
standard way to report results between AGA members that happen on their servers
to us for computing a cross-server rating.

Other goals of the project can be found on the [implementation plan here](https://docs.google.com/document/d/1XOcpprw0Y8xhHTroYnUU7tt0rN6F3-T4_9sgOeifqwI)

## Using the API (Go Server implementers)

All api endpoints accept and return JSON.
Available endpoints:
  - `POST /api/v1/games` Report a game result.
  - `GET /api/v1/games/<game_id>` Get a game result by ID
  - `GET /api/v1/games/<game_id>/sgf` Get a game's SGF file by ID
  - `GET /api/v1/players/<player_id>` Get a player by ID
  - `GET /api/v1/players?token=<token>` Get a player by their secret token.

Here's an example HTTP request to create a game:

```
POST /api/v1/games HTTP/1.1
Content-Type: application/json
X-Auth-Server-Token: secret_kgs
X-Auth-Black-Player-Token: player_1_token
X-Auth-White-Player-Token: player_2_token

{
  "black_id": 1,
  "white_id": 2,
  "server_id": 1,
  "result": "W+R",
  "date_played": "2015-02-26T10:30:00",
  "game_record": "(;FF[4]GM[1]SZ[19]CA[UTF-8]BC[ja]WC[ja]EV[54th Japanese Judan]PB[Kono Takashi]BR[8p]PW[O Meien]WR[9p]KM[6.5]DT[2015-02-26]RE[W+R];B[qd];W[dp];B[pq];W[od])"
}
```

You can also submit a `game_url` in lieu of the `game_record` field. `server_token` is the game server's secret token, and `black_token`, `white_token` are the player's secret tokens. Your `server_id` can be discovered through the UI for online-ratings.

## Getting Started (Online Ratings backend developers)

### Overview

Before you get started working on Online Ratings, you'll need to do some setup:

* Choose your package manager
* Install Python3 and the relevant dependencies
* Install the Docker command line tools.
* Get set up with a VM to use with Docker
* Build and run the app on the VM with Docker
* log in using the fake login credentials found in `web/create_db.py`

## Package Managers

This dev guide assumes a POSIX tool chain. Most developers on this project use OSX.

* OSX: Install [homebrew](http://brew.sh/)
* Linux/Ubuntu: You should already apt-get installed

## Python and Dependencies

1.  Install Python3
    * OSX: `brew install python3`
    * Linux: You probably already have Python3 installed. If not: `sudo apt-get
      install python3`
4.  Install [pip](https://en.wikipedia.org/wiki/Pip_(package_manager))
    * `curl https://bootstrap.pypa.io/get-pip.py | python3`
5.  Install postgres
    * OSX: `brew install postgresql`
    * Linux: [See here](https://www.postgresql.org/download/linux/ubuntu/)
6.  Install the python dependencies with pip.
    * cd to `online-ratings/web` directory and run: `pip install -r requirements.txt`
7.  Run the tests!
    * cd to `online-ratings/web` directory and run: `python3 -m unittest
      discover`

**[Optional]**

Optionally, you can install VirtualEnv, which makes working with python versions
a little easier.

1.  Install Virtual Environment: mkvirtualenv
    * `pip install virtualenvwrapper`
    * Add `source /usr/local/bin/virtualenvwrapper.sh` to your `.bash_profile`
      or `.bashrc`. Alternatively, just run `source
      /usr/local/bin/virtualenvwrapper.sh` when you need it.
2.  Use VirtualWrapper to make a new virtual env:;
    * `mkvirtualenv --python=/usr/local/bin/python3 online-ratings-env`

## Getting set up with Docker

### Mac
You'll want to install `docker`, `docker-machine`, and `docker-compose`. This is easily done with Docker for Mac.

### Linux
Install [docker](https://docs.docker.com/engine/installation/) and [docker-compose](https://docs.docker.com/compose/install/)

### [All]
Then the following commands should start the app running and start tailing the logs.

```shell
cp .env_example .env
docker-compose build
docker-compose up -d
docker-compose logs
```

The `build` step will create docker containers for each part of the app (nginx,
flask, etc.). The `up -d` step will coordinate the running of all the containers
as specified in the docker-compose yaml file.

If this is the first time you've set up the database, you'll need to create the
initial tables with

```shell
docker-compose run --rm web python /usr/src/app/manage.py create_all_data
```

The dockerfile configuration will then serve the app at localhost:80.

You can remap the ports that the app listens on by editing `docker-compose.yml` and changing the nginx ports mapping to something like `"8080:80"`

## Development
You might find it useful to have a python shell in Docker. This lets you interactively play with database queries and such.
```
docker-compose -f docker-compose.dev.yml run --rm web python -i /usr/src/app/manage.py shell
>>> from app.models import Player
>>> print(Player.query.filter(Player.id==1).first())
Player FooPlayerKGS, id 1
```

## Running Locally

Generally, we prefer running with Docker. However, if you wish to run the web
server locally (perhaps for a faster iteration cycle) you can do so with the
following:

```shell
cd online-ratings
sed 's/^\([^#]\)/export \1/g' .env_example > .env_local 
source .env_local
cd web
pip install -r requirements.txt
python3 manage.py runserver
```

You should see:

```shell
* Running on http://0.0.0.0:5000/ (Press CTRL+C to quit)
```

Note: At this point, you still need to run your local Online Ratings instance
against a database instance. You can either create a local postgres instance and
create some data. Or, you can point your local server at the running Docker
images. For that, all you need to do is run through the Docker startup
instructions above and then change `DB_SERVICE` in your `.env_local` to
`0.0.0.0`.


## Running the Tests
The standard `unittest` module has a discovery feature that will automatically
find and run tests.  The directions given below will search for tests in any
file named `test_*.py`.

```shell
source bin/activate
cd web
python -m unittest discover
```
To see other options for running tests, you may:

```shell
cd <repo root directory>
python -m unittest --help
```

## Deploying

Production is the same as local. Yay Docker!

We build images automatically as part of the `.travis` unittesting. If you want
to know how it works, check out [Travis: encrypting secret
data](https://docs.travis-ci.com/user/encryption-keys/) and [Travis:
docker](https://docs.travis-ci.com/user/docker/). Essentially, this does the following:

*   When changes are pushed to the release branch,
*   Check to ensure that the tests pass.
*   If so, push images to the [USGO Docker hub org](https://hub.docker.com/u/usgo/)

Note that due the limitations of secrets, the [commit cannot come from a
fork](https://docs.travis-ci.com/user/pull-requests#Pull-Requests-and-Security-Restrictions):
it must be created/pushed from the base repo (usgo/online-ratings).

### Production

On the server, we have yet to integrate the above image process: (Work in progress):

```shell
vim .env (change passwords, secret_key to production values)
docker-compose build
docker-compose up -d
```

## API Documentation

### Running locally

1. Ensure [`mkdocs`][0] is installed.
2. Run `mkdocs serve` from within the root of `online-ratings`.
3. Load it in a browser and profit!

### Making non-API Pages

Create or edit the `.md` files within `docs/`.

Refer to [mkdocs][0] for more details.

### Generating API Documentation

Source files to be edited can be found in `docs/schemata`.  The files are in [YAML][1] for improved
readability.

1. Install [prmd][2] per their instructions.
2. From root of `online-ratings`, run
   `prmd combine --meta docs/meta.yml docs/schemata | prmd verify | prmd doc > docs/api.md`

[JSON Schema][3] is the general format used for types and [JSON Hyper-Schema][4] is used for
endpoint definitions.

### Deploying To gh-pages

1. Run `mkdocs gh-deploy --clean`.
2. That's it!

## Questions?
The developer mail list can be found here:
https://groups.google.com/forum/#!forum/usgo-online-ratings

[0]: http://www.mkdocs.org/
[1]: https://en.wikipedia.org/wiki/YAML
[2]: https://github.com/interagent/prmd
[3]: http://json-schema.org/documentation.html
[4]: http://json-schema.org/latest/json-schema-hypermedia.html
