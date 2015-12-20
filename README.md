online-ratings
==============

AGA Online Ratings protocol and implementation

The goal of the AGA Online Ratings Protocol is to provide Go Servers with a standard way to report results between AGA members that happen on their servers to us for computing a cross-server rating.

Other goals of the project can be found on the [implementation plan here](https://docs.google.com/document/d/1XOcpprw0Y8xhHTroYnUU7tt0rN6F3-T4_9sgOeifqwI)


## Getting Started (Developers)
### Overview:
 - Get set up with a VM to use with Docker
 - Build and run the app on the VM with Docker
 - log in using the fake login credentials found in web/create_db.py

## Getting set up with Docker
You'll want to install docker-compose and docker-machine
```
  $ brew install docker-compose docker-machine
```

You'll also want to have a virtual machine installed, such as VirtualBox. You can then set up a docker host on VirtualBox.
```
  $ docker-machine create -d virtualbox dev
```
The output of the above command will tell you how to set the local environment variables to connect to your shiny new docker host.  For me, using fish shell, it's something like `eval (docker-machine env dev)`
Then the following commands should start the app running and start tailing the logs.
```
  $ docker-compose -f docker-compose.dev.yml build
  $ docker-compose -f docker-compose.dev.yml up -d
  $ docker-compose -f docker-compose.dev.yml logs
```
The `build` step will create docker containers for each part of the app (nginx, flask, etc.). The `up -d` step will coordinate the running of all the containers as specified in the docker-compose yaml file.

If this is the first time you've set up the database, you'll need to create the initial tables with 
```
  $ docker-compose -f docker-compose.dev.yml run --rm web python /src/create_db.py
```
The dockerfile configuration will then serve the app at [[virtual machine IP on localhost]], port 80. For example, http://192.168.99.100/ You can find your docker host's by running
```
  $ docker-machine ls
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
  $ cd web
  $ python -m unittest
```
To see other options for running tests, you may:
```
  $ cd <repo root directory>
  $ python -m unittest --help
```

## Deploying

Deploying should be the same as testing, except that the docker machine you use is on AWS, etc. Additionally, you should run docker-compose with the prod overrides:
```
  $ docker-compose -f docker-compose.yml -f prod.yml build
  $ docker-compose -f docker-compose.yml -f prod.yml up -d
```

## Questions?
The developer mail list can be found here:
https://groups.google.com/forum/#!forum/usgo-online-ratings
