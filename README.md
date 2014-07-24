online-ratings
==============

AGA Online Ratings protocol and implementation

The goal of the AGA Online Ratings Protocol is to provide Go Servers with a standard way to report results between AGA members that happen on their servers to us for computing a cross-server rating.

Other goals of the project can be found on the [implementation plan here](https://docs.google.com/document/d/1XOcpprw0Y8xhHTroYnUU7tt0rN6F3-T4_9sgOeifqwI)


## Getting Started (Developers)
### Overview:
 - Set up a virtualenv with python 3.4
 - clone the repo
 - `pip install` the requirements
 - run the app.

### On a mac, with homebrew
Assuming you have homebrew installed, and pip/virtualenv/virtualenvwrapper installed on the system python.
```
  $ brew install python3
  $ mkvirtualenv --python=/usr/local/bin/python3 <env name here>
  $ git clone https://github.com/usgo/online-ratings.git
  $ cd online-ratings
  $ pip install -r requirements.txt
  $ python run.py
```
