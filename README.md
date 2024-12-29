# pynewsreader

> An easy to use news aggregator and viewer written in python 

NOTE: This project is under active development and the API may change quite a bit. Feel free to give it a try!

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

## Web Application

The main interface for viewing the RSS feeds is the `fasthtml` web application, which can be lauched from the command line:

```bash
pnr-app --host 0.0.0.0 --port 5000
# Or
python3 -m pynewsreader.app --host 0.0.0.0 --port 5000
```

## Python Usage

```python
# Import and initialize pnr object
from pynewsreader.core import Feed, PyNewsReader
pnr = PyNewsReader()

# List feeds
pnr.feeds()

# Add a feed, and use a custom name for it
some_feeds = {
    "https://www.cbc.ca/webfeed/rss/rss-canada": "CBC | Canada",
    "https://www.cbc.ca/webfeed/rss/rss-business": "CBC | Business",
}
all_feeds = {
    "https://ricochet.media/feed/": "Richochet Media",
    "https://thetyee.ca/rss2.xml": "The Tyee",
    "https://www.thestar.com/search/?f=rss&t=article&bl=2827101&l=50": "Toronto Star | Top Stories",
    "https://www.thestar.com/search/?f=rss&t=article&c=news/investigations*&l=50&s=start_time&sd=desc": "Toronto Star | Investigations",
    "https://www.macleans.ca/feed/": "Macleans",
    "https://www.cbc.ca/webfeed/rss/rss-topstories": "CBC | Top Stories",
    "https://www.cbc.ca/webfeed/rss/rss-canada-ottawa": "CBC | Ottawa",
    "https://www.cbc.ca/webfeed/rss/rss-world": "CBC | World",
    "https://www.cbc.ca/webfeed/rss/rss-canada": "CBC | Canada",
    "https://www.cbc.ca/webfeed/rss/rss-business": "CBC | Business",
    "https://www.cbc.ca/webfeed/rss/rss-technology": "CBC | Technology",
    "https://thenarwhal.ca/feed/": None,
    "https://www.theguardian.com/world/rss": None,
    "https://www.theguardian.com/uk/technology/rss": None,
    "https://www.theguardian.com/science/rss": None,
    "https://www.theguardian.com/world/canada/rss": None,
    "https://www.thebeaverton.com/feed/?q=1684448990":"The Beaverton",
    "https://hf.co/blog/feed.xml": "Huggingface Blog",
    "https://engineering.fb.com/feed": "Facebook AI Blog",
    "https://blog.google/technology/ai/rss/": "Google AI Blog",
    "https://openai.com/blog/rss.xml": "OpenAI Blog",
    "https://www.answer.ai/index.xml": "Answer.ai Blog",
    "https://simonwillison.net/atom/everything/":"Simon Wilson Weblog"
}

for feed, name in some_feeds.items():
    pnr.add_feed(Feed(url=feed, name=name if name else None))

pnr.feeds()

# Update feeds
pnr.update()

# List entries
pnr.show(limit=1)

# Search entries
pnr.search("inflation", limit=1)

# Blacklist 
for i in [
    "Musk",
    "Apple",
    "Bezos",
    "Google",
    "Samsung",
    "iPhone",
    "iPad",
    "guardian.com/sport/",
    "guardian.com/football/",
    "thestar.com/sports",
    "cbc.ca/sports"
]:
    pnr.blacklist_add(i)

# Whitelist
# Automatically marks as "Important"
for i in ["interest rate", "Bank of Canada", "housing market"]:
    pnr.whitelist_add(i)

# Low-level access to data
res = next(pnr._get_entries(read=True, limit=1))
```
