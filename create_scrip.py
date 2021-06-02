#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
import numpy
import argparse
import math
from scipy.spatial import ConvexHull

def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('-i','--input',type=str,help='input file',default=None)
    p.add_argument('-o','--output',type=str,help='output file',default=None)
    p.add_argument('-s','--scrip',type=str,help='scrip file',default=None)
    return vars(p.parse_args())

def scramble(xi,xo):
    xt=numpy.zeros([4])
    for i in range(4):
      xt[i]=xi[i]
    jf=[]
    jf.append(True)
    jf.append(True)
    jf.append(True)
    jf.append(True)
    for i in range(4):
        x=xt[i]
        for j in range(4):
            if jf[j]:
               #print(i,j,x,xo[j],abs(x-xo[j]),abs(x-xo[j])<0.01)
               wtf=abs(x-xo[j])<0.01
               #if abs(x-xo[j])<0.0001:
               if wtf:
                  #print("found: ",j),xo[j]
                  xi[j]=xo[j]
                  jf[j]=False
    return xi 

def compute_corner(cellx,celly,iloc,jloc):
    n=0
    idx=[]
    jdx=[]
    for i in range(3):
        #print(i,cellx[i+1],cellx[0])
        #print(cellx[i+1]<cellx[0])
        #print(cellx[i+1]==cellx[0])
        #print(celly[i+1] <celly[0])
        if (cellx[i+1]<cellx[0]) or (cellx[i+1]==cellx[0] and celly[i+1] <celly[0]):
           #print("in: ",i)
           n = i+1
    #print("n: ",n)

    if n==0:
       idx.append(iloc)
       jdx.append(jloc)
       idx.append(iloc+1)
       jdx.append(jloc)
       idx.append(iloc+1)
       jdx.append(jloc+1)
       idx.append(iloc)
       jdx.append(jloc+1)
    elif n==1:
       idx.append(iloc+1)
       jdx.append(jloc)
       idx.append(iloc+1)
       jdx.append(jloc+1)
       idx.append(iloc)
       jdx.append(jloc+1)
       idx.append(iloc)
       jdx.append(jloc)
    elif n==2:
       idx.append(iloc+1)
       jdx.append(jloc+1)
       idx.append(iloc)
       jdx.append(jloc+1)
       idx.append(iloc)
       jdx.append(jloc)
       idx.append(iloc+1)
       jdx.append(jloc)
    elif n==3:
       idx.append(iloc)
       jdx.append(jloc+1)
       idx.append(iloc)
       jdx.append(jloc)
       idx.append(iloc+1)
       jdx.append(jloc)
       idx.append(iloc+1)
       jdx.append(jloc+1)
    return(idx,jdx)
       

        
   

#------------------
# Opening the file
#------------------
comm_args    = parse_args()
Input_file   = comm_args['input']
Output_file  = comm_args['output']
scrip_file = comm_args['scrip']
ncFid = Dataset(Input_file, mode='r')
ncFidOut = Dataset(Output_file, mode='w', format='NETCDF4')
ncScrip = Dataset(scrip_file,mode='r')
tlon=ncScrip.variables['grid_corner_lon'][:]
tlat=ncScrip.variables['grid_corner_lat'][:]
#clon=ncScrip.variables['grid_center_lon'][:]
#clat=ncScrip.variables['grid_center_lat'][:]
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
print(ncols)
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
xt=numpy.zeros([4])
yt=numpy.zeros([4])

xy=numpy.zeros([4,2])


temp = ncFid.variables["lons"][:]
grid_center_lon[:]=temp.reshape([ncols])
tempxc=temp.reshape([ncols])

temp = ncFid.variables["lats"][:]
grid_center_lat[:]=temp.reshape([ncols])
tempyc=temp.reshape([ncols])

