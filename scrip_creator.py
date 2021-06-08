#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy
import argparse
import math
# Opening the file
#------------------
def create_scrip_from_geos(Input_file,Output_file):
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

   #for att in ncFid.ncattrs():
       #setattr(ncFidOut,att,getattr(ncFid,att))
   setattr(ncFidOut,"GridDescriptionFormat","SCRIP")
   setattr(ncFidOut,"title","GMAO PE24x144-CF Grid")

   ncols = len(xdim)*len(ydim)*len(nf)
   im=len(xdim)
   ncolOut = ncFidOut.createDimension('grid_size', ncols)
   grsz = ncFidOut.createDimension('grid_corners',4)
   grnk = ncFidOut.createDimension('grid_rank',1)


   grid_dims = ncFidOut.createVariable('grid_dims','i4',('grid_rank'))
   grid_dims[:]=1
   grid_imask = ncFidOut.createVariable('grid_imask','i4',('grid_size'))
   grid_imask[:]=1
   grid_center_lon = ncFidOut.createVariable('grid_center_lon','f8',('grid_size'))
   setattr(grid_center_lon,'units','degrees')
   grid_center_lat = ncFidOut.createVariable('grid_center_lat','f8',('grid_size'))
   setattr(grid_center_lat,'units','degrees')
   grid_corner_lon = ncFidOut.createVariable('grid_corner_lon','f8',('grid_size','grid_corners'))
   setattr(grid_corner_lon,'units','degrees')
   grid_corner_lat = ncFidOut.createVariable('grid_corner_lat','f8',('grid_size','grid_corners'))
   setattr(grid_corner_lat,'units','degrees')

   grid_area = ncFidOut.createVariable('grid_area','f8',('grid_size'))
   setattr(grid_area,'units','radians^2')
   grid_area[:]=0

   Exclude_Var = ['Xdim','Ydim','time','lev','nf','ncontact','cubed_sphere','contacts','orientation','anchor']
   do_var = ['lons','lats','corner_lons','corner_lats']

   x=numpy.zeros([4])
   y=numpy.zeros([4])

   newx = numpy.zeros([ncols,4])
   newy = numpy.zeros([ncols,4])

   temp = ncFid.variables["lons"][:]
   grid_center_lon[:]=temp.reshape([ncols])
   tempxc=temp.reshape([ncols])

   temp = ncFid.variables["lats"][:]
   grid_center_lat[:]=temp.reshape([ncols])
   tempyc=temp.reshape([ncols])

   tempx = ncFid.variables["corner_lons"][:]
   tempy = ncFid.variables["corner_lats"][:]
   icnt=0

   tempx[1,:,0]=tempx[0,:,im]
   tempy[1,:,0]=tempy[0,:,im]

   tempx[2,::-1,0]=tempx[0,im,:]
   tempy[2,::-1,0]=tempy[0,im,:]

   tempx[4,im,::-1]=tempx[0,:,0]
   tempy[4,im,::-1]=tempy[0,:,0]

   tempx[5,im,:]=tempx[0,0,:]
   tempy[5,im,:]=tempy[0,0,:]

   tempx[2,0,:]=tempx[1,im,:]
   tempy[2,0,:]=tempy[1,im,:]

   tempx[3,0,::-1]=tempx[1,:,im]
   tempy[3,0,::-1]=tempy[1,:,im]

   tempx[5,::-1,im]=tempx[1,0,:]
   tempy[5,::-1,im]=tempy[1,0,:]

   tempx[3,:,0]=tempx[2,:,im]
   tempy[3,:,0]=tempy[2,:,im]

   tempx[4,::-1,0]=tempx[2,im,:]
   tempy[4,::-1,0]=tempy[2,im,:]

   tempx[2,:,im]=tempx[3,:,0]
   tempy[2,:,im]=tempy[3,:,0]

   tempx[4,0,:]=tempx[3,im,:]
   tempy[4,0,:]=tempy[3,im,:]

   tempx[5,0,::-1]=tempx[3,:,im]
   tempy[5,0,::-1]=tempy[3,:,im]

   tempx[5,:,0]=tempx[4,:,im]
   tempy[5,:,0]=tempy[4,:,im]

   for n in range(6):
      for j in range(im):
         for i in range(im):

             newx[icnt,0]=tempx[n,j,i]
             newx[icnt,1]=tempx[n,j,i+1]
             newx[icnt,2]=tempx[n,j+1,i+1]
             newx[icnt,3]=tempx[n,j+1,i]

             newy[icnt,0]=tempy[n,j,i]
             newy[icnt,1]=tempy[n,j,i+1]
             newy[icnt,2]=tempy[n,j+1,i+1]
             newy[icnt,3]=tempy[n,j+1,i]

             icnt=icnt+1

   grid_corner_lon[:]=newx[:]
   grid_corner_lat[:]=newy[:]
   ncFidOut.close()
   ncFid.close()

