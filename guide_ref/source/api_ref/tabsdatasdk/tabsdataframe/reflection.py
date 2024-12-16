#
# Copyright 2024 Tabs Data Inc.
#

import logging
from typing import List

from polars import DataFrame, LazyFrame

import tabsdatasdk.tabsdataframe.frame as tdf
from tabsdatasdk.exceptions import ErrorCode, TabsDataFrameError
from tabsdatasdk.tabsdataframe.constants import (
    DUPLICATE_METHODS,
    FUNCTION_METHODS,
    INTERNAL_METHODS,
    MATERIALIZE_METHODS,
    RENAME_METHODS,
    REQUIRED_COLUMNS,
    UNNECESSARY_METHODS,
    UNRECOMMENDED_METHODS,
    UNSTABLE_METHODS,
    UNSUPPORTED_METHODS,
)
from td_interceptor import Interceptor

# ToDo: SDK-128: Define the logging model for SDK CLI execution
logger = logging.getLogger(__name__)


def get_class_methods(cls) -> List[str]:
    methods = [func for func in dir(cls) if callable(getattr(cls, func))]
    methods.sort()
    return methods


def get_missing_methods():
    polars_methods = get_class_methods(LazyFrame)
    tabsdata_methods = get_class_methods(tdf.TabsDataLazyFrame)
    tabsdata_all_methods = set(
        tabsdata_methods
        + DUPLICATE_METHODS
        + FUNCTION_METHODS
        + INTERNAL_METHODS
        + MATERIALIZE_METHODS
        + RENAME_METHODS
        + UNNECESSARY_METHODS
        + UNRECOMMENDED_METHODS
        + UNSUPPORTED_METHODS
        + UNSTABLE_METHODS
    )
    diff = list(set(polars_methods) - tabsdata_all_methods)
    if diff:
        logger.warning(
            "There are some polars LazyDataFrame not available in TabsDataLazyFrame"
        )
    for polars_method in diff:
        logger.warning(f"   {polars_method}")


def check_polars_api():
    """
    Check polars API.
    """
    logger.info("Available TabsDataLazyFrame methods:")
    for method in get_class_methods(tdf.TabsDataLazyFrame):
        logger.info(f"   {method}")
    get_missing_methods()


def required_columns() -> list[str]:
    return REQUIRED_COLUMNS + Interceptor.instance().required_columns()


def check_required_columns(df: DataFrame | LazyFrame):
    """
    Check if any required column is missing.
    This can depend on the interceptor implementation.
    """
    missing_columns = [
        column
        for column in required_columns()
        if column not in df.collect_schema().names()
    ]
    if missing_columns:
        raise TabsDataFrameError(ErrorCode.TDF1, missing_columns)
