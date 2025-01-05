from fasthtml.common import *
from fire import Fire

from .app_components import (
    add_feed_form,
    article_grid,
    get_search_form,
    menu_bar,
    remove_feed_form,
    show_articles,
)
from .app_utils import dedupe_articles
from .core import Feed, PyNewsReader

pnr = PyNewsReader()

app, rt = fast_app(
    hdrs=(
        Script(
            src="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
            type="text/css",
        )
    ),
    key_fname="/tmp/pynewsreader.sesskey",
)
app.title = "pynewsreader"

setup_toasts(app, duration=2)


@rt("/")
def get():
    return Main(
        menu_bar(),
        show_articles(pnr=pnr, mark_read=True, limit=20),
        style="padding-left: 10px;padding-right: 10px",
    )


@rt("/search")
def get():
    return Div(
        Titled("Search", get_search_form(pnr)),
        id="#main",
    )


@rt("/search_articles")
@app.post("/search_articles")
def post(query: str, feeds: str, tags: str):
    if feeds == "All":
        feeds = None
    if tags == "none":
        tags = False

    if len(query) > 0:
        articles = [
            pnr._reader.get_entry(i)
            for i in pnr._reader.search_entries(
                query, feed=feeds, tags=[tags], limit=200
            )
        ]
    else:
        articles = [
            i for i in pnr._reader.get_entries(limit=200, feed=feeds, tags=[tags])
        ]

    articles = dedupe_articles(articles)

    return article_grid(articles, next_button=False)


@rt("/favourites")
def get():
    articles = [i for i in pnr._get_entries(important=True, limit=200, read=None)]
    articles = dedupe_articles(articles)

    return article_grid(articles, next_button=False)


@rt("/change")
def get():
    return Div(show_articles(pnr, mark_read=True, limit=20))


@rt("/refresh_feeds")
def get(session):
    pnr.update()

    add_toast(session, f"Feeds updated. Reload page to view latest updates.", "info")

    return P("pynewsreader")


@rt("/config")
def get():
    all_feeds = pnr.feeds()

    frm = add_feed_form()
    frm2 = Div((remove_feed_form(i) for i in all_feeds))

    return Div(
        Titled("Add Feed", frm),
        Titled("Remove Feed", frm2),
        A("Back", href="/", role="button"),
    )


@rt("/add_feed")
@app.post("/add_feed")
def post(feed_url: str, feed_name: str):
    """Add RSS feed to pynewsreader

    Args:
        feed_url (str): URL of RSS feed
        feed_name (str): Name of RSS feed

    Returns:
        str: HTML formatted response from pynewsreader.add_feed method
    """
    if feed_name in ("None", "none", "null"):
        feed_name = None

    pnr.add_feed(Feed(url=feed_url, name=feed_name))

    return P("Feed added")


@rt("/remove_feed")
@app.post("/remove_feed")
def post(feed_url: str, feed_name: str):
    """Remove RSS feed from pynewsreader

    Args:
        feed_url (str): URL of RSS feed
        feed_name (str): Name of RSS feed

    Returns:
        str: HTML formatted response from pynewsreader.remove_feed method
    """
    if feed_name in ("None", "none", "null"):
        feed_name = None

    pnr.remove_feed(Feed(url=feed_url, name=feed_name))

    return P("Feed removed")


@rt("/mark_important")
@app.post("/mark_important")
def post(session, feed_url: str, entry_id: str):
    """Mark article as important

    Args:
        session (fasthttp:session): fasthtml session object
        feed_url (str): RSS feed URL
        entry_id (str): reader entry ID

    Returns:
        str: HTML formatted response from pynewsreader._mark_important method
    """
    ret = pnr._mark_important(feed_url=feed_url, entry_id=entry_id)

    add_toast(session, f"Marked article as important", "info")

    return P(ret)


@rt("/mark_unimportant")
@app.post("/mark_unimportant")
def post(session, feed_url: str, entry_id: str):
    """Mark article as unimportant

    Args:
        session (fasthttp:session): fasthtml session object
        feed_url (str): RSS feed URL
        entry_id (str): reader entry ID

    Returns:
        str: HTML formatted response from pynewsreader._mark_unimportant method
    """
    ret = pnr._mark_unimportant(feed_url=feed_url, entry_id=entry_id)

    add_toast(session, f"Marked article as unimportant", "info")

    return P(ret)


def main_app(
    host: str = "localhost",
    port: int = 8000,
    reload: bool = False,
    reload_includes: List[str] = [],
    reload_excludes: List[str] = [],
):
    """pynewsreader web application launching script

    Args:
        host (str, optional): HTTP host. Defaults to "localhost".
        port (int, optional): HTTP port. Defaults to 8000.
        reload (bool, optional): Reload app on file changes. Defaults to True.
        reload_includes (List[str], optional): Reload only if these files change. Defaults to [].
        reload_excludes (List[str], optional): Do not reload if these files change. Defaults to [].
    """
    uvicorn.run(
        f"pynewsreader.app:app",
        host=host,
        port=port,
        reload=reload,
        reload_includes=reload_includes,
        reload_excludes=reload_excludes,
    )


def cli_app():
    return Fire(main_app)


if __name__ == "__main__":
    cli_app()
