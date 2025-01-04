import reader
from fa6_icons import svgs
from fasthtml.common import *

from .app_utils import get_article_image, get_date, get_feed_image
from .core import Feed, PyNewsReader


def get_search_form(
    pnr: PyNewsReader, hx_target: str = "#main", hx_post: str = "/search_articles"
):
    return Form(
        Label(
            "Query",
            Input(name="query", placeholder="Search text", type="text"),
        ),
        Label(
            "Sources",
            Select(
                Option("All"),
                *(Option(i.url) for i in pnr.feeds()),
                name="feeds",
                cls="selector",
            ),
        ),
        Button("Submit"),
        hx_post=hx_post,
        method="post",
        hx_target=hx_target,
    )


def add_feed_form():
    return Form(
        Group(
            Input(name="feed_url", placeholder="Feed URL", type="text"),
            Input(name="feed_name", placeholder="Feed Name", type="text"),
            Button("Add"),
        ),
        hx_post="/add_feed",
        method="post",
        hx_swap="innerHTML",
    )


def remove_feed_form(feed: Feed):
    return Form(
        Group(
            Input(name="feed_url", value=feed.url, type="text", inputmode="readonly"),
            Input(name="feed_name", value=feed.name, type="text"),
            Button("Remove", cls="secondary"),
        ),
        method="post",
        hx_post="/remove_feed",
        hx_swap="delete",
    )


def main_page(*args):
    return Div(
        Nav(
            Ul(Li(A(H1("pynewsreader"), href="/"))),
            Ul(
                Li(
                    A(
                        Svg(svgs.magnifying_glass, width=40, height=40),
                        hx_get="/search",
                        hx_swap="innerHTML",
                        hx_target="#main",
                    )
                ),
                Li(
                    A(
                        Svg(svgs.arrows_rotate, width=40, height=40),
                        hx_get="/refresh_feeds",
                        hx_swap="none",
                    )
                ),
                Li(
                    A(
                        Svg(svgs.heart, width=40, height=40),
                        hx_get="/favourites",
                        hx_target="#main",
                        hx_swap="innerHTML",
                    )
                ),
                Li(
                    A(
                        Svg(svgs.gear, width=40, height=40),
                        hx_get="/config",
                        hx_target="#main",
                        hx_swap="innerHTML",
                    )
                ),
                Li(
                    A(
                        Svg(svgs.github.brands, width=40, height=40),
                        href="https://github.com/radinplaid/pynewsreader",
                        target="_blank",
                    ),
                ),
            ),
        ),
        *args,
        style="padding-left: 10px;padding-right: 10px",
    )


def article_card(entry: reader.Entry, entry_id: str, feed_url: str):
    article_image = get_article_image(entry)

    return Card(
        (
            Img(
                style="min-height:128px; max-height: 256px; min-width:128px; max-width: 256px; margin-top: 20px; ",
                src=article_image,
            )
            if article_image
            else None
        ),
        Div(
            Form(
                Group(
                    Input(name="entry_id", value=entry_id, type="text", hidden=True),
                    Input(name="feed_url", value=feed_url, type="text", hidden=True),
                    Button(
                        "👍",
                        cls="secondary",
                        hx_post="/mark_important",
                        hx_swap="none",
                    ),
                ),
                style="margin-right: 5px;",
            ),
            Form(
                Group(
                    Input(name="entry_id", value=entry_id, type="text", hidden=True),
                    Input(name="feed_url", value=feed_url, type="text", hidden=True),
                    Button(
                        "👎",
                        cls="secondary",
                        hx_post="/mark_unimportant",
                        hx_swap="none",
                    ),
                ),
                style="margin-left: 5px;",
            ),
            style="display: flex; margin-top: 10px;",
        ),
        P("❗Important") if entry.important else (),
        header=A(
            get_feed_image(entry.feed.url),
            H3("❗" + entry.title) if entry.important else H4(entry.title),
            style="display: flex; text-decoration: none; ",
            cls="row",
            href=entry.link,
            target="_blank",
        ),
        footer=(P("Source: " + entry.feed.title), P("Date: " + get_date(entry))),
        style="min-width: 420px; max-width:420px;",
    )


def article_grid(entries: List[reader.Entry], next_button: bool = True):
    if next_button:
        next_button = Button(
            "Next",
            hx_get="/change",
            hx_target="#main",
            hx_swap="outerHTML",
            onclick="window.scrollTo(0, 0);",
            style="margin-bottom: 20px",
        )
    else:
        next_button = None

    return Div(
        Div(
            (article_card(entry, entry.id, entry.feed.url) for entry in entries),
            style="""display: flex;
    flex-direction: row;
    justify-content: space-between;
    flex-wrap: wrap;""",
        ),
        next_button,
        cls="row",
        id="main",
    )


def show_articles(pnr: PyNewsReader, mark_read: bool, limit: int):
    entries = pnr._get_entries(limit=limit, read=False)
    entries = [i for i in entries]

    # New articles can be duplicated if the same story is in different feeds
    # E.g. CBC Top Stories are always in a different feed, too
    urls = set()
    unique_entries = []
    for i in entries:
        if i.id not in urls:
            urls.add(i.id)
            unique_entries.append(i)

    if mark_read:
        for entry in entries:
            pnr._reader.mark_entry_as_read(entry)

    return article_grid(unique_entries)
