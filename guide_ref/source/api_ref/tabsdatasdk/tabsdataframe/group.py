#
# Copyright 2024 Tabs Data Inc.
#

from __future__ import annotations

from collections.abc import Iterable

# noinspection PyProtectedMember
from polars._typing import IntoExpr, RollingInterpolationMethod
from polars.lazyframe.group_by import LazyGroupBy

import tabsdatasdk.tabsdataframe.frame as tdf


class TabsDataLazyGroupBy:
    def __init__(self, gb: LazyGroupBy) -> None:
        self._gb = gb

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    def agg(
        self, *aggs: IntoExpr | Iterable[IntoExpr], **named_aggs: IntoExpr
    ) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.agg(*aggs, **named_aggs))

    def head(self, n: int = 5) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.head(n=n))

    def tail(self, n: int = 5) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.tail(n=n))

    def all(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.all())

    def len(self, name: str | None = None) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.len(name=name))

    # ToDo: officially deprecated; we can keep it as it is not harming.
    def count(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.count())

    def first(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.first())

    def last(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.last())

    def max(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.max())

    def mean(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.mean())

    def median(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.median())

    def min(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.min())

    def n_unique(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.n_unique())

    def quantile(
        self, quantile: float, interpolation: RollingInterpolationMethod = "nearest"
    ) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(
            self._gb.quantile(quantile=quantile, interpolation=interpolation)
        )

    def sum(self) -> tdf.TabsDataLazyFrame:
        return tdf.TabsDataLazyFrame(self._gb.sum())
