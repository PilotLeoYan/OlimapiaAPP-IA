import csv
import numpy as np
import os


__version__ = "1.0.0"
__all__ = [
    "DataLoader"
]


def DataLoader(extract_all=False, headers=False, index=False, path=r'./dataset'):
    csv_path = os.path.join(path, r'data.csv')
    
    data = _loadcsv(csv_path, extract_all, headers, index)
    paths = _loadpaths(path)
    return data, paths


def _loadcsv(csv_path, extract_all, headers, index):
    with open(file=csv_path, newline='') as file:
        csv_reader = csv.reader(file, )
        rows = [row for row in csv_reader]

    data = np.array(rows)

    if not headers:
        data = np.delete(data, obj=[0], axis=0)

    if not index:
        data = np.delete(data, obj=[0], axis=1)

    if extract_all:
        return data
    # delete pencil brand, margin and type of filling columns
    if index:
        data = np.delete(data, obj=[0, 1, 2], axis=1)
    data = np.delete(data, obj=[1, 2, 3], axis=1)

    return data

def _loadpaths(path):
    folders = (
        'cam-1',
    )

    paths = [os.listdir(os.path.join(path, folder)) for folder in folders]
    return [_path for folder in paths for _path in folder]