import os

import numpy as np
import six
from pandas import HDFStore, DataFrame
from scipy import signal
from scipy.io import loadmat


def mat_to_data(path):
    mat = loadmat(path)
    names = mat['dataStruct'].dtype.names
    ndata = {n: mat['dataStruct'][n][0, 0] for n in names}
    for kk, vv in six.iteritems(ndata):
        if vv.shape == (1, 1):
            ndata[kk] = vv[0, 0]
    return ndata


def get_label(infile):
    return infile.split(".")[-2][-1] == "0"


def periodogram_gen_one_name(folder):
    file_paths = list(filter(lambda x: x.endswith(".mat"), os.listdir(folder)))
    for file_path in file_paths:
        try:
            infile = os.path.join(folder, file_path)
            label = get_label(file_path)
            data = mat_to_data(infile)
            xx = data["data"].transpose(1, 0)
            (freq, powspec) = signal.periodogram(xx)
            yield powspec, np.array([[label]]), "subject" + file_path[:-4]
        except ValueError:
            continue

data_dir = os.path.expanduser("~/data/seizure-prediction")

h5filename = os.path.join(data_dir, "periodograms.h5")

# Save periodograms in HDF5 file
with HDFStore(h5filename) as h5:
    for xx, yy, ff in periodogram_gen_one_name(data_dir):
        print(ff, xx.shape, yy.shape)
        dfx = DataFrame(xx)
        dfx.name = yy
        h5[ff] = dfx

# Read back periodograms from HDF5 file to be safe
h5 = HDFStore(h5filename)
print("=====================")
print("keys:")
print(h5.keys())
h5.close()
