#!/usr/bin/env python3

# pyright: strict

from functools import reduce


def transform_title(val_orig: str):
    
    def _transform_remove_dupes(val: str):
        def _reducer(a: list[str], b: str):
            return (a + ([b] if len(a) == 0 or b != a[-1] else []))

        return "/".join(reduce(_reducer, val.split("/"), []))
    
    out1 = _transform_remove_dupes(val_orig)
    return out1
