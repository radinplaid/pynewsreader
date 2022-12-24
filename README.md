# pynewsreader

> An easy to use news aggregator and viewer written in python 

## Install

```sh
pip install git+https://github.com/radinplaid/pynewsreader.git
```

## Command Line Usage

```bash
# Show help
pnr --help

# Add a feed
pnr add_feed https://rss.cbc.ca/lineup/world.xml

# Update feed(s)
pnr update

# Show entries
pnr show --limit 10

# Search entries
pnr search canada

```

## Python Usage

Import and initialize pnr object

```{python}
from pynewsreader.core import Feed, PyNewsReader

pnr = PyNewsReader()
```

Add a feed, and use a custom name for it

```{python}
myfeed = Feed(
    url="https://www.thestar.com/content/thestar/feed.RSSManagerServlet.articles.topstories.rss",
    name="Toronto Star | Top Stories",
)

pnr.add_feed(myfeed)
```

Update feeds

```{python}
pnr.update()
```

List entries

```{python}
pnr.show()
```

Search entries

```{python}
pnr.search("canada")
```


