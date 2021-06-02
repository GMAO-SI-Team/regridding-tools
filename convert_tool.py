#!/usr/bin/env python

from cf_latlon_grid_descriptor import LatLonGridFactory
from convertCStoScrip import convert_cs_to_scrip
import argparse
import sys
import os,subprocess
from netCDF4 import Dataset

def generate_esmf_weights(cube_size,ll_file,weights,method):
   
    cube6=cube_size*6
    scrip_file="/discover/nobackup/bmauer/Cubed_Sphere_Grids_WithArea/PE"+str(cube_size)+"x"+str(cube6)+"-CF.nc4"
    input_arg="-s "+scrip_file
    dest_arg="-d "+ll_file
    w_arg="-w "+weights
    extra_args="--check --netCDF4"
    if method=="bilinear":
       m_opt="--line_type"
       m_arg="greatcircle"
    elif method=="conserve":
       m_opt="-m"
       m_arg="conserve"

    exec_path="/discover/swdev/gmao_SIteam/Baselibs/ESMA-Baselibs-6.1.0/x86_64-pc-linux-gnu/ifort_19.1.3.304-intelmpi_19.1.3.304/Linux/bin/ESMF_RegridWeightGen"
    subprocess.call([exec_path,"-s",scrip_file,"-d",ll_file,"-w",weights,m_opt,m_arg,"--check","--netCDF4"])

def run_remap(input_file,output_file,weights):

   cmd="ncremap"
   subprocess.call([cmd,"-i",input_file,"-o",output_file,"-m",weights,"--preserve=mean"])


def strip_vars(input_file,output_file):
   cmd="ncks"
   subprocess.call([cmd,"-C","-x", "-v", "area,lon_bnds,lat_bnds,gw,ncol",input_file,output_file])


def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('-d','--dateline',type=str,help='pole',default=None)
    p.add_argument('-p','--pole',type=str,help='dateline',default=None)
    p.add_argument('-i','--im_world',type=str,help='lons',default=None)
    p.add_argument('-j','--jm_world',type=str,help='lats',default=None)
    p.add_argument('-n','--input_file',type=str,help='input',default=None)
    p.add_argument('-o','--output_file',type=str,help='output',default=None)
    p.add_argument('-m','--method',type=str,help='method',default="bilinear")

    return vars(p.parse_args())

if __name__ == '__main__':
   sys.path.append(".")

   comm_args    = parse_args()
   im_world = int(comm_args['im_world'])
   jm_world = int(comm_args['jm_world'])
   pole = comm_args['pole']
   dateline = comm_args['dateline']
   output_file = comm_args['output_file']
   input_file = comm_args['input_file']

   method = comm_args['method']

   latlon_grid = LatLonGridFactory(im_world,jm_world,dateline,pole,"degrees")

   ll_file=pole+str(im_world)+"x"+str(jm_world)+"-"+dateline
   latlon_grid.write_grid(ll_file)

   ncFid = Dataset(input_file,mode='r')
   xdim = ncFid.variables['Xdim'][:]
   cube_size = len(xdim)

   temp_file="temp_1d.nc4"
   temp_out="temp_out.nc4"
   weight_file="temp_weights.nc4"

   convert_cs_to_scrip(input_file,temp_file)

   generate_esmf_weights(cube_size,ll_file,weight_file,method)

   run_remap(temp_file,temp_out,weight_file)

   strip_vars(temp_out,output_file)

   subprocess.call(["rm",temp_out,temp_file,weight_file,"PET*.RegridWeightGen.Log",ll_file])


