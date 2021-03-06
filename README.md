# Mustache templating for Python


### What?
A recursive descent parser for the [mustache templating
language](http://mustache.github.com/).

Install: `pip install mustache` or `easy_install mustache`.

But really, you should be using [Pystache](https://github.com/defunkt/pystache).
**This library is unmaintained.**


### Why?
I wrote this to improve my Python skills and learn about recursive descent
parsing. I guess it's something that every young programmer needs to do :)

I also wanted to provide a simple API that plays nicely with micro-WSGI
frameworks  like nice [`bottle`](bottlepy.org) and
[`flask`](http://flask.pocoo.org/). Here's an example of using `mustache` to
show a web page that tells you the current year (useful for time travelers).


##### `bottle_app.py`
```python
import time
from bottle import Bottle, run
from mustache import template

app = Bottle()

@app.get('/')
@template('templates/index.mustache')
def index():
    now = time.time()
    return {'year' : now.tm_year}

if __name__ == '__main__':
    run(host='127.0.0.1', port=8080)
```


##### `flask_app.py`
```python
import time
from flask import Flask
from mustache import template

app = Flask(__name__)

@app.route('/')
@template('templates/index.mustache')
def index():
    now = time.time()
    return {'year' : now.tm_year}

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)
```


##### `templates/index.mustache`
```mustache
The year is {{year}}!
```


### Documentation
Almost certainly never going to be written. Sorry!


### Testing [![Build Status](https://travis-ci.org/peterldowns/python-mustache.png?branch=master,development)](https://travis-ci.org/peterldowns/python-mustache)

The current test suite is the [official mustache
spec](https://github.com/mustache/spec/), which is included as a git submodule.

Testing requires `json` (or `simplejson` for Python < 2.5). To install this
requirement automatically, specify the `test` option when installing like so:
`pip install mustache[test]` or `easy_install mustache[test]`.


#### Running the test suite
* Clone the git repo.
* From the root of the repository, run:
    * `git submodule init`
    * `git submodule update`
    * `nosetests`


### Etc.
* Only depends on the stdlib.
* Does not support streaming.
* No command-line utility.
* Written as a learning experience.
* Probably ready for production. It has a test suite, after all!

