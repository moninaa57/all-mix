#!/usr/bin/env python3
"""
notes.py - Simple CLI note manager using SQLite.

Usage:
  notes.py add "Title" "body text" [--tags tag1,tag2]
  notes.py list [--tag TAG]
  notes.py show ID
  notes.py search "query"
  notes.py delete ID
  notes.py export-md ID > note.md
"""

import argpa
import sqlite3
import os
import datetime
import sys
from typing import List, Optional

DB_PATH = os.path.expanduser("~/.local_notes.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        tags TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()

def add_note(title: str, body: str, tags: Optional[List[str]]):
    now = datetime.datetime.utcnow().isoformat()
    tags_str = ",".join(tags) if tags else ""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (title, body, tags, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (title, body, tags_str, now, now))
    conn.commit()
    nid = cur.lastrowid
    conn.close()
    print(f"Added note ID {nid}")

def list_notes(filter_tag: Optional[str]):
    conn = get_conn()
    cur = conn.cursor()
    if filter_tag:
        cur.execute("SELECT id, title, tags, created_at FROM notes WHERE tags LIKE ? ORDER BY updated_at DESC", (f"%{filter_tag}%",))
    else:
        cur.execute("SELECT id, title, tags, created_at FROM notes ORDER BY updated_at DESC")
    rows = cur.fetchall()
    if not rows:
        print("No notes found.")
        return
    for r in rows:
        tags = r["tags"] or "-"
        created = r["created_at"].split("T")[0]
        print(f"[{r['id']}] {r['title']}  (tags: {tags})  created: {created}")
    conn.close()

def show_note(nid: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE id = ?", (nid,))
    r = cur.fetchone()
    conn.close()
    if not r:
        print("Note not found.")
        return
    print(f"ID: {r['id']}")
    print(f"Title: {r['title']}")
    print(f"Tags: {r['tags'] or '-'}")
    print(f"Created: {r['created_at']}")
    print(f"Updated: {r['updated_at']}")
    print("\n---\n")
    print(r['body'])

def delete_note(nid: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = ?", (nid,))
    conn.commit()
    changed = cur.rowcount
    conn.close()
    if changed:
        print(f"Deleted note {nid}")
    else:
        print("Note not found.")

def search_notes(query: str):
    q = f"%{query}%"
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, tags, created_at FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY updated_at DESC", (q, q))
    rows = cur.fetchall()
    conn.close()
    if not rows:
        print("No matches.")
        return
    for r in rows:
        print(f"[{r['id']}] {r['title']}  (tags: {r['tags'] or '-'})")

def export_md(nid: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM notes WHERE id = ?", (nid,))
    r = cur.fetchone()
    conn.close()
    if not r:
        print("Note not found.", file=sys.stderr)
        sys.exit(2)
    title = r['title']
    tags = r['tags'] or ''
    created = r['created_at']
    body = r['body']
    md = f"# {title}\n\n_Created: {created}_\n\n*Tags:* {tags}\n\n---\n\n{body}\n"
    print(md)

def parse_args():
    p = argparse.ArgumentParser(prog="notes.py")
    sub = p.add_subparsers(dest="cmd", required=True)

    a_add = sub.add_parser("add", help="Add a new note")
    a_add.add_argument("title")
    a_add.add_argument("body")
    a_add.add_argument("--tags", help="comma separated tags", default="")

    a_list = sub.add_parser("list", help="List notes")
    a_list.add_argument("--tag", help="filter by tag", default="")

    a_show = sub.add_parser("show", help="Show a note")
    a_show.add_argument("id", type=int)

    a_search = sub.add_parser("search", help="Search notes by text")
    a_search.add_argument("query")

    a_delete = sub.add_parser("delete", help="Delete note by id")
    a_delete.add_argument("id", type=int)

    a_export = sub.add_parser("export-md", help="Export note as markdown to stdout")
    a_export.add_argument("id", type=int)

    return p.parse_args()

def main():
    init_db()
    args = parse_args()
    if args.cmd == "add":
        tags = [t.strip() for t in args.tags.split(",") if t.strip()] if args.tags else []
        add_note(args.title, args.body, tags)
    elif args.cmd == "list":
        tag = args.tag if args.tag else None
        list_notes(tag)
    elif args.cmd == "show":
        show_note(args.id)
    elif args.cmd == "search":
        search_notes(args.query)
    elif args.cmd == "delete":
        delete_note(args.id)
    elif args.cmd == "export-md":
        export_md(args.id)
    else:
        print("Unknown command")

if _name_ == "_main_":
    main()
