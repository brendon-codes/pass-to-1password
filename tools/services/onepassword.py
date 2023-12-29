#!/usr/bin/env python3.11

# pyright: strict

from typing import TypedDict, Literal, NotRequired, cast
import os
import tempfile
from itertools import chain
import re
import subprocess


def item_create_login(
    title: str,
    password: str,
    url: str | None = None,
    fields: dict[str, str] | None = None,
    vault: str | None = None,
):

    class ItemCreateMainArgs(TypedDict):
        category: Literal["login"]
        title: str
        vault: NotRequired[str]
        url: NotRequired[str]


    CreateType = Literal["password", "text", "file"]

    EXCLUDE_FIELDS = ["password", "meta_title", "url"]

    def _build_main_args_out(mainargs: ItemCreateMainArgs):
        def _build(arg: tuple[str, str]):
            key, val = arg
            return [f"--{key}", val]
        items = cast(list[tuple[str, str]], mainargs.items())
        return list(chain.from_iterable(map(_build, items)))


    def _build_cust_args_out(customargs: dict[str, str]):
        Ret = tuple[str, CreateType, str]

        def _makefile(data: str):
            fpath: str
            with tempfile.NamedTemporaryFile(mode="wt", delete=False) as fp:
                fp.write(data)
                fpath = fp.name
            return fpath

        def _is_item_password(key: str, val: str):
            return key == "password"

        def _is_item_file(key: str, val: str):
            return "\n" in val

        def _is_item_email(key: str, val: str):
            return re.match(
                r"^[\w\u002D\u002B\u002E\u00F5]{1,253}\u0040[\w\u002D\u002B\u002E]{1,253}$",
                val
            )

        def _makeitem(key: str, val: str):
            if _is_item_password(key, val):
                return cast(Ret, (key, "password", val))
            if _is_item_file(key, val):
                return cast(Ret, (key, "file", _makefile(val)))
            if _is_item_email(key, val):
                return cast(Ret, (key, "email", val))
            return cast(Ret, (key, "text", val))

        def _makeitems(args: dict[str, str]):
            items: list[Ret] = []
            for key1, val1 in args.items():
                items.append(_makeitem(key1, val1))
            return items

        def _build(arg: Ret):
            key, typ, val = arg
            return f"{key}[{typ}]={val}"

        def _get_file_paths(items: list[Ret]):
            return list(
                map(
                    lambda a: a[2],
                    filter(
                        lambda a: a[1] == "file",
                        items
                    )
                )
            )

        items = _makeitems(customargs)
        filepaths = _get_file_paths(items)
        out = list(map(_build, items))
        return (out, filepaths)

    def _clean_cust_args(args: dict[str, str]):
        def _filt(arg: tuple[str, str]):
            key = arg[0].lower()
            if key in EXCLUDE_FIELDS:
                return False
            return True
        return dict(filter(_filt, args.items()))

    mainargs: ItemCreateMainArgs = {
        "category": "login",
        "title": title
    }
    if vault is not None:
        mainargs["vault"] = vault
    if url is not None:
        mainargs["url"] = url
    customargs: dict[str, str] = _clean_cust_args(fields.copy()) if fields is not None else {}
    customargs["password"] = password
    mainargs_out = _build_main_args_out(mainargs)
    custargs_out, tmp_filepaths = _build_cust_args_out(customargs)
    cmd_args = ["item", "create"]
    all_args = [*cmd_args, *mainargs_out, *custargs_out]
    try:
        run_cmd(all_args)
    except Exception as e:
        clean_tmp_files(tmp_filepaths)
        raise e
    else:
        clean_tmp_files(tmp_filepaths)


def clean_tmp_files(fpaths: list[str]):
    for fpath in fpaths:
        if not fpath.startswith("/tmp/"):
            raise Exception("Cannot delete file")
        os.remove(fpath)


def run_cmd(all_args: list[str]):
    run_args = ["op", *all_args]
    subprocess.run(run_args)
