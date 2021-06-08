#!/usr/bin/env python

from cf_latlon_grid_descriptor import LatLonGridFactory
from convertCStoScrip import convert_cs_to_scrip
from scrip_creator import create_scrip_from_geos
import argparse
import sys
import os,subprocess
import glob
from netCDF4 import Dataset


def generate_esmf_weights(cube_size,cube_file,ll_file,nproc,weights,method):
   
    cube6=cube_size*6
    scrip_file=cube_file
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

    exec_path="ESMF_RegridWeightGen"
    subprocess.call(["mpirun","-np",nproc,exec_path,"-s",scrip_file,"-d",ll_file,"-w",weights,m_opt,m_arg,"--check","--netCDF4","--no_log"])

def run_remap(input_file,output_file,weights,variables):

   cmd="ncremap"
   args = [cmd,"-i",input_file,"-o",output_file,"-m",weights,"--preserve=mean"]
   if variables != 'all':
      args.append("-v")
      args.append(variables)
   subprocess.call(args)


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
    p.add_argument('--grid_dir',type=str,help='precompute_grid_dir',default=".")
    p.add_argument('--num_tasks',type=str,help='num_tasks',default="1")
    p.add_argument('-v','--vars',type=str,help='comma separated list of variables to regrid',default='all')
    

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
   grid_path = comm_args['grid_dir']
   method = comm_args['method']
   mpi_task = comm_args['num_tasks']
   vars_opt = comm_args['vars']

   ncFid = Dataset(input_file,mode='r')
   xdim = ncFid.variables['Xdim'][:]
   cube_size = len(xdim)
   cube_file = "PE"+str(cube_size)+"x"+str(cube_size*6)+"-CF.nc4"

   cube_path = grid_path+"/"+cube_file

   if grid_path != ".":
      if (not os.path.isfile(cube_path)):
         print("Generating scrip file")
         create_scrip_from_geos(input_file,cube_path)
   else:
      create_scrip_from_geos(input_file,cube_path)
   

   latlon_grid = LatLonGridFactory(im_world,jm_world,dateline,pole,"degrees")


   ll_file=pole+str(im_world)+"x"+str(jm_world)+"-"+dateline
   latlon_grid.write_grid(ll_file)

   temp_file="temp_1d.nc4"
   temp_out="temp_out.nc4"

   weight_file = "PE"+str(cube_size)+"x"+str(cube_size*6)+"-CF_"+str(im_world)+"x"+str(jm_world)+"-"+dateline+"_"+method+".nc4" 
   weight_path = grid_path+"/"+weight_file
   if grid_path != ".":
      if (not os.path.isfile(weight_path)):
         generate_esmf_weights(cube_size,cube_path,ll_file,mpi_task,weight_path,method)
   else:
      generate_esmf_weights(cube_size,cube_path,ll_file,mpi_task,weight_path,method)

   convert_cs_to_scrip(input_file,temp_file)
   run_remap(temp_file,temp_out,weight_path,vars_opt)

   strip_vars(temp_out,output_file)

   fileList=[temp_out,temp_file,ll_file]
   if (grid_path == "."):
      fileList.append(cube_path)
      fileList.append(weight_path)
   for filePath in fileList:
      os.remove(filePath)


   fileList=glob.glob('PET*.Log')
   for filePath in fileList:
      os.remove(filePath)
      

