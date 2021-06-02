#!/usr/bin/env python

from cf_latlon_grid_descriptor import LatLonGridFactory
import argparse
import sys

def parse_args():
    p = argparse.ArgumentParser(description='Flatten a lat-lon to 1D')
    p.add_argument('-d','--dateline',type=str,help='pole',default=None)
    p.add_argument('-p','--pole',type=str,help='dateline',default=None)
    p.add_argument('-i','--im_world',type=str,help='lons',default=None)
    p.add_argument('-j','--jm_world',type=str,help='lats',default=None)
    p.add_argument('-o','--output_file',type=str,help='output',default=None)
    p.add_argument('-u','--units',type=str,help='units',default="rad")

    return vars(p.parse_args())

if __name__ == '__main__':
   sys.path.append(".")

   comm_args    = parse_args()
   im_world = int(comm_args['im_world'])
   jm_world = int(comm_args['jm_world'])
   pole = comm_args['pole']
   dateline = comm_args['dateline']
   output_file = comm_args['output_file']
   units = comm_args['units']

   latlon_grid = LatLonGridFactory(im_world,jm_world,dateline,pole,units)

   latlon_grid.write_grid(output_file)

