import dask
import dask.array as da
from dask.local import get_sync

dask.set_options(get=get_sync)


class DaskNetCDF(object):
    def __init__(self, variable, array=None, chunks=None):
        self._variable = variable
        self.chunks = -1 if not chunks else chunks
        if array is None:
            self.array = da.from_array(variable, chunks=chunks)
        else:
            self.array = array

    def __repr__(self):
        lines = self._variable.__repr__().split("\n")
        new_lines = ["<class 'dask_netcdf.DaskNetCDF'>"]
        for line in lines[1:]:
            if "current shape" in line:
                left = line.split("=")[0]
                line = "= ".join([left, str(self.array.shape)])
            new_lines.append(line)

        return "\n".join(new_lines)

    @property
    def dtype(self):
        return self.array.dtype

    @property
    def shape(self):
        return self.array.shape

    def transpose(self, *axes):
        new_array = self.array.transpose(*axes)
        return DaskNetCDF(
            variable=self._variable, array=new_array, chunks=self.chunks
        )

    @property
    def T(self):
        return self.transpose()

    def __getitem__(self, index):
        return self.array.__getitem__(index).compute()

    def __add__(self, other):
        new_array = self.array.__add__(other)
        return DaskNetCDF(
            variable=self._variable, array=new_array, chunks=self.chunks
        )

    def __sub__(self, other):
        new_array = self.array.__sub__(other)
        return DaskNetCDF(
            variable=self._variable, array=new_array, chunks=self.chunks
        )

    def astype(self, dtype, **kwargs):
        new_array = self.array.astype(dtype, **kwargs)
        return DaskNetCDF(
            variable=self._variable, array=new_array, chunks=self.chunks
        )
