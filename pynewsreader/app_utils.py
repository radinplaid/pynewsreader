import re

import reader
from fasthtml.common import *


def get_article_image(res: reader.Entry):
    for i in res.enclosures:
        if "image" in i.type:
            return i.href
    images = re.findall(
        "http[^\"')]+.[jJ]{1}[pP]{1}[eE]{0,1}[gG]{1}|http[^\"')]+.[pP]{1}[Nn]{1}[gG]{1}",
        str(res),
    )
    if len(images) > 0:
        ret = images[0].strip("'").strip('"')
        # Strange unicode symbol in marktechpost image URLs
        return ret.replace("\\u202f", "%E2%80%AF")
    return None


def get_date(entry: reader.Entry):
    """Extract date from reader entry

    Args:
        entry (reader.Entry): reader Entry object

    Returns:
        str: Formatted date (Y-m-d)
    """
    if entry.published is not None:
        article_date = entry.published
    else:
        article_date = entry.added
    return article_date.strftime("%Y-%m-%d")


def get_feed_image(feed_url: str):
    """Get HTML image iconfor a given RSS feed

    Args:
        feed_url (str): URL of RSS feed

    Returns:
        Img: HTML Image/icon
    """
    return Img(
        style="max-width:48px; max-height: 48px; min-width:48px; max-width: 48px; margin-right: 10px;}",
        src=f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={feed_url}",
    )


def dedupe_articles(entries: List[reader.Entry]):
    """Deduplicate reader articles in a result set

    Args:
        entries (List[reader.Entry]): List of reader entries

    Returns:
        List[reader.Entry]: List of reader entries deduplicated by URL
    """
    # New articles can be duplicated if the same story is in different feeds
    # E.g. CBC Top Stories are always in a different feed, too
    urls = set()
    unique_entries = []
    for i in entries:
        if i.id not in urls:
            urls.add(i.id)
            unique_entries.append(i)
    return unique_entries


def list_to_markdown_table(listOfDicts):
    """Loop through a list of dicts and return a markdown table as a multi-line string.

    Source: https://github.com/codazoda/tomark/blob/master/tomark/tomark.py

    listOfDicts -- A list of dictionaries, each dict is a row

    """
    markdowntable = ""
    # Make a string of all the keys in the first dict with pipes before after and between each key
    markdownheader = "| " + " | ".join(map(str, listOfDicts[0].keys())) + " |"
    # Make a header separator line with dashes instead of key names
    markdownheaderseparator = "|-----" * len(listOfDicts[0].keys()) + "|"
    # Add the header row and separator to the table
    markdowntable += markdownheader + "\n"
    markdowntable += markdownheaderseparator + "\n"
    # Loop through the list of dictionaries outputting the rows
    for row in listOfDicts:
        markdownrow = ""
        for key, col in row.items():
            markdownrow += "| " + str(col) + " "
        markdowntable += markdownrow + "|" + "\n"
    return markdowntable
