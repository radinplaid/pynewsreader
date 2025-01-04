import re

import reader
from fasthtml.common import *


def get_article_image(res: reader.Entry):
    for i in res.enclosures:
        if "image" in i.type:
            return i.href
    images = re.findall(
        '"{1}http[^"\']+.jpg["]|"{1}http[^"\']+.jpeg["]|"{1}http[^"\']+.png["]',
        str(res),
    )
    if len(images) > 0:
        return images[0].strip("'").strip('"')
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
