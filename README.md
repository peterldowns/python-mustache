# Mustache templating for Python

### What?
A recursive descent parser for the [mustache templating
language](http://mustache.github.com/).

Install: `pip install mustache` or `easy_install mustache`.

### Why?

I wrote this to improve my Python skills and learn about recursive descent. I
guess it's something that every young programmer needs to do :)

I also wanted to provide a simple API that plays nicely with micro-WSGI
frameworks  like nice [`bottle`](bottlepy.org) and
[`flask`](http://flask.pocoo.org/). For example, here's how to use `mustache`
with `bottle` to show a web page that tells you the current year (useful for
time travelers):

`wsgi.py`:

```python
import time
from bottle import Bottle
from mustache import template

app = Bottle()

@app.get('/')
@template('templates/index.mustache')
def index():
    now = time.time()
    return {'year' : now.tm_year}
```

`templates/index.mustache`:

```mustache
The year is {{year}}!
```

### Documentation

Coming soon! Sorry!


### Testing
As of March 2 2013 this library passes every test in the
[offical mustache spec](https://github.com/mustache/spec/), which is included as
a git submodule.

To run the test suite:

* Clone the git repo.
* From the root, run:
    * `git submodule init`
    * `git submodule update`
    * `nosetests`


### Etc.
* Only depends on the stdlib.
* Does not support streaming.
* No command-line utility.
* **Written as a learning experience.**