tempx = ncFid.variables["corner_lons"][:]
tempy = ncFid.variables["corner_lats"][:]
icnt=0
for n in range(6):
#for n in range(1):
   for j in range(im):
      for i in range(im):
   #for j in range(1):
      #for i in range(20):

          x[0]=tempx[n,j,i]
          x[1]=tempx[n,j,i+1]
          x[2]=tempx[n,j+1,i+1]
          x[3]=tempx[n,j+1,i]
          y[0]=tempy[n,j,i]
          y[1]=tempy[n,j,i+1]
          y[2]=tempy[n,j+1,i+1]
          y[3]=tempy[n,j+1,i]

          xt=tlon[icnt,:]
          yt=tlat[icnt,:]

          #print(x)
          x=scramble(x,xt)
          #print(x)
          #print(xt)
          y=scramble(y,yt)

       

          #lon_e=x.max()
          #lon_w=x.min()
          #xt=x
          #if (abs(lon_e - lon_w) > 180.0) and (tempxc[icnt] < 180.0):
             #xt=numpy.where(x>180.0,x-360.0,x)
          #elif (abs(lon_e - lon_w) > 180.0) and (tempxc[icnt] > 180.0):
             #xt=numpy.where(x<180.0,x+360.0,x)

          #xy[0,0]=xt[0]
          #xy[1,0]=xt[1]
          #xy[2,0]=xt[2]
          #xy[3,0]=xt[3]
          #xy[0,1]=y[0]
          #xy[1,1]=y[1]
          #xy[2,1]=y[2]
          #xy[3,1]=y[3]
          #hull=ConvexHull(xy,qhull_options='Qa')
          #print(hull.vertices[0])


          #idx,jdx=compute_corner(xt,y,i,j)

          #grid_corner_lon[icnt,0]=tempx[n,j,i]
          #grid_corner_lon[icnt,1]=tempx[n,j,i+1]
          #grid_corner_lon[icnt,2]=tempx[n,j+1,i+1]
          #grid_corner_lon[icnt,3]=tempx[n,j+1,i]

          #grid_corner_lat[icnt,0]=tempy[n,j,i]
          #grid_corner_lat[icnt,1]=tempy[n,j,i+1]
          #grid_corner_lat[icnt,2]=tempy[n,j+1,i+1]
          #grid_corner_lat[icnt,3]=tempy[n,j+1,i]
          #grid_corner_lon[icnt,0]=tempx[n,j,i]

          #grid_corner_lon[icnt,0]=tempx[n,jdx[0],idx[0]]
          #grid_corner_lon[icnt,1]=tempx[n,jdx[1],idx[1]]
          #grid_corner_lon[icnt,2]=tempx[n,jdx[2],idx[2]]
          #grid_corner_lon[icnt,3]=tempx[n,jdx[3],idx[3]]

          #grid_corner_lat[icnt,0]=tempy[n,jdx[0],idx[0]]
          #grid_corner_lat[icnt,1]=tempy[n,jdx[1],idx[1]]
          #grid_corner_lat[icnt,2]=tempy[n,jdx[2],idx[2]]
          #grid_corner_lat[icnt,3]=tempy[n,jdx[3],idx[3]]

          #grid_corner_lon[icnt,0]=x[hull.vertices[0]]
          #grid_corner_lon[icnt,1]=x[hull.vertices[1]]
          #grid_corner_lon[icnt,2]=x[hull.vertices[2]]
          #grid_corner_lon[icnt,3]=x[hull.vertices[3]]

          #grid_corner_lat[icnt,0]=y[hull.vertices[0]]
          #grid_corner_lat[icnt,1]=y[hull.vertices[1]]
          #grid_corner_lat[icnt,2]=y[hull.vertices[2]]
          #grid_corner_lat[icnt,3]=y[hull.vertices[3]]

          grid_corner_lon[icnt,0]=x[0]
          grid_corner_lon[icnt,1]=x[1]
          grid_corner_lon[icnt,2]=x[2]
          grid_corner_lon[icnt,3]=x[3]

          grid_corner_lat[icnt,0]=y[0]
          grid_corner_lat[icnt,1]=y[1]
          grid_corner_lat[icnt,2]=y[2]
          grid_corner_lat[icnt,3]=y[3]
          icnt=icnt+1

     
ncFidOut.close()


#-----------------
# Closing the file
#-----------------
ncFid.close()

