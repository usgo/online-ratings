online-ratings
==============

AGA Online Ratings protocol and implementation

The goal of the AGA Online Ratings Protocol is to provide Go Servers with a standard way to report results between AGA members that happen on their servers to us for computing a cross-server rating.

Other goals of the project can be found on the [implementation plan here](https://docs.google.com/document/d/1XOcpprw0Y8xhHTroYnUU7tt0rN6F3-T4_9sgOeifqwI)

## Using the API (Go Server implementers)

All api endpoints accept and return JSON.
Available endpoints:
  - `POST /api/v1/games` Report a game result.
  - `GET /api/v1/games/<game_id>` Get a game result by ID
  - `GET /api/v1/games/<game_id>/sgf` Get a game's SGF file by ID
  - `GET /api/v1/players/<player_id>` Get a player by ID
  - `GET /api/v1/players?token=<token>` Get a player by their secret token.

Here's an example request to create a game:
POST /api/v1/games
  ?server_tok=secret_kgs
  &b_tok=player_1_token
  &w_tok=player_2_token
{
  "black_id": 1,
  "white_id": 2,
  "game_server": "KGS",
  'rated': True,
  'result': 'W+R',
  'date_played': '2015-02-26T10:30:00',
  'game_record': '(;FF[4]GM[1]SZ[19]CA[UTF-8]SO[gokifu.com]BC[ja]WC[ja]EV[54th Japanese Judan]PB[Kono Takashi]BR[8p]PW[O Meien]WR[9p]KM[6.5]DT[2015-02-26]RE[W+R];B[qd];W[dp];B[pq];W[od];B[oc];W[nc];B[pc];W[nd];B[qf];W[ec];B[jd];W[hd];B[jf];W[mg];B[jh];W[mi];B[cd];W[de];B[ce];W[df];B[cg];W[jj];B[hf];W[ff];B[dc];W[kg];B[jg];W[gj];B[jq];W[mp];B[gq];W[po];B[qo];W[qp];B[pp];W[qq];B[qn];W[pr];B[or];W[qr];B[oq];W[pn];B[rp];W[rq];B[ro];W[pm];B[ps];W[qm];B[rm];W[rl];B[sr];W[eq];B[cm];W[ip];B[iq];W[hp];B[gp];W[fr];B[gr];W[dn];B[dm];W[em];B[cn];W[co];B[en];W[do];B[el];W[fm];B[fl];W[gm];B[gl];W[hm];B[hl];W[im];B[lq];W[dk];B[dl];W[mq];B[lr];W[di];B[il];W[ii];B[jm];W[jn];B[kn];W[ko];B[jo];W[in];B[km];W[jp];B[lo];W[kp];B[lp];W[jl];B[fo];W[ho];B[cq];W[dr];B[bo];W[bp];B[an];W[bq];B[ck];W[cj];B[bk];W[eb];B[cb];W[jc];B[kc];W[ic];B[kd];W[le];B[id];W[hc];B[gh];W[ih];B[kj];W[kk];B[lj];W[ki];B[ji];W[ij];B[kh];W[li];B[lg];W[lf];B[lh];W[mh];B[ig];W[mm];B[mn];W[qg];B[pf];W[nn];B[pg];W[mr];B[no];W[mo];B[ln];W[op];B[sq];W[nq];B[rr];W[nl];B[ms];W[ns];B[ls];W[nr];B[qs];W[oo];B[js];W[qh];B[ph];W[mb];B[hh];W[fj];B[lb];W[bj];B[ej];W[ei];B[hj];W[hi];B[gi];W[hk];B[ek];W[ob];B[fi];W[mj];B[pb];W[he];B[ie];W[dg];B[ch];W[qi];B[pi];W[rg];B[rk];W[qk];B[sl];W[dj];B[kl];W[jk];B[ak];W[re];B[qe];W[rf];B[rd];W[gf];B[jb];W[ib];B[ql];W[pj];B[pl];W[ol];B[ll];W[lk];B[rj];W[qj];B[oj];W[nf];B[oa];W[na];B[nb];W[hq])'
}

You can also submit a `game_url` in lieu of the `game_record` field. `server_tok` is the game server's secret token, and `b_tok`, `w_tok` are the player's secret tokens. 


## Getting Started (Online Ratings backend developers)
### Overview:
 - Get set up with a VM to use with Docker
 - Build and run the app on the VM with Docker
 - log in using the fake login credentials found in web/create_db.py

## Getting set up with Docker
### Mac
You'll want to install docker-compose and docker-machine
```
  $ brew install docker-compose docker-machine
```

You'll also want to have a virtual machine installed, such as VirtualBox. You can then set up a docker host on VirtualBox.
```
  $ docker-machine create -d virtualbox dev
```
The output of the above command will tell you how to set the local environment variables to connect to your shiny new docker host.  For me, using fish shell, it's something like `eval (docker-machine env dev)`

### Linux
Install [docker](https://docs.docker.com/engine/installation/) and [docker-compose](https://docs.docker.com/compose/install/)

### [All]
Then the following commands should start the app running and start tailing the logs.
```
  $ cp .env_example .env
  $ docker-compose -f docker-compose.dev.yml build
  $ docker-compose -f docker-compose.dev.yml up -d
  $ docker-compose -f docker-compose.dev.yml logs
```
The `build` step will create docker containers for each part of the app (nginx, flask, etc.). The `up -d` step will coordinate the running of all the containers as specified in the docker-compose yaml file.

If this is the first time you've set up the database, you'll need to create the initial tables with 
```
  $ docker-compose -f docker-compose.dev.yml run --rm web python /usr/src/app/create_db.py
```
The dockerfile configuration will then serve the app at [[virtual machine IP on localhost]], port 80. For example, http://192.168.99.100:80 You can find your docker hosts by running
```
  $ docker-machine ls
```

You can remap the ports that the app listens on by editing `docker-compose.base.yml` and changing the nginx ports mapping to something like `"8080:80"`

## Development
You might find it useful to have a python shell in Docker. This lets you interactively play with database queries and such.
```
  $ docker-compose -f docker-compose.dev.yml run --rm web python -i /usr/src/app/shell.py
  >>> from app.models import Player
  >>> print(Player.query.filter(Player.id==1).first())
  Player FooPlayerKGS, id 1
```

## Running locally, without Docker
Assuming you have homebrew installed, and pip/virtualenv/virtualenvwrapper installed on the system python. 
```
  $ brew install python3
  $ mkvirtualenv --python=/usr/local/bin/python3 <env name here>
  $ git clone https://github.com/usgo/online-ratings.git
  $ cd online-ratings
  $ pip install -r requirements.txt
  $ python run.py
```


## Running the Tests
The standard `unittest` module has a discovery feature that will automatically find and run tests.  The directions given below will search for tests in any file named `test_*.py`.
```
  $ source bin/activate
  $ cd web
  $ python -m unittest discover
```
To see other options for running tests, you may:
```
  $ cd <repo root directory>
  $ python -m unittest --help
```

## Deploying

Deploying should be the same as testing, except that the docker machine you use is on AWS, etc. Additionally, you should run docker-compose with the prod overrides:
```
  $ vim .env (change passwords, secret_key to production values)
  $ docker-compose -f docker-compose.prod.yml build
  $ docker-compose -f docker-compose.prod.yml up -d
```

## Questions?
The developer mail list can be found here:
https://groups.google.com/forum/#!forum/usgo-online-ratings
