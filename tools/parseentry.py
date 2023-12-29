#!/usr/bin/env python3.11

# pyright: strict

from typing import TextIO, TypedDict, cast
import json
import re
import sys
from itertools import count

from transforms import transform_title


KEY_PASSWORD = "password"
KEY_TITLE = "title"
VAL_NA = "value_na"


def build_data(f: TextIO, title: str):
    obj: dict[str, str] = {}
    itr = zip(f, count())
    lastkey: str = ""
    for dline1, idx in itr:
        dline = dline1.rstrip()
        if is_pass_line(idx):
            lastkey = KEY_PASSWORD
            obj[lastkey] = dline
            continue
        data_cont = extract_continuation(dline)
        if data_cont is not None:
            if lastkey != "":
                obj[lastkey] += append_data_cont(data_cont)
            continue
        data_start = extract_start(dline)
        if data_start is not None:
            key, val = data_start
            if val == VAL_NA:
                return (None, f"MISSING VALUE: {title}")
            lastkey = make_key(obj, key, idx)
            obj[lastkey] = val
            continue
    return (obj, None)


def append_data_cont(data: str):
    return f"\n{data}"


def make_key(obj: dict[str, str], key: str, idx: int):
    return make_new_key(key, idx) if key in obj else key


def make_new_key(key: str, idx: int):
    return f"{key} extra {str(idx)}"


def extract_start(dline: str):
    mtch = re.match(r"^(?<!\s).+$", dline)
    if mtch is None:
        return None
    data = mtch[0]
    parts = cast(list[str], re.split(r"\s*\u003A\s*", data, maxsplit=1))
    key = clean_key(parts[0])
    has_val = len(parts) > 1
    val = parts[1] if has_val else VAL_NA
    return (key, val)


def clean_key(key: str):
    return re.sub(r"\W+", " ", key)


def extract_continuation(dline: str):
    class Groups(TypedDict):
        data: str
    mtch = re.match(r"^\s+(?P<data>.*)$", dline)
    if mtch is None:
        return mtch
    groups = cast(Groups, mtch.groupdict())
    return groups["data"]


def is_pass_line(idx: int):
    return idx == 0


def clean_title_path(val: str):
    return re.sub(r"\u003A\u003A", "/", val)


def normalize_title(val: str):
    val1 = clean_title_path(val)
    val2 = transform_title(val1)
    return val2


def post_process_data(obj_orig: dict[str, str], title: str):
    obj = obj_orig.copy()
    if KEY_TITLE in obj:
        obj["title extra 0"] = obj[KEY_TITLE]
        del obj[KEY_TITLE]
    obj[KEY_TITLE] = title
    if "username" in obj:
        return obj
    if "user" in obj:
        obj["username"] = obj["user"]
        del obj["user"]
        return obj
    if "email" in obj:
        obj["username"] = obj["email"]
        del obj["email"]
        return obj
    return obj


def build_all(title_orig: str, fh: TextIO):
    title = normalize_title(title_orig)
    obj1, msg1 = build_data(fh, title)
    if obj1 is None or msg1 is not None:
        return obj1, msg1
    obj2 = post_process_data(obj1, title)
    return obj2, None


def main():
    obj, msg = build_all(sys.argv[1], sys.stdin)
    if obj is None or msg is not None:
        print(msg, file=sys.stderr)
        sys.exit(1)
    json.dump(obj, sys.stdout, indent=2)
    sys.exit(0)


if __name__ == "__main__":
    main()

