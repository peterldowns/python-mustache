# Mustache templating for Python

### What?
A recursive descent parser for the [mustache templating
language](http://mustache.github.com/).

Install: `pip install mustache` or `easy_install mustache`.

### Why?

I wrote this to improve my Python skills and learn about recursive descent. I
guess it's something that every young programmer needs to do :)

I also wanted to provide a nice way to render templates that didn't require
instantiating special classes, or much "magic" in the lookup of templates. I'm
not a huge fan of the [`pystache`
API](https://github.com/defunkt/pystache#use-it).

Compare the `mustache` way:

```python
from mustache import template

@template('static/templates/index.mustache')
def render_index(name):
    return {'name' : name}

@template('static/other_templates_folder/index2.mustache')
def render_index2(age):
    return {'age' : age}
```

with the `pystache` way:

```python
from pystache import Renderer

class Index(object):
    def __init__(self, name):
        self.name = name

def render_index(name):
    return Renderer(search_dirs='t1').render(Index(name))

class Index2(object):
    def __init__(self, age):
        self.age = age

def render_index2(age):
    return Renderer(search_dirs='t2').render(Index2(age))
```

A nice bonus to the API is that it plays well with [`bottle`](bottlepy.org),
[`flask`](http://flask.pocoo.org/), and other micro web frameworks. For example,
here's how to use `mustache` with `bottle` to show a web page that tells you the
current year (useful for time travelers):

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


An important disclaimer: the `pystache` code works really well and is very
clean and well-written. The people who have worked on it have done a great job, and I've
learned a lot diving through their code. In fact, I first started this project
as a fork of `pystache`!

### Documentation

There is still a lot of work to be done documenting the `mustache` API. It's on
its way!


### Status?
As of March 2 2013 this library passes every test in the
[offical mustache spec](https://github.com/mustache/spec/).

It also passes a couple other tests I've written (although I should write more). Try pulling
and running `nosetest`. 


### Etc.
* Only depends on the stdlib, which is pretty cool.
* Does not support streaming (yet).

