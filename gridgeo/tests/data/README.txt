# COAWST

http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/jcwarner/Projects/Sandy/triple_nest/00_dir_NYB05.ncml
ncks -F --dimension ocean_time,1 --variable temp,salt,u,v,lat_psi,lon_psi,grid,s_rho,Cs_r,zeta,h,hc $url 00_dir_NYB05.nc --overwrite

# FVCOM

url=http://crow.marine.usf.edu:8080/thredds/dodsC/FVCOM-Nowcast-Agg.nc
ncks -F --dimension time,1 --variable temp,salinity,fvcom_mesh,nv,lon,lat,lonc,latc,siglay,zeta,h $url FVCOM-Nowcast-Agg.nc --overwrite

## subset
ncks -F --dimension time,1, -F --dimension nele,1,10 --variable fvcom_mesh,nv,lon,lat,lonc,latc $url FVCOM-Nowcast-Agg.nc --overwrite

# Bad grid (incomplete)

http://geoport.whoi.edu/thredds/dodsC/clay/usgs/users/jcwarner/Projects/Sandy/triple_nest/00_dir_NYB05.ncml
ncks -F --dimension ocean_time,1 --variable grid $url grid.nc --overwrite
