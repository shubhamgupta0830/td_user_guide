#
# Copyright 2024 Tabs Data Inc.
#

from __future__ import annotations

import sys
from collections.abc import Collection, Iterable, Mapping, Sequence
from io import IOBase
from pathlib import Path
from typing import Any, Literal, NoReturn, overload

from accessify import accessify, private
from polars import DataFrame, DataType, Expr, LazyFrame, Schema

# noinspection PyProtectedMember
from polars._typing import (
    ColumnNameOrSelector,
    ExplainFormat,
    FillNullStrategy,
    IntoExpr,
    IntoExprColumn,
    JoinStrategy,
    JoinValidation,
    PolarsDataType,
    SerializationFormat,
    UniqueKeepStrategy,
)
from polars.dependencies import numpy as np

import tabsdatasdk.tabsdataframe.group as tdg
import tabsdatasdk.tabsdataframe.reflection as reflection
from tabsdatasdk.exceptions import ErrorCode, TabsDataFrameError
from tabsdatasdk.tabsdataframe.annotation import Status, status
from tabsdatasdk.tabsdataframe.reflection import check_polars_api

# ToDo: SDK-127: Unify conditional imports that depend on Python version in a single
#  file for better management
if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


@accessify
class TabsDataLazyFrame:
    """Inherited polars Functions."""

    """ Initialization Functions """

    # Todo: disable access to _df.
    @status(Status.TODO)
    def __init__(self, df: LazyFrame | DataFrame | TabsDataLazyFrame) -> None:
        if isinstance(df, LazyFrame):
            reflection.check_required_columns(df)
            self._df = df
        elif isinstance(df, DataFrame):
            reflection.check_required_columns(df)
            self._df = df.lazy()
        elif isinstance(df, TabsDataLazyFrame):
            self._df = df._df
        else:
            raise TabsDataFrameError(ErrorCode.TDF2, {type(df)})

    @status(Status.DONE)
    def clone(self) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.clone())

    """ Serialization Functions """

    @status(Status.DONE)
    def __getstate__(self) -> bytes:
        return self._df.__getstate__()

    @status(Status.DONE)
    def __setstate__(self, state: bytes) -> None:
        self._df = LazyFrame()
        self._df.__setstate__(state=state)

    # fmt: off
    @status(Status.DONE)
    @overload
    def serialize(
            self, file: None = ..., *, serialize_format: Literal["binary"] = ...
    ) -> bytes:
        ...

    # fmt: on

    # fmt: off
    @status(Status.DONE)
    @overload
    def serialize(
            self, file: None = ..., *, serialize_format: Literal["json"]
    ) -> str:
        ...

    # fmt: on

    # fmt: off
    @status(Status.DONE)
    @overload
    def serialize(
            self, file: IOBase | str | Path, *,
            serialize_format: SerializationFormat = ...
    ) -> None:
        ...

    # fmt: on

    @status(Status.DONE)
    def serialize(
        self,
        file: IOBase | str | Path | None = None,
        *,
        serialize_format: SerializationFormat = "binary",
    ) -> bytes | str | None:
        return self._df.serialize(file=file, format=serialize_format)

    @classmethod
    @status(Status.DONE)
    def deserialize(
        cls,
        source: str | Path | IOBase,
        *,
        serialize_format: SerializationFormat = "binary",
    ) -> TabsDataLazyFrame:
        return cls(LazyFrame.deserialize(source=source, format=serialize_format))

    """ Introspection Functions """

    @status(Status.DONE)
    @property
    def columns(self) -> list[str]:
        return self._df.collect_schema().names()

    @status(Status.DONE)
    @property
    def dtypes(self) -> list[DataType]:
        return self._df.collect_schema().dtypes()

    @status(Status.DONE)
    @property
    def schema(self) -> Schema:
        return self._df.collect_schema()

    @status(Status.DONE)
    @property
    def width(self) -> int:
        return self.collect_schema().len()

    """ Special Functions """

    # ToDo: work in progress; still pending restricted access and system td columns
    #  handling.
    @status(Status.TODO)
    def __getattr__(self, name):
        """This special method is used to forward attribute access to the underlying
        LazyFrame.

        If the attribute is not found in TabsDataLazyFrame, it is looked up in the
        wrapped LazyFrame.
        """
        attr = getattr(self._lazy_df, name)
        if callable(attr):

            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if isinstance(result, LazyFrame):
                    return TabsDataLazyFrame(result)
                return result

            return wrapper
        return attr

    @status(Status.DONE)
    def __bool__(self) -> NoReturn:
        return self._df.__bool__()

    @status(Status.DONE)
    def __eq__(self, other: object) -> NoReturn:
        if isinstance(other, TabsDataLazyFrame):
            return self._df.__eq__(other=other._df)
        else:
            return self._df.__eq__(other=other)

    @status(Status.DONE)
    def __ne__(self, other: object) -> NoReturn:
        if isinstance(other, TabsDataLazyFrame):
            return self._df.__ne__(other=other._df)
        else:
            return self._df.__ne__(other=other)

    @status(Status.DONE)
    def __gt__(self, other: Any) -> NoReturn:
        if isinstance(other, TabsDataLazyFrame):
            return self._df.__gt__(other=other._df)
        else:
            return self._df.__gt__(other=other)

    @status(Status.DONE)
    def __lt__(self, other: Any) -> NoReturn:
        if isinstance(other, TabsDataLazyFrame):
            return self._df.__lt__(other=other._df)
        else:
            return self._df.__lt__(other=other)

    @status(Status.DONE)
    def __ge__(self, other: Any) -> NoReturn:
        if isinstance(other, TabsDataLazyFrame):
            return self._df.__ge__(other=other._df)
        else:
            return self._df.__ge__(other=other)

    @status(Status.DONE)
    def __le__(self, other: Any) -> NoReturn:
        if isinstance(other, TabsDataLazyFrame):
            return self._df.__le__(other=other._df)
        else:
            return self._df.__le__(other=other)

    # ToDo: should we block system td columns?
    @status(Status.DONE)
    def __contains__(self, key: str) -> bool:
        return self._df.__contains__(key=key)

    @status(Status.DONE)
    def __copy__(self) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.__copy__())

    @status(Status.DONE)
    def __deepcopy__(self, memo: None = None) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.__deepcopy__(memo=memo))

    @status(Status.TODO)
    def __getitem__(self, item: int | range | slice) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.__getitem__(item=item))

    @status(Status.DONE)
    def __str__(self) -> str:
        return self._df.explain()

    @status(Status.DONE)
    def __repr__(self) -> str:
        return (
            f"<{self.__class__.__name__} at 0x{id(self):X}> with {self._df.__repr__()}"
        )

    @private
    @status(Status.DONE)
    def _repr_html_(self) -> str:
        # noinspection PyProtectedMember
        return self._df._repr_html_().replace("LazyFrame", "TabsDataLazyFrame")

    """ Description Functions """

    @status(Status.DONE)
    @private
    def explain(
        self,
        *,
        explain_format: ExplainFormat = "plain",
        optimized: bool = True,
        type_coercion: bool = True,
        predicate_pushdown: bool = True,
        projection_pushdown: bool = True,
        simplify_expression: bool = True,
        slice_pushdown: bool = True,
        comm_subplan_elim: bool = True,
        comm_subexpr_elim: bool = True,
        cluster_with_columns: bool = True,
        collapse_joins: bool = True,
        streaming: bool = False,
        tree_format: bool | None = None,
    ) -> str:
        return self._df.explain(
            format=explain_format,
            optimized=optimized,
            type_coercion=type_coercion,
            predicate_pushdown=predicate_pushdown,
            projection_pushdown=projection_pushdown,
            simplify_expression=simplify_expression,
            slice_pushdown=slice_pushdown,
            comm_subplan_elim=comm_subplan_elim,
            comm_subexpr_elim=comm_subexpr_elim,
            cluster_with_columns=cluster_with_columns,
            collapse_joins=collapse_joins,
            streaming=streaming,
            tree_format=tree_format,
        )

    @private
    @status(Status.DONE)
    def show_graph(
        self,
        *,
        optimized: bool = True,
        show: bool = True,
        output_path: str | Path | None = None,
        raw_output: bool = False,
        figsize: tuple[float, float] = (16.0, 12.0),
        type_coercion: bool = True,
        predicate_pushdown: bool = True,
        projection_pushdown: bool = True,
        simplify_expression: bool = True,
        slice_pushdown: bool = True,
        comm_subplan_elim: bool = True,
        comm_subexpr_elim: bool = True,
        cluster_with_columns: bool = True,
        collapse_joins: bool = True,
        streaming: bool = False,
    ) -> str | None:
        return self._df.show_graph(
            optimized=optimized,
            show=show,
            output_path=output_path,
            raw_output=raw_output,
            figsize=figsize,
            type_coercion=type_coercion,
            predicate_pushdown=predicate_pushdown,
            projection_pushdown=projection_pushdown,
            simplify_expression=simplify_expression,
            slice_pushdown=slice_pushdown,
            comm_subplan_elim=comm_subplan_elim,
            comm_subexpr_elim=comm_subexpr_elim,
            cluster_with_columns=cluster_with_columns,
            collapse_joins=collapse_joins,
            streaming=streaming,
        )

    @private
    @status(Status.DONE)
    def inspect(self, fmt: str = "{}") -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.inspect(fmt=fmt))

    """ Transformation Functions """

    # ToDo: proper expressions handling.
    @status(Status.TODO)
    def sort(
        self,
        by: IntoExpr | Iterable[IntoExpr],
        *more_by: IntoExpr,
        descending: bool | Sequence[bool] = False,
        nulls_last: bool | Sequence[bool] = False,
        maintain_order: bool = False,
        multithreaded: bool = True,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(
            self._df.sort(
                by=[by] + list(more_by),
                *more_by,
                descending=descending,
                nulls_last=nulls_last,
                maintain_order=maintain_order,
                multithreaded=multithreaded,
            )
        )

    # ToDo: disallow transformations in system td columns.
    @status(Status.TODO)
    def cast(
        self,
        dtypes: (
            Mapping[ColumnNameOrSelector | PolarsDataType, PolarsDataType]
            | PolarsDataType
        ),
        *,
        strict: bool = True,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.cast(dtypes=dtypes, strict=strict))

    # ToDo: should we allow only clear to 0 rows?
    @status(Status.TODO)
    def clear(self, n: int = 0) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.clear(n=n))

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    @status(Status.TODO)
    def join(
        self,
        other: TabsDataLazyFrame,
        on: str | Expr | Sequence[str | Expr] | None = None,
        how: JoinStrategy = "inner",
        *,
        left_on: str | Expr | Sequence[str | Expr] | None = None,
        right_on: str | Expr | Sequence[str | Expr] | None = None,
        suffix: str = "_right",
        validate: JoinValidation = "m:m",
        join_nulls: bool = False,
        coalesce: bool | None = None,
        allow_parallel: bool = True,
        force_parallel: bool = False,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(
            self._df.join(
                other=other._df,
                on=on,
                how=how,
                left_on=left_on,
                right_on=right_on,
                suffix=suffix,
                validate=validate,
                join_nulls=join_nulls,
                coalesce=coalesce,
                allow_parallel=allow_parallel,
                force_parallel=force_parallel,
            )
        )

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    @status(Status.TODO)
    def with_columns(
        self, *exprs: IntoExpr | Iterable[IntoExpr], **named_exprs: IntoExpr
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.with_columns(*exprs, **named_exprs))

    # ToDo: officially deprecated; we can remove it.
    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    # ToDO: We keep it as the replacement of with_context as there is no instance method
    #       that can substitute it.
    @status(Status.TODO)
    def concat(self, other: Self | list[Self]) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.with_context(other._df))

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    @status(Status.TODO)
    def drop(
        self,
        *columns: ColumnNameOrSelector | Iterable[ColumnNameOrSelector],
        strict: bool = True,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.drop(*columns, strict=strict))

    # ToDo: ensure system td columns are left unchanged.
    @status(Status.TODO)
    def fill_null(
        self,
        value: Any | Expr | None = None,
        strategy: FillNullStrategy | None = None,
        limit: int | None = None,
        *,
        matches_supertype: bool = True,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(
            self._df.fill_null(
                value=value,
                strategy=strategy,
                limit=limit,
                matches_supertype=matches_supertype,
            )
        )

    # ToDo: ensure system td columns are left unchanged.
    @status(Status.TODO)
    def fill_nan(self, value: int | float | Expr | None) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.fill_nan(value=value))

    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    # ToDo: ensure system td columns are left unchanged.
    @status(Status.DELAYED)
    def explode(
        self, columns: str | Expr | Sequence[str | Expr], *more_columns: str | Expr
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.explode(columns=columns, *more_columns))

    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    # ToDo: ensure system td columns are left unchanged.
    @status(Status.TODO)
    def unique(
        self,
        subset: ColumnNameOrSelector | Collection[ColumnNameOrSelector] | None = None,
        *,
        keep: UniqueKeepStrategy = "any",
        maintain_order: bool = False,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(
            self._df.unique(subset=subset, keep=keep, maintain_order=maintain_order)
        )

    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    # ToDo: ensure system td columns are left unchanged.
    @status(Status.TODO)
    def drop_nulls(
        self,
        subset: ColumnNameOrSelector | Collection[ColumnNameOrSelector] | None = None,
    ) -> LazyFrame:
        return LazyFrame(self._df.drop_nulls(subset=subset))

    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    # ToDo: ensure system td columns are left unchanged.
    @status(Status.DELAYED)
    def unnest(
        self,
        columns: ColumnNameOrSelector | Collection[ColumnNameOrSelector],
        *more_columns: ColumnNameOrSelector,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.unnest(columns, *more_columns))

    """Retrieval Functions"""

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    def filter(
        self,
        *predicates: (
            IntoExprColumn
            | Iterable[IntoExprColumn]
            | bool
            | list[bool]
            | np.ndarray[Any, Any]
        ),
        **constraints: Any,
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.filter(*predicates, **constraints))

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    @status(Status.TODO)
    def select(
        self, *exprs: IntoExpr | Iterable[IntoExpr], **named_exprs: IntoExpr
    ) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.select(*exprs, **named_exprs))

    # ToDo: allways attach system td columns.
    # ToDo: dedicated algorithm for proper provenance handling.
    # ToDo: check for undesired operations of system td columns.
    # ToDo: proper expressions handling.
    @status(Status.TODO)
    def group_by(
        self,
        *by: IntoExpr | Iterable[IntoExpr],
        maintain_order: bool = False,
        **named_by: IntoExpr,
    ) -> tdg.TabsDataLazyGroupBy:
        return tdg.TabsDataLazyGroupBy(
            self._df.group_by(*by, maintain_order=maintain_order, **named_by)
        )

    @status(Status.DONE)
    def slice(self, offset: int, length: int | None = None) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.slice(offset=offset, length=length))

    @status(Status.DONE)
    def limit(self, n: int = 5) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.limit(n=n))

    @status(Status.DONE)
    def head(self, n: int = 5) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.head(n=n))

    @status(Status.DONE)
    def tail(self, n: int = 5) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.tail(n=n))

    @status(Status.DONE)
    def last(self) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.last())

    @status(Status.DONE)
    def first(self) -> TabsDataLazyFrame:
        return TabsDataLazyFrame(self._df.first())

    """Internal private Functions."""


# Check polars API changes the first time this module is loaded.
check_polars_api()
