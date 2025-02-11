"""Main codebase for fetching and saving RSS feeds"""

__all__ = ["console", "logger", "strip_html", "Feed", "PyNewsReader", "main"]

import json
import logging
from collections import namedtuple
from pathlib import Path
from typing import *

import fire
import reader
from bs4 import BeautifulSoup
from rich import print
from rich.console import Console
from rich.panel import Panel

console = Console()

logger = logging.getLogger(__name__)


def strip_html(s: str):
    s = BeautifulSoup(s, "html.parser")
    return s.text


class Feed:
    """RSS feed class"""

    def __init__(self, url: str, name: str = None, tags: List[str] = []):
        self.url = url
        self.name = name
        self.tags = tags

    def add_tag(self, tag: str):
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str):
        if tag in self.tags:
            self.tags.remove(tag)


class PyNewsReader:
    def __init__(self, feeds=List[Feed]):
        self._dbfolder = Path().home() / ".cache/pynewsreader"
        if not self._dbfolder.exists():
            self._dbfolder.mkdir(parents=True)

        # If custom feed names exist, read them in
        feed_names_path = self._dbfolder / "feed_names.json"
        if feed_names_path.exists():
            with open(self._dbfolder / "feed_names.json", "rt") as myfile:
                self._feed_names = json.load(myfile)
        else:
            self._feed_names = {}

        # If title blacklist exists, read it in
        title_blacklist_path = self._dbfolder / "title_blacklist.json"
        if title_blacklist_path.exists():
            with open(self._dbfolder / "title_blacklist.json", "rt") as myfile:
                self._title_blacklist = json.load(myfile)
        else:
            self._title_blacklist = []

        self._reader = reader.make_reader(
            str(self._dbfolder / "db.sqlite"),
            plugins=["reader.enclosure_dedupe", "reader.entry_dedupe"],
        )

        # If title whitelist exists, read it in
        title_whitelist_path = self._dbfolder / "title_whitelist.json"
        if title_whitelist_path.exists():
            with open(self._dbfolder / "title_whitelist.json", "rt") as myfile:
                self._title_whitelist = json.load(myfile)
        else:
            self._title_whitelist = []

        self._reader = reader.make_reader(
            str(self._dbfolder / "db.sqlite"),
            plugins=["reader.enclosure_dedupe", "reader.entry_dedupe"],
        )

        self._reader.enable_search()

        def hook(session, request, **kwargs):
            request.headers.setdefault(
                "User-Agent",
                "Mozilla/5.0 (X11; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
            )

        self._reader._parser.session_factory.request_hooks.append(hook)

    def _print_entries(
        self, entries: List[reader.Entry], mark_as_read: bool = True, limit: int = 10
    ):
        """Pretty print entries - supports reader.Reader.get_entries arguments"""
        displayed_links = set()
        for e in entries:
            if e.link in displayed_links:
                # Don't display duplicates
                self._reader.mark_entry_as_read(e)
            else:
                displayed_links.add(e.link)
                if e.published:
                    published_date = "Date: " + e.published.isoformat()[:10]
                else:
                    published_date = "Date: Unknown"
                if mark_as_read:
                    self._reader.mark_entry_as_read(e)

                feed_title = f"[bold]{self._get_feed_title(e.original_feed_url)}[/bold]"

                if e.important:
                    panel_body = ":exclamation_mark:"
                else:
                    panel_body = ""
                panel_body += f"Title: [bold]{e.title}[/bold]" + "\n"
                panel_body += str(published_date) + "\n\n"
                try:
                    panel_body += strip_html(e.summary).strip() + "\n"
                except TypeError:
                    panel_body += str(e.summary) + "\n"

                console.print(
                    Panel(
                        panel_body,
                        title=feed_title,
                        subtitle=f"[link={e.link}]{e.link}[/link]",
                    )
                )
                console.print()
            if len(displayed_links) == limit:
                return

    def _get_feed_title(self, url: str):
        """Get display title for pynewsreader feed"""
        if url in self._feed_names and self._feed_names[url] is not None:
            return self._feed_names[url]
        elif self._reader.get_feed(url).title:
            return self._reader.get_feed(url).title
        else:
            return self._reader.get_feed(url).url

    def _get_entries(
        self, important: bool = None, read: Union[None, bool] = None, limit: int = 10
    ) -> List[reader.Entry]:
        """Get entries in reader.Entry format"""
        return self._reader.get_entries(read=read, limit=limit, important=important)

    def _get_tags(self, entry: reader.Entry):
        """Get tags for a given entry"""
        return [i[0] for i in list(self._reader.get_tags(entry))]

    def _add_tag(self, entry: reader.Entry, tag_key: str, tag_value: Dict = None):
        """Add tag to entry"""
        reader.Reader.set_tag(entry, tag_key, tag_value)

    def _remove_tag(self, entry: reader.Entry, tag_key: str):
        """Remove tag from entry"""
        self._reader.delete_tag(entry, tag_key)

    def _mark_important(self, feed_url: str, entry_id: str):
        article = self._reader.get_entry((feed_url, entry_id))
        self._reader.mark_entry_as_important(article)

    def _mark_unimportant(self, feed_url: str, entry_id: str):
        article = self._reader.get_entry((feed_url, entry_id))
        self._reader.mark_entry_as_unimportant(article)

    def _mark_blacklist_as_read(self, match_strings: List):
        for i in self._reader.get_entries(read=False):
            for filter_string in match_strings:
                if (filter_string in i.title) or (filter_string in i.link):
                    self._reader.mark_entry_as_read(i)
                    self._reader.set_tag(i, "blacklist", ())

    def _mark_whitelist_as_important(self, match_strings: List):
        for i in self._reader.get_entries(read=False):
            for filter_string in match_strings:
                if filter_string in i.title:
                    self._reader.mark_entry_as_important(i)
                    self._reader.set_tag(i, "whitelist", ())

    def blacklist_add(self, blacklist_string: str):
        """Add entry to blacklist"""
        if blacklist_string not in self._title_blacklist:
            self._title_blacklist.append(blacklist_string)
            with open(self._dbfolder / "title_blacklist.json", "wt") as myfile:
                json.dump(self._title_blacklist, myfile)

    def blacklist_remove(self, blacklist_string: str):
        """Remove entry from blacklist"""
        if blacklist_string in self._title_blacklist:
            self._title_blacklist.remove(blacklist_string)
            with open(self._dbfolder / "title_blacklist.json", "wt") as myfile:
                json.dump(self._title_blacklist, myfile)

    def blacklist_show(self):
        """Show blacklist"""
        return self._title_blacklist

    def whitelist_add(self, whitelist_string: str):
        """Add entry to whitelist"""
        if whitelist_string not in self._title_whitelist:
            self._title_whitelist.append(whitelist_string)
            with open(self._dbfolder / "title_whitelist.json", "wt") as myfile:
                json.dump(self._title_whitelist, myfile)
            for entry in self._get_entries(limit=None):
                if whitelist_string in entry.title:
                    self._reader.mark_entry_as_important(entry)

    def whitelist_remove(self, whitelist_string: str):
        """Remove whitelist entry"""
        if whitelist_string in self._title_whitelist:
            self._title_whitelist.remove(whitelist_string)
            with open(self._dbfolder / "title_whitelist.json", "wt") as myfile:
                json.dump(self._title_whitelist, myfile)
            for entry in self._get_entries(limit=None):
                if whitelist_string in entry.title:
                    self._reader.mark_entry_as_unimportant(entry)

    def whitelist_show(self):
        """Show whitelist"""
        return self._title_whitelist

    def update(self, workers: int = 8):
        """Update feeds and search"""
        self._reader.update_feeds(workers=workers)
        self._reader.update_search()
        if len(self._title_blacklist) > 0:
            self._mark_blacklist_as_read(self._title_blacklist)
        if len(self._title_whitelist) > 0:
            self._mark_whitelist_as_important(self._title_whitelist)

    def add_feed(self, feed: Union[Feed, str]):
        """Add feed to pynewsreader

        Args:
            feed (Feed): pynewsreader Feed to add
        """
        if isinstance(feed, Feed):
            self._feed_names[feed.url] = feed.name
            self._reader.add_feed(feed.url.rstrip("/"), exist_ok=True)
        elif isinstance(feed, str):
            self._reader.add_feed(feed.rstrip("/"), exist_ok=True)
        else:
            raise Exception("Must be str or Feed type to add")

        # Save names to file
        with open(self._dbfolder / "feed_names.json", "wt") as myfile:
            json.dump(self._feed_names, myfile)

    def remove_feed(self, feed: Union[Feed, str]):
        """Remove feed from pynewsreader instance

        Args:
            feed (Union[Feed, str]): Feed to remove
        """

        if isinstance(feed, Feed):
            self._reader.delete_feed(feed.url)
        elif isinstance(feed, str):
            self._reader.delete_feed(feed)
        else:
            raise Exception(TypeError)

    def feeds(self):
        """List pynewsreader feeds

        Returns:
            List[str]: List of names of current pynewsreader feeds
        """
        feed_object = namedtuple("Feeds", ["url", "name"])
        return [
            feed_object(i.url, self._get_feed_title(i.url))
            for i in self._reader.get_feeds()
        ]

    def show(
        self,
        limit: int = 6,
        read: bool = False,
        important: bool = None,
        mark_as_read: bool = True,
    ):
        """Pretty print entries

        Args:
            limit (int, optional): Number of entries to show. Defaults to 5.
            read (bool, optional): Show read entries (True), unread entries (False), or all entries (None). Defaults to None.
            mark_as_read (bool, optional): Mark displayed entries as read. Defaults to False.
        """
        self._print_entries(
            self._get_entries(read=read, important=important, limit=limit * 2),
            limit=limit,
            mark_as_read=mark_as_read,
        )

    def search(self, query: str, mark_as_read: bool = True, limit: int = 10):
        """Search entries and pretty print results

        Args:a
            query (str): Search query
            mark_as_read (bool, optional): Mark results as read? Defaults to True.
        """
        entries = [
            self._reader.get_entry(i) for i in self._reader.search_entries(query)
        ]
        if len(entries) > 0:
            self._print_entries(
                entries,
                mark_as_read=mark_as_read,
                limit=limit,
            )


def main():
    fire.Fire(PyNewsReader)


if __name__ == "__main__":
    main()
