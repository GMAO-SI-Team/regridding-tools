#!/usr/bin/env python

#-------------
# Load modules
#-------------
from netCDF4 import Dataset
from scrip_creator import create_scrip_from_geos
import argparse

def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('-i','--input',type=str,help='input file',default=None)
    p.add_argument('-o','--output',type=str,help='output file',default=None)
    return vars(p.parse_args())

comm_args    = parse_args()
Input_file   = comm_args['input']
Output_file  = comm_args['output']

create_scrip_from_geos(Input_file, Output_file)
