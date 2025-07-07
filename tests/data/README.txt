The netcdf files here are based on

$ url="http://colossus.dl.stevens-tech.edu:8080/thredds/dodsC/latest/Complete_gcmplt.nc"
$ ncks -d time,0 -d sigma,0 -v temp $url unknown_2d.nc

$ url="http://thredds.cencoos.org/thredds/dodsC/CENCOOS_CA_ROMS_FCST.nc"
$ ncks -d time,0 -d depth,0 -v temp $url unknown_1d.nc

$ url="http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc"
$ ncks -d time,0 -d siglay,0 -v temp,fvcom_mesh $url ugrid.nc

$ url="http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/jcwarner/Sandy/triple_nest/00_dir_NYB07.ncml"
$ ncks -d ocean_time,0 -d s_rho,0 -v temp $url sgrid.nc

then a .cdl was created and edited to reduce the size on the .nc.
