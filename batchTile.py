import os, sys, glob, time, argparse, multiprocessing
from PIL import Image
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--images', '-i', help="full-path to 3 channel image(s)")
parser.add_argument('--annotations', '-a', help="full-path to 1 channel annotation image(s)")
parser.add_argument('--which', '-w', help="which dataset to tile, valid answers: images or annotations")
parser.add_argument('--outPath', '-c', help="full-path to output tiles")

args = parser.parse_args()
print args

images=args.images
annotations=args.annotations
which=args.which
outPath=args.outPath

def translateRGB(rasterRGB):
    os.system('gdal_translate -of PNG -b 1 -b 2 -b 3 '+rasterRGB+' '+rasterRGB[:-4]+'.png')
    
def translateGrey(rasterGrey):
    os.system('gdal_translate -of PNG '+rasterGrey+' '+rasterGrey[:-4]+'.png')

def tile256rgb(rasterRGB,x,y,outPath):
    os.system('./tileRGB.sh '+rasterRGB+' 256 '+str(x)+' '+str(y)+' '+outPath +' 10')
    
def tile256(rasterGrey,x,y,outPath):
    os.system('./tile.sh '+rasterGrey+' 256 '+str(x)+' '+str(y)+' '+outPath +' 10')

if not os.path.exists(outPath):
    os.mkdir(outPath)
        
def tileRGB(f):
    filename_split = os.path.splitext(f)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    #if not os.path.exists(outPath+'images/'):
    #    os.mkdir(outPath+'images/')
    out=outPath+'images/'+basename   #make a directory to write to
    im=np.array(Image.open(f))
    size=im.shape
    print(size)
    y=size[0]
    x=size[1]
    tile256rgb(f,x,y,out)
    return

def tileGrey(f):
    filename_split = os.path.splitext(f)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    if not os.path.exists(outPath+'annotations/'):
        os.mkdir(outPath+'annotations/')
    out=outPath+'annotations/'+basename[:-4]   #make a directory to write to
    im=np.array(Image.open(f))
    im[im==255]=0
    size=im.shape
    y=size[0]
    x=size[1]
    tile256(f,x,y,out)
    return

"""p = multiprocessing.Pool()
for f in glob.glob(images+'*.tif'):
    p.apply_async(translateRGB, [f])
    os.system('ls '+images)
p.close()
p.join()

p = multiprocessing.Pool()
for f in glob.glob(images+'*.png'):
    p.apply_async(tileRGB, [f])
    print('tiled image')
p.close()
p.join()"""

p = multiprocessing.Pool(30)

if which=='images':
  p = multiprocessing.Pool(30)
  for f in glob.glob(images+'*.tif'):
      p.apply_async(translateRGB, [f])
      os.system('ls '+images) 
  p.close()
  p.join()
  p = multiprocessing.Pool(30)
  for f in glob.glob(images+'*.png'):
      p.apply_async(tileRGB, [f])
  p.close()
  p.join()
  print('tiled images')
elif which=='annotations':
  p = multiprocessing.Pool(30)
  for f in glob.glob(annotations+'*.tif'):
      p.apply_async(translateGrey, [f])
      os.system('ls '+annotations) 
  p.close()
  p.join()
  p = multiprocessing.Pool(30)
  for f in glob.glob(annotations+'*.png'):
      p.apply_async(tileGrey, [f])
  p.close()
  p.join()
  print('tiled annotations')
else:
   print("wrong options, please choose either images or annotations")

"""
if which=='images':
  for f in glob.glob(images+'*.tif'):
      p.apply_async(tileRGB, [f])
  print('tiled images')
elif which=='annotations':
  for f in glob.glob(annotations+'*.tif'):
      p.apply_async(tileGrey, [f])
  print('tiled annotations')
else:
   print("wrong options, please choose either images or annotations")
p.close()
p.join()
"""
#for f in *; do mv "$f" "${f//_060717_d1g99b97575_062917cr_c_/}"; done

#nohup python FCN.py --gpu 0 --data_dir /mnt/cirrus/data/impervious/HCpilot2/tree_shadow_train/tiled/ --mode=train > HCpilot2_tree_shadow_train.out&
