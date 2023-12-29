#!/usr/bin/env python3

from typing import TextIO, cast, TypedDict
import sys
import json

from services import onepassword


class Args(TypedDict):
    title: str | None
    password: str | None
    url: str | None
    fields: dict[str, str]


def load_obj(fh: TextIO):
    obj = json.load(fh)
    if not isinstance(obj, dict):
        return None
    return cast(dict[str, str], obj)


def get_title_key(obj: dict[str, str]):
    if "title" not in obj:
        return None
    return "title"


def get_password_key(obj: dict[str, str]):
    if "password" not in obj:
        return None
    return "password"


def get_url_key(obj: dict[str, str]):
    names = ["url", "website"]
    keys = list(filter(lambda key: key.lower().strip() in names, obj.keys()))
    if len(keys) == 0:
        return None
    return keys[0]


def build_args(obj_orig: dict[str, str]):
    obj = obj_orig.copy()
    title_key = get_title_key(obj)
    title = None if title_key is None else obj[title_key]
    if title_key is not None:
        del obj[title_key]
    password_key = get_password_key(obj)
    password = "" if password_key is None else obj[password_key]
    if password_key is not None:
        del obj[password_key]
    url_key = get_url_key(obj)
    url = None if url_key is None else obj[url_key]
    if url_key is not None:
        del obj[url_key]
    ret: Args = {
        "title": title,
        "password": password,
        "url": url,
        "fields": obj
    }
    return ret


def main():
    obj = load_obj(sys.stdin)
    if obj is None:
        raise Exception("Error")
    args = build_args(obj)
    if args["title"] is None:
        raise Exception("Bad title")
    onepassword.item_create_login(
        args["title"],
        args["password"],
        args["url"],
        args["fields"]
    )


if __name__ == "__main__":
    main()
