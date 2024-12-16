#
# Copyright 2024 Tabs Data Inc.
#

from enum import Enum

DUPLICATE_METHODS = ["collect_schema"]
FUNCTION_METHODS = ["pipe"]
INTERNAL_METHODS = [
    "_comparison_error",
    "_fetch",
    "_from_pyldf",
    "_scan_python_function",
    "_set_sink_optimizations",
]
MATERIALIZE_METHODS = [
    "collect",
    "collect_async",
    "describe",
    "fetch",
    "max",
    "mean",
    "median",
    "min",
    "null_count",
    "profile",
    "quantile",
    "std",
    "sum",
    "var",
]
RENAME_METHODS = ["with_context"]
UNNECESSARY_METHODS = ["lazy"]
UNRECOMMENDED_METHODS = ["cache"]
UNSUPPORTED_METHODS = [
    "approx_n_unique",
    "count",
    "gather_every",
    "group_by_dynamic",
    "interpolate",
    "join_asof",
    "map_batches",
    "melt",
    "reverse",
    "shift",
    "merge_sorted",
    "rename",
    "rolling",
    "select_seq",
    "set_sorted",
    "top_k",
    "bottom_k",
    "unpivot",
    "with_columns_seq",
    "with_row_count",
    "with_row_index",
]
UNSTABLE_METHODS = [
    "_to_metadata",
    "join_where",
    "sink_csv",
    "sink_ipc",
    "sink_ndjson",
    "sink_parquet",
    "sql",
    "update",
]


class SystemColumns(Enum):
    TD_ID = "$td.id"
    TD_SRC = "$td.src"


REQUIRED_COLUMNS = [
    SystemColumns.TD_ID.value,
]
