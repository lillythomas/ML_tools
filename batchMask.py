import os, sys, glob, time, argparse, multiprocessing
from PIL import Image
import numpy as np
import fiona, shapely
import geopandas as gpd

parser = argparse.ArgumentParser()
parser.add_argument('--images', '-i', help="full-path to 3 channel image(s)")
parser.add_argument('--mask', '-m', help="the dataset to be used for labeling images")
parser.add_argument('--mode', '-md', help="translate labels or rasterize, options: 1) translate 2) rasterize")
parser.add_argument('--inField', '-inF', help="the existing field with which to use as the identifying class")
parser.add_argument('--outField', '-oF', help="the zero-based and sequential destination field with which to use as the identifying class")
parser.add_argument('--outPath', '-o', help="full-path to output tiles")

args = parser.parse_args()
print args

images=args.images
mask=args.mask
inField=args.inField
outField=args.outField
outPath=args.outPath

def translateLabels(mask):
    filename_split = os.path.splitext(mask)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    geo = gpd.read_file(mask)
    print(geo.columns)
    print(np.unique(geo[str(inField)]))
    geo[str(outField)] = geo[str(inField)]
    inF_arr = np.unique(geo[str(inField)])
    outF_arr = np.arange(0, len(inF_arr))
    print(outF_arr)
    print(len(inF_arr))
    print(len(outF_arr))
    inF_list = inF_arr.tolist()
    outF_list = outF_arr.tolist()
    for i, j in zip(inF_list, outF_list):
        geo.loc[geo[str(outField)]==i, str(outField)] = j
    print(np.unique(geo[str(outField)]))
    outMask = geo.to_file(outPath+basename+'_translated'+fileext, driver='ESRI Shapefile')
    return geo, outMask
    
def labelGrey(raster):
    filename_split = os.path.splitext(mask)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    os.system('ogr2ogr -f GeoJSON '+filename_zero+'.geojson '+filename_zero+'.shp')
    geojson = filename_zero+'.geojson'
    filename_split1 = os.path.splitext(raster)
    filename_zero1, fileext1 = filename_split1
    basename1 = os.path.basename(filename_zero1)    
    os.system('rio rasterize '+filename_zero1+'_labels.tif --fill 255 --force-overwrite --property '+str(outField)+' --like '+raster+' < '+geojson)
    rasterGrey = filename_zero1+'_labels.tif'
    os.system('gdal_rasterize -a '+str(outField)+' -l '+mask+' '+rasterGrey+' '+outPath+rasterGrey[:-4]+'.tif')
    return geojson, rasterGrey

def translateGrey(rasterGrey):
    os.system('gdal_translate -of PNG -ot Byte '+rasterGrey+' '+rasterGrey[:-4]+'.png')
    return

if not os.path.exists(outPath):
    os.mkdir(outPath)

if mode=='translate':
  translateLabels(mask)
elif mode=='rasterize':
  p = multiprocessing.Pool(30)
  for f in glob.glob(images+'*.TIF'):
      p.apply_async(labelGrey, [f])
      os.system('ls '+outPath)
  p.close()
  p.join()
  p = multiprocessing.Pool(30)
  for f in glob.glob(images+'*_labels.tif'):
      p.apply_async(translateGrey, [f])
      os.system('ls '+outPath)
  p.close()
  p.join()
