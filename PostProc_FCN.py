import numpy as np
import os, glob, time, re
import scipy as sp
from subprocess import call
import skimage
from skimage import *
from skimage.morphology import erosion, dilation, opening, closing, white_tophat, square, disk
import cv2
from PIL import Image
import rasterio
import numpy.ma as ma
import multiprocessing
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--path', '-p', help="full-path to greyscale prediction chips")
parser.add_argument('--outPath', '-op', help="full-path to resulting, morphed greyscale chips...e.g. ./dilated/ or ./closed/")
parser.add_argument('--upsampleRes', '-ur', help="resolution for cubic spline interpolation, e.g. 2.0")
parser.add_argument('--colorFile', '-cf', help="full-path to rgb color file, e.g. ./color_table.txt")

args = parser.parse_args()
print args

path=args.path
outPath=args.outPath
upsampleRes = args.upsampleRes
colorfile = args.colorFile

start_time = time.time()

def upsample_smooth(image):
  filename_split = os.path.splitext(image)
  filename_zero, fileext = filename_split
  basename = os.path.basename(filename_zero)
  upsampleRes = int(upsampleRes)
  upsampled_image = outPath+basename+'_cubicSpline.png'
  os.system("gdalwarp -tr", upsample_res, upsample_res," -r cubicspline ", image, upsampled_image)
  im = np.array(Image.open(upsampled_image))
  with rasterio.open(image) as r:
    im = r.read()
    p = r.profile
  im = im.squeeze()
  selem = disk(1)
  print("image min and max: ", im.min(),im.max())
  dilated = skimage.morphology.dilation(im, selem)
  print("dilated image min and max: ", dilated.min(),dilated.max())
  eroded = skimage.morphology.erosion(im, selem)
  print("eroded image min and max: ", eroded.min(),eroded.max())
  opened = opening(im, selem)
  print("opened image min and max: ", opened.min(),opened.max())
  closed = closing(im, selem)
  print("closed image min and max: ", closed.min(),closed.max())
  dilated = Image.fromarray(dilated)
  dilated.save(outPath+basename+'.png')
  with rasterio.open(outPath+basename+fileext, 'w', **p) as dst:
      dst.write(dilated, 1)
  color_outPath = outPath+'color/'
  if not os.path.exists(color_outPath):
        os.mkdir(color_outPath) 
  colored_image = color_outPath+basename+'.png'
  os.system("gdaldem color-relief", dilated, colorfile, colored_image)
  return im, dilated, eroded, opened, closed

def smooth(image):
  filename_split = os.path.splitext(image)
  filename_zero, fileext = filename_split
  basename = os.path.basename(filename_zero)
  im = np.array(Image.open(image))
  with rasterio.open(image) as r:
    im = r.read()
    p = r.profile
  im = im.squeeze()
  selem = disk(1)
  print("image min and max: ", im.min(),im.max())
  dilated = skimage.morphology.dilation(im, selem)
  print("dilated image min and max: ", dilated.min(),dilated.max())
  eroded = skimage.morphology.erosion(im, selem)
  print("eroded image min and max: ", eroded.min(),eroded.max())
  opened = opening(im, selem)
  print("opened image min and max: ", opened.min(),opened.max())
  closed = closing(im, selem)
  print("closed image min and max: ", closed.min(),closed.max())
  #im[im==1]=0
  #im[im==2]=1
  median = cv2.medianBlur(im,9)
  average = cv2.blur(im,(9,9))
  #gaussian = cv2.GaussianBlur(im,(9,9),0)
  gaussian = cv2.GaussianBlur(dilated,(9,9),0)
  #bilateral = cv2.bilateralFilter(im,9,75,75)
  bilateral = cv2.bilateralFilter(gaussian,9,75,75)
  with rasterio.open(outPath+basename+fileext, 'w', **p) as dst:
      dst.write(bilateral, 1)
  color_outPath = outPath+'color/'
  if not os.path.exists(color_outPath):
        os.mkdir(color_outPath) 
  colored_image = color_outPath+basename+'.png'
  os.system("gdaldem color-relief", bilateral, colorfile, colored_image)
  return im, dilated, eroded, opened, closed, median, average, gaussian, bilateral
  
p = multiprocessing.Pool()
for f in glob.glob(path+'*.png'):
    p.apply_async(smooth, [f])
p.close()
p.join()

print ("finished post-processing in %(x)s seconds" % {"x" : (time.time() - start_time)})
  
