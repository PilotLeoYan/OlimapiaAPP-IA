import numpy as np
from typing import List, Tuple, TypeAlias


DataArray: TypeAlias = np.ndarray[Tuple[int, int], np.dtype[np.str_]]
ListPaths: TypeAlias = List[str]


def DataLoader(
    extract_all: bool = False, 
    headers: bool = False, 
    index: bool = False, 
    path: str = r'./dataset'
    ) -> Tuple[DataArray, ListPaths]:
    """
    Import data from data.csv and a list with all paths of the images
    in the dataset.

    Args:
        extract_all (bool): Return optional columns like pencil brand, margin and type of filling.
        headers (bool): Return data with the first row of the headers.
        index (bool): Return data with the first columns of index.
        path (str): Path of the dataset folder or directory.
    Returns:
        tuple: Data from data.csv and a list with all paths of the images.
    """
    ...


def _loadcsv(
        csv_path: str, 
        extract_all: bool, 
        headers: bool, 
        index: bool
    ) -> DataArray:
    """Load data.csv into a np.ndarray"""
    ...

def _loadpaths(
        path: str
    ) -> ListPaths:
    """Return a list with all paths of the images."""
    ...