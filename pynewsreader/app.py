from fa6_icons import svgs
from fasthtml.common import *
from fire import Fire
import re

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


def b64_enc(x):
    return base64.b64encode(x.encode("ascii")).decode("ascii")


def b64_dec(x):
    return base64.b64decode((x.encode("ascii"))).decode("ascii")


def get_article_image(res):
    for i in res.enclosures:
        if "image" in i.type:
            return i.href
    images = re.findall(
        '"{1}http[^"\']+.jpg["]|"{1}http[^"\']+.jpeg["]|"{1}http[^"\']+.png["]',
        str(res),
    )
    if len(images) > 0:
        print(images)
        return images[0].strip("'").strip('"')
    return None


def article_card(entry):
    article_image = get_article_image(entry)

    return Card(
        # P("Author: " + entry.author if entry.author else ""),
        Div(
            Button(
                "👍",
                cls="secondary",
                hx_post=f"/mark_important/{b64_enc(entry.feed.url)}/{b64_enc(entry.id)}",
                hx_swap="none",
            ),
            Nbsp(),
            Button(
                "👎",
                cls="secondary",
                hx_post=f"/mark_unimportant/{b64_enc(entry.feed.url)}/{b64_enc(entry.id)}",
                hx_swap="none",
            ),
            Nbsp(),
            (
                Img(
                    style="min-height:128px; max-height: 256px; min-width:128px; max-width: 256px; margin-top: 20px; ",
                    src=article_image,
                )
                if article_image
                else None
            ),
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
        footer=(P("Source: " + entry.feed.title), P("Date: " + get_date(entry))),
        style="min-width: 420px; max-width:420px;",
    )


def get_date(entry):
    if entry.published is not None:
        article_date = entry.published
    else:
        article_date = entry.added
    return article_date.strftime("%Y-%m-%d")


def render_entries(entries, next_button=True):
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
            (article_card(entry) for entry in entries),
            style="""display: flex;
    flex-direction: row;
    justify-content: space-between;
    flex-wrap: wrap;""",
        ),
        next_button,
        cls="row",
        id="main",
    )


def show_articles(mark_read: bool = True, limit: int = 20):
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

    return render_entries(unique_entries)


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


@rt("/")
def get():
    return main_page(show_articles())


@rt("/search")
def get():
    frm = (
        Form(
            Group(
                Input(name="query", placeholder="Search text", type="text"),
                Button("Submit"),
            ),
            hx_post="/search_articles",
            method="post",
            hx_swap="innerHTML",
        ),
    )
    return Div(
        Titled("Search", frm),
    )


@rt("/search_articles")
@app.post("/search_articles")
def post(query: str):
    articles = [
        pnr._reader.get_entry(i) for i in pnr._reader.search_entries(query, limit=100)
    ]
    return render_entries(articles, next_button=False)


@rt("/change")
def get():
    return Div(show_articles())


@rt("/refresh_feeds")
def get(session):
    pnr.update()
    add_toast(session, f"Feeds updated. Reload page to view latest updates.", "info")
    return P("pynewsreader")


@rt("/config")
def get():
    all_feeds = pnr.feeds()
    frm = Form(
        Group(
            Input(name="feed_url", placeholder="Feed URL", type="text"),
            Input(name="feed_name", placeholder="Feed Name", type="text"),
            Button("Add"),
        ),
        hx_post="/add_feed",
        method="post",
        hx_swap="innerHTML",
    )
    frm2 = Div(
        (
            Form(
                Group(
                    Input(
                        name="feed_url", value=i.url, type="text", inputmode="readonly"
                    ),
                    Input(name="feed_name", value=i.name, type="text"),
                    Button("Remove", cls="secondary"),
                ),
                method="post",
                hx_post="/remove_feed",
                hx_swap="delete",
            )
            for i in all_feeds
        )
    )
    return Div(
        Titled("Add Feed", frm),
        Titled("Remove Feed", frm2),
        A("Back", href="/", role="button"),
    )


@rt("/add_feed")
@app.post("/add_feed")
def post(feed_url: str, feed_name: str):
    if feed_name in ("None", "none", "null"):
        feed_name = None
    pnr.add_feed(Feed(url=feed_url, name=feed_name))
    return P("Feed added")


@rt("/remove_feed")
@app.post("/remove_feed")
def post(feed_url: str, feed_name: str):
    if feed_name in ("None", "none", "null"):
        feed_name = None
    pnr.remove_feed(Feed(url=feed_url, name=feed_name))
    return P("Feed removed")


@rt("/mark_important")
@app.post("/mark_important/{feed_url}/{id}")
def get(session, id: str, feed_url: str):
    id = b64_dec(id)
    feed_url = b64_dec(feed_url)
    ret = pnr._mark_important(feed_url=feed_url, entry_id=id)
    add_toast(session, f"Marked article as important", "info")
    return P(ret)


@rt("/mark_unimportant")
@app.post("/mark_unimportant/{feed_url}/{id}")
def get(session, id: str, feed_url: str):
    id = b64_dec(id)
    feed_url = b64_dec(feed_url)
    ret = pnr._mark_unimportant(feed_url=feed_url, entry_id=id)
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
