#
# Copyright 2024 Tabs Data Inc.
#

from abc import ABC, abstractmethod
from typing import List, Tuple, Union


class InputPlugin(ABC):
    """
    Abstract class for input plugins.

    Methods:
        trigger_input(working_dir: str) -> Union[str, Tuple[str, ...], List[str]]
            Trigger the import of the data. The method will receive a folder where it
            must store the data as parquet files, and return a list of the paths of
            the files created. This files will then be loaded and mapped to the
            dataset function in positional order, so if you want file.parquet to be
            the first argument of the dataset function, you must return it first. If
            you want a parameter to receive multiple files, return a list of the paths.
            For example, you would give the following return to provide a first argument
            with a single file and a second argument with two files:
            return ["file1.parquet", ["file2.parquet", "file3.parquet"]]
    """

    IDENTIFIER = "input-plugin"

    @abstractmethod
    def trigger_input(self, working_dir: str) -> Union[str, Tuple[str, ...], List[str]]:
        """
        Trigger the import of the data. This must be implemented in any class that
            inherits from this class. The method will receive a folder where it must
            store the data as parquet files, and return a list of the paths of the
            files created. This files will then be loaded and mapped to the dataset
            function in positional order, so if you want file.parquet to be the first
            argument of the dataset function, you must return it first. If you want a
            parameter to receive multiple files, return a list of the paths.
            For example, you would give the following return to provide a first
            argument with a single file and a second argument with two files:
            return ["file1.parquet", ["file2.parquet", "file3.parquet"]]

        Args:
            working_dir (str): The folder where the files must be stored

        Returns:
            Union[str, Tuple[str, ...], List[str]]: The path of the file(s) created, in
                the order they must be mapped to the dataset function
        """

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the object. This is used to save the
            object in a file.

        Returns:
            dict: A dictionary with the object's attributes.
        """
        return {self.IDENTIFIER: f"{self.__class__.__name__}.pkl"}


class OutputPlugin(ABC):
    """
    Abstract class for output plugins.

    Methods:
        trigger_output(*args, **kwargs)
            Trigger the exporting of the data. This function will receive the resulting
            data from the dataset function and must store it in the desired location.
    """

    IDENTIFIER = "output-plugin"

    @abstractmethod
    def trigger_output(self, *args, **kwargs):
        """
        Trigger the exporting of the data. This function will receive the resulting data
            from the dataset function and must store it in the desired location.

        Args:
            *args: The data to be exported
            **kwargs: Additional parameters to be used in the export

        Returns:
            None
        """

    def to_dict(self) -> dict:
        """
        Return a dictionary representation of the object. This is used to save the
            object in a file.

        Returns:
            dict: A dictionary with the object's attributes.
        """
        return {self.IDENTIFIER: f"{self.__class__.__name__}.pkl"}
