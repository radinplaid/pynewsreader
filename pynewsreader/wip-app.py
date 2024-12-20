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


def article_card(entry):
    return A(
        Card(
            # P("Author: " + entry.author if entry.author else ""),
            P("Source: " + entry.feed.title),
            header=Div(
                Img(
                    style="max-width:64px; max-height: 64px; min-width:64px; max-width: 64px; margin-right: 20px;",
                    src=f"https://t1.gstatic.com/faviconV2?client=SOCIAL&type=FAVICON&fallback_opts=TYPE,SIZE,URL&size=128&url={entry.feed.url}",
                ),
                H5(entry.title),
                style="display: flex;",
                cls="row contrast",
            ),
            footer="Date: " + get_date(entry),
            style="max-width:450px; min-width: 450px;",
            cls="box contrast",
        ),
        href=entry.link,
        target="_blank",
        style="text-decoration: none;",
        cls="contrast",
    )


def get_date(entry):
    if entry.published is not None:
        article_date = entry.published
    else:
        article_date = entry.added
    return article_date.strftime("%Y-%m-%d")


def show_articles(mark_read: bool = True):
    entries = pnr._get_entries(limit=200, read=None)
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
            Ul(Li(H3("pynewsreader"))),
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
    )


@rt("/change")
def get():
    return Div(show_articles())


serve()
