#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy
import argparse

def convert_cs_to_scrip(Input_file,Output_file):
   ncFid = Dataset(Input_file, mode='r')
   ncFidOut = Dataset(Output_file, mode='w', format='NETCDF4')
   #---------------------
   # Extracting variables
   #---------------------

   haveLev = False
   for dim in ncFid.dimensions:
       if dim == 'lev':
              haveLev = True

   time = ncFid.variables['time'][:]
   if haveLev:
      lev  = ncFid.variables['lev'][:]
   ydim  = ncFid.variables['Xdim'][:]
   xdim  = ncFid.variables['Ydim'][:]
   nf  = ncFid.variables['nf'][:]

   for att in ncFid.ncattrs():
       setattr(ncFidOut,att,getattr(ncFid,att))

   ncols = len(xdim)*len(ydim)*len(nf)
   ncolOut = ncFidOut.createDimension('ncol', ncols)
   ncolsOut = ncFidOut.createVariable('ncol','f4',('ncol',))
   ncolsOut[:] = range(ncols)

   if haveLev:
      levOut = ncFidOut.createDimension('lev', len(lev))
      levsOut = ncFidOut.createVariable('lev','f4',('lev',))
      for att in ncFid.variables['lev'].ncattrs():
          setattr(ncFidOut.variables['lev'],att,getattr(ncFid.variables['lev'],att))
      levsOut[:] = lev

   timeOut = ncFidOut.createDimension('time', len(time))
   timesOut = ncFidOut.createVariable('time','f4',('time',))
   for att in ncFid.variables['time'].ncattrs():
       setattr(ncFidOut.variables['time'],att,getattr(ncFid.variables['time'],att))
   timesOut[:] = time

   Exclude_Var = ['Xdim','Ydim','time','lev','nf','ncontact','cubed_sphere','contacts','orientation','anchor']
   for var in ncFid.variables:
      if var not in Exclude_Var:
         temp = ncFid.variables[var][:]
         dim_size =len(temp.shape)
         if dim_size == 5:
            Tout = ncFidOut.createVariable(var,'f4',('time','lev','ncol',),fill_value=1.0e15)
            for att in ncFid.variables[var].ncattrs():
               if att != "_FillValue" and att != "grid_mapping":
                  setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
            Tout[:,:,:] = temp.reshape([ len(time),len(lev),ncols])
         elif dim_size == 4:
            Tout = ncFidOut.createVariable(var,'f4',('time','ncol',),fill_value=1.0e15)
            for att in ncFid.variables[var].ncattrs():
               if att != "_FillValue" and att != "grid_mapping":
                  setattr(ncFidOut.variables[var],att,getattr(ncFid.variables[var],att))
            Tout[:,:] = temp.reshape([ len(time),ncols])
   ncFidOut.close()


   #-----------------
   # Closing the file
   #-----------------
   ncFid.close()

