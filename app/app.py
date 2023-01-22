# These are all we need for our purposes
import datetime
import random

import pytz
from dateutil.parser import parse as date_parse
from flask import Flask, jsonify, redirect, render_template, request

from pynewsreader.core import PyNewsReader

LIMIT = 4

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", **{
        "flask_test": "This is a test!",
        "news": []
    })


@app.route('/rand', methods=['GET'])
def ping_pong():
    return jsonify(random.random())


@app.route('/ignore_source', methods=['GET'])
def ignore_source():
    pass


@app.route('/favourite_source', methods=['GET'])
def favourite_source():
    pass


@app.route('/update', methods=['GET'])
def update():
    pnr = PyNewsReader()
    pnr.update()
    return jsonify(True)


@app.route('/feeds', methods=['GET'])
def feeds():
    pnr = PyNewsReader()
    return jsonify(pnr.feeds())


@app.route('/getnews', methods=['GET'])
def getnews():
    pnr = PyNewsReader()
    news = []
    all_links = []
    only_unread = False
    only_important = False

    args = request.args.to_dict()
    if 'search' in args:
        # print(f"Categories: {args['categories'].split(',')}")
        # print(f"Min Date: {args['min_date']}")
        # print(f"Max Date: {args['max_date']}")
        # print(f"Search: {args['search']}")
        # print(f"Unread: {args['unread']}")
        if args['unread'] == 'false':
            only_unread = None
        if 'important' in args:
            if args['important'] == 'false':
                only_important = None
            else:
                only_important = True

    if 'search' in args and args['search']!='null' and args['search'] > 0:
        if args['search'] != "null" and args['search'] != "":
            dat = pnr._search_entries(args['search'])
        else:
            dat = pnr._get_entries(limit=None, important = only_important, read=only_unread)
    else:
        dat = pnr._get_entries(limit=None, important = only_important, read=only_unread)

    for i in dat:
        article_date = i.added
        if i.published is not None:
            article_date = i.published
        if 'min_date' in args:
            # print(f"Feed Name {pnr._feed_names[i.feed.url] }")
            # print(f"Feed list {args['categories'].split(',')}")
            if 'categories' in args:
                selected_feeds = args['categories'].split(',')
            else:
                selected_feeds = pnr.feeds()
            if pnr._feed_names[i.feed.url] in selected_feeds or i.feed.title in selected_feeds:
                if article_date >= date_parse(args['min_date']).replace(tzinfo=pytz.UTC):
                    if article_date <= date_parse(args['max_date']).replace(tzinfo=pytz.UTC)+datetime.timedelta(days=1):
                        pnr._reader.mark_entry_as_read(i)
                        if i.link not in all_links:
                            all_links.append(i.link)
                            news.append({
                                "title": i.title,
                                "link": i.link,
                                "published": str(article_date),
                                "published_epoch": article_date.timestamp(),
                                "source_url": i.feed_url,
                                "source_name": i.feed.title
                            })
                        if len(news) >= LIMIT:
                            return jsonify(news)
        else:
            pnr._reader.mark_entry_as_read(i)
            if i.link not in all_links:
                all_links.append(i.link)
                news.append({
                    "title": i.title,
                    "link": i.link,
                    "published": str(i.added),
                    "published_epoch": i.added.timestamp(),
                    "source_url": i.feed_url,
                    "source_name": i.feed.title
                })
            if len(news) >= LIMIT:
                return jsonify(news)

    return jsonify(news)
