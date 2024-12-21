from urllib.parse import urlencode

from fa6_icons import svgs
from fasthtml.common import *

from pynewsreader.core import PyNewsReader

pnr = PyNewsReader()

app, rt = fast_app(
    hdrs=(
        Script(
            src="https://cdnjs.cloudflare.com/ajax/libs/flexboxgrid/6.3.1/flexboxgrid.min.css",
            type="text/css",
        )
    )
)


def b64_enc(x):
    return base64.b64encode(x.encode("ascii")).decode("ascii")


def b64_dec(x):
    return base64.b64decode((x.encode("ascii"))).decode("ascii")


def article_card(entry):

    return Card(
        # P("Author: " + entry.author if entry.author else ""),
        P("Source: " + entry.feed.title),
        Button(
            "👍",
            cls="secondary",
            hx_post=f"/mark_important/{b64_enc(entry.feed.url)}/{b64_enc(entry.id)}",
            hx_swap="beforeend",
        ),
        Nbsp(),
        Button(
            "👎",
            cls="secondary",
            hx_post=f"/mark_unimportant/{b64_enc(entry.feed.url)}/{b64_enc(entry.id)}",
            hx_swap="beforeend",
        ),
        P("❗Important") if entry.important else (),
        header=A(
            Img(
                style="max-width:64px; max-height: 64px; min-width:64px; max-width: 64px; margin-right: 20px;",
                src=f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={entry.feed.url}",
            ),
            H3("❗" + entry.title) if entry.important else H4(entry.title),
            style="display: flex; text-decoration: none; ",
            cls="row",
            href=entry.link,
            target="_blank",
        ),
        footer="Date: " + get_date(entry),
        style="min-width: 450px; max-width:450px;",
    )


def get_date(entry):
    if entry.published is not None:
        article_date = entry.published
    else:
        article_date = entry.added
    return article_date.strftime("%Y-%m-%d")


def show_articles(mark_read: bool = True):
    entries = pnr._get_entries(limit=12, read=None)
    entries = [i for i in entries]

    if mark_read:
        for entry in entries:
            pnr._reader.mark_entry_as_read(entry)

    return Div(
        Div(
            (article_card(entry) for entry in entries),
            style="""display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;""",
        ),
        cls="row",
        id="main",
    )


@rt("/")
def get():
    return Div(
        Nav(
            Ul(Li(H1("pynewsreader"))),
            Ul(
                Li(
                    A(
                        Svg(svgs.github.brands, width=40, height=40),
                        href="https://github.com/radinplaid/pynewsreader",
                        target="_blank",
                    ),
                )
            ),
        ),
        show_articles(),
        Span(cls="mdi mdi-github-circle"),
        Button("Next", hx_get="/change", hx_target="#main", hx_swap="innerHTML"),
        style="padding-left: 10px;padding-right: 10px",
    )


@rt("/change")
def get():
    return Div(show_articles())


@rt("/mark_important")
@app.post("/mark_important/{feed_url}/{id}")
def get(id: str, feed_url: str):
    id = b64_dec(id)
    feed_url = b64_dec(feed_url)
    return pnr._mark_important(feed_url=feed_url, entry_id=id)


@rt("/mark_unimportant")
@app.post("/mark_unimportant/{feed_url}/{id}")
def get(id: str, feed_url: str):
    id = b64_dec(id)
    feed_url = b64_dec(feed_url)
    return pnr._mark_unimportant(feed_url=feed_url, entry_id=id)


serve()
