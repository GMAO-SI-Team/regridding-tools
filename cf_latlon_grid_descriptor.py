#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy as np
import argparse
import math

def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('-d','--dateline',type=str,help='pole',default=None)
    p.add_argument('-p','--pole',type=str,help='dateline',default=None)
    p.add_argument('-i','--im_world',type=str,help='lons',default=None)
    p.add_argument('-j','--jm_world',type=str,help='lats',default=None)
    p.add_argument('-o','--output_file',type=str,help='output',default=None)
    p.add_argument('-u','--units',type=str,help='units',default="rad")

    return vars(p.parse_args())

def compute_range(x0,x1,n):
    output=np.zeros((n),dtype=np.double)
    output[0]=x0
    output[n-1]=x1
    delta=(x1-x0)/(n-1)
    for i in range(n-1):
       output[i+1] = x0 + (int(i+1)*delta)
    return output

def compute_lon_centers(dateline,im):
    lons=np.zeros((im),dtype=np.double)
    delta = 360.0/float(im)
    if dateline=='DC':
       min_coord = -180.0
       max_coord = 180.0-delta
    elif dateline=='DE':
       min_coord=-180.0+delta/2.0
       max_coord=180.0-delta/2.0

    lons=compute_range(min_coord,max_coord,im)
    return lons

def compute_lat_centers(pole,im):
    lats=np.zeros((im),dtype=np.double)
    if pole=='PC':
       min_coord = -90.0
       max_coord = 90.0
    elif pole=='PE':
       delta = 180.0/float(im)
       min_coord=-90.0+delta/2.0
       max_coord=90.0-delta/2.0

    lats=compute_range(min_coord,max_coord,im)
    return lats

def compute_lon_corners(dateline,im):
    lons=np.zeros((im+1),dtype=np.double)
    delta = 360.0/float(im)
    if dateline=='DC':
       min_coord = -180.0-delta/2.0
       max_coord = 180.0-delta/2.0
    elif dateline=='DE':
       min_coord=-180.0
       max_coord=180.0

    lons=compute_range(min_coord,max_coord,im+1)
    return lons

def compute_lat_corners(pole,im):
    lats=np.zeros((im+1),dtype=np.double)
    if pole=='PC':
       delta=180.0/(float(im)-1)
       min_coord = -90.0-delta/2.0
       max_coord = 90.0+delta/2.0
    elif pole=='PE':
       delta = 180.0/float(im)
       min_coord=-90.0
       max_coord=90.0

    lats=compute_range(min_coord,max_coord,im+1)
    if pole=='PC':
       lats[0]=-90.0
       lats[im]=90.0
    return lats

class LatLonGridFactory(object):

   def __init__(self,im,jm,dateline,pole,units):

      self.lons=compute_lon_centers(dateline,im)
      self.lats=compute_lat_centers(pole,jm)
      self.lon_bnds=compute_lon_corners(dateline,im)
      self.lat_bnds=compute_lat_corners(pole,jm)
      if units=='rad':
         self.lons=self.lons*math.pi/180.0
         self.lats=self.lats*math.pi/180.0
         self.lon_bnds=self.lon_bnds*math.pi/180.0
         self.lat_bnds=self.lat_bnds*math.pi/180.0

   def write_grid(self,output_file):
       
      ncFid = Dataset(output_file, mode='w', format='NETCDF4')

      im_world=len(self.lons)
      jm_world=len(self.lats)

      lon_bndso=np.zeros((im_world,2),dtype=np.double)
      lat_bndso=np.zeros((jm_world,2),dtype=np.double)

      for i in range(im_world):
          #lon_bndso[0,i]=self.lon_bnds[i]
          #lon_bndso[1,i]=self.lon_bnds[i+1]
          lon_bndso[i,0]=self.lon_bnds[i]
          lon_bndso[i,1]=self.lon_bnds[i+1]

      for i in range(jm_world):
          #lat_bndso[0,i]=self.lat_bnds[i]
          #lat_bndso[1,i]=self.lat_bnds[i+1]
          lat_bndso[i,0]=self.lat_bnds[i]
          lat_bndso[i,1]=self.lat_bnds[i+1]


      lon_dim=ncFid.createDimension('lon',im_world)
      lat_dim=ncFid.createDimension('lat',jm_world)
      b_dim=ncFid.createDimension('bound',2)

      lon_var=ncFid.createVariable('lon','f8',('lon'))
      lat_var=ncFid.createVariable('lat','f8',('lat'))
      #lonb_var=ncFid.createVariable('lon_bnds','f8',('bound','lon'))
      #latb_var=ncFid.createVariable('lat_bnds','f8',('bound','lat'))
      lonb_var=ncFid.createVariable('lon_bnds','f8',('lon','bound'))
      latb_var=ncFid.createVariable('lat_bnds','f8',('lat','bound'))


      setattr(lon_var,'long_name','longitude')
      setattr(lat_var,'long_name','latitude')
      setattr(lon_var,'standard_name','longitude')
      setattr(lat_var,'standard_name','latitude')
      setattr(lon_var,'units','degrees_east')
      setattr(lat_var,'units','degrees_north')
      setattr(lon_var,'bounds','lon_bnds')
      setattr(lat_var,'bounds','lat_bnds')

      lon_var[:]=self.lons[:]
      lat_var[:]=self.lats[:]

      lonb_var[:,:]=lon_bndso[:,:]
      latb_var[:,:]=lat_bndso[:,:]

      ncFid.close()
