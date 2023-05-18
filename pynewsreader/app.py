# These are all we need for our purposes
import datetime
import random

import fire
import pytz
from dateutil.parser import parse as date_parse
from flask import Flask, jsonify, render_template, request

from pynewsreader.core import PyNewsReader

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", **{
        "news": []
    })


@app.route('/update', methods=['GET'])
def update():
    pnr = PyNewsReader()
    pnr.update()
    return jsonify(True)


@app.route('/mark_important', methods=['GET'])
def mark_important():
    pnr = PyNewsReader()
    args = request.args.to_dict()
    if 'link' in args:
        pnr._mark_entries_important_by_url(args['link'])
        return jsonify(True)
    else:
        return jsonify(False)


@app.route('/mark_unimportant', methods=['GET'])
def mark_unimportant():
    pnr = PyNewsReader()
    args = request.args.to_dict()
    if 'link' in args:
        pnr._mark_entries_unimportant_by_url(args['link'])
        return jsonify(True)
    else:
        return jsonify(False)


@app.route('/add_tag', methods=['GET'])
def add_tag():
    pnr = PyNewsReader()
    args = request.args.to_dict()
    if 'link' in args:
        pnr._add_tag(args['link'])
        return jsonify(True)
    else:
        return jsonify(False)


@app.route('/remove_tag', methods=['GET'])
def remove_tag():
    pnr = PyNewsReader()
    args = request.args.to_dict()
    if 'link' in args:
        pnr._remove_tag(args['link'])
        return jsonify(True)
    else:
        return jsonify(False)


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

    if 'limit' in args:
        LIMIT = int(args['limit'])
    else:
        LIMIT = 50

    if 'search' in args:
        if args['unread'] == 'false':
            only_unread = None
        if 'important' in args:
            if args['important'] == 'false':
                only_important = None
            else:
                only_important = True

    if 'search' in args and args['search'] != 'null' and len(args['search']) > 0:
        if args['search'] != "null" and args['search'] != "":
            dat = [pnr._reader.get_entry(
                i) for i in pnr._reader.search_entries(args['search'], sort='recent')]
        else:
            dat = pnr._get_entries(
                limit=None, important=only_important, read=only_unread)
    else:
        dat = pnr._get_entries(
            limit=None, important=only_important, read=only_unread)

    if 'categories' in args:
        selected_feeds = args['categories'].split(',')
    else:
        selected_feeds = pnr.feeds()

    for i in dat:
        if pnr._feed_names[i.feed.url] in selected_feeds or i.feed.title in selected_feeds:
            if i.published is not None:
                article_date = i.published
            else:
                article_date = i.added


            if 'min_date' in args:
                if (
                    article_date < date_parse(args['min_date']).replace(tzinfo=pytz.UTC) or
                    article_date > date_parse(args['max_date']).replace(
                        tzinfo=pytz.UTC)+datetime.timedelta(days=1)
                ):
                    continue

            pnr._reader.mark_entry_as_read(i)
            if i.link not in all_links:
                all_links.append(i.link)
                news.append({
                    "title": i.title,
                    "link": i.link,
                    "published": str(article_date),
                    "published_epoch": article_date.timestamp(),
                    "source_url": i.feed_url,
                    "source_name": i.feed.title,
                    "icon": "mdi-bell" if i.important else "",
                    "tags": [{"key": j, "value": j} for j in pnr._get_tags(i)]
                })
            if len(news) >= LIMIT:
                return jsonify(news)

    return jsonify(news)


def run_app(host="127.0.0.1", port=5000):
    app.run(host=host, port=port)


def main():
    fire.Fire(run_app)


if __name__ == "__main__":
    main()
