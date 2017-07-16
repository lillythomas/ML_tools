import os, sys
import gdal
from gdalconst import *
import os, glob, time, re
import geopandas as gpd
import fiona
from shapely.geometry import shape, mapping
from shapely.ops import unary_union
import itertools
import time
import multiprocessing
import ogr
from subprocess import call
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', '-p', help="path to binary rasters")
parser.add_argument('--mode', '-m', help="options: (vectorize, extract, merge, dissolve, explode) 1) to just vectorize from raster, 2) to extract certain values in existing vector dataset(s), 3) to merge existing vector datasets, 4) to dissolve a merged vector dataset, 5) to explode a multipart polygon to singleparts")
parser.add_argument('--mergeFile', '-mF', help="the destination vector dataset for appending others upon")
parser.add_argument('--dissolveFile', '-dF', help="the singlepart vector dataset generated from dissolving the merged dataset")


args = parser.parse_args()
print args

path=args.path
mode=args.mode

start_time = time.time()


def vectorize(file):
    filename_split = os.path.splitext(file)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    os.system('mkdir '+path+'tmp/')
    outPoly = path+'tmp/'+basename+'.shp'
    call(["gdal_polygonize.py", file, "-f", "ESRI Shapefile", outPoly, basename, 'DN'])
    print("vectorized")

def extractVal(file):
    filename_split = os.path.splitext(file)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    imp_gpd = gpd.GeoDataFrame.from_file(file)
    imp_gpd = imp_gpd.loc[imp_gpd['DN'] == 1]
    extract_outPath = path+'tmp/extract/'
    if not os.path.exists(extract_outPath):
        os.mkdir(extract_outPath)
    imp_gpd.to_file(path+'tmp/extract/'+basename+'_extract.shp')
    imp_gpd.to_file(path+'tmp/extract/'+basename+'_extract.shp')
    print("extracted")

def dissolve(file):
    filename_split = os.path.splitext(file)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    imp_gpd = gpd.read_file(file)
    print(imp_gpd.columns)
    #imp_gpd = imp_gpd[['DN', 'geometry']]
    #imp_gpd = imp_gpd.dissolve(by='DN')
    #imp_gpd.to_file(path+basename+'_dissolve.shp')
    dissolveFile = path+basename+"_dissolve.shp"
    with fiona.open(file) as input:
        meta = input.meta
        with fiona.open(dissolveFile, 'w', **meta) as output:
                e = sorted(input, key=lambda k: k['properties']['DN'])
                for key, group in itertools.groupby(e, key=lambda x:x['properties']['DN']):
                    properties, geom = zip(*[(feature['properties'],shape(feature['geometry'])) for feature in group])
                    output.write({'geometry': mapping(unary_union(geom)), 'properties': properties[0]})
    print("dissolved")
    return dissolveFile   

def explode(file):
    filename_split = os.path.splitext(file)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    explodeFile = path+basename+"_singlepart.shp"
    with fiona.open(file) as input:
        with fiona.open(explodeFile,'w',driver=input.driver, crs=input.crs, schema=input.schema) as output:
	    for multi in input:
	        for poly in shape(multi['geometry']):
		    output.write({'properties': multi['properties'],'geometry': mapping(poly)})
    print("exploded into singleparts")
    return explodeFile 
                    
p = multiprocessing.Pool(30)
if mode=='vectorize':
  for f in glob.glob(path+'*.png'):
      p.apply_async(vectorize, [f])
if mode=='extract':      
  for f in glob.glob(path+'tmp/*.shp'):
      p.apply_async(extractVal, [f])
p.close()
p.join()

if mode=='merge':
    mergeFile = args.mergeFile
    os.system("for f in "+path+"*.shp; do ogr2ogr -update -append "+mergeFile+" $f -f 'ESRI Shapefile'; done;")
    os.system("ogrinfo -so -al "+mergeFile)
    print('merged')

if mode=='dissolve':
    mergeFile = args.mergeFile
    dissolve(mergeFile)
    os.system("ogrinfo -so -al "+mergeFile[:-4]+"_dissolve.shp")
    print('dissolved')
    
if mode=='explode':
    dissolveFile = args.dissolveFile
    explode(dissolveFile)
    os.system("ogrinfo -so -al "+dissolveFile[:-4]+"_singlepart.shp")
    print('exploded into singleparts')
