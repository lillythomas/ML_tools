import os, glob, time, re, argparse, tempfile
import multiprocessing
import numpy as np
from PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('--images', '-i', help="full-path to 3 channel image(s)")
parser.add_argument('--annotations', '-a', help="full-path to 1 channel annotation image(s)")
parser.add_argument('--pairs', '-p', help="full-path to paired image(s) and annotation(s)")
parser.add_argument('--which', '-w', help="which dataset to arrange, valid answers: images, annotations, or combined")
parser.add_argument('--combine', '-c', help="combine lists, valid answers: True or False")
parser.add_argument('--pairPath', '-pp', help="full-path to combined list, e.g. comboList.txt")


args = parser.parse_args()
print args

images=args.images
annotations=args.annotations
pairPath=args.pairPath
pairs=args.pairs
combine=args.combine
which=args.which

def arrangeImages():
    os.system("ls "+images+"*.png"+" > "+images+"imageList.txt")
    os.system("cd "+images)
    print(os.system("pwd"))
    return
    
def arrangeAnnotations():
    os.system("ls "+annotations+"*.png"+" > "+annotations+"annotationList.txt")
    os.system("cd "+annotations)
    print(os.system("pwd"))
    return    

def concat():
    #os.system("paste "+images+"imageList.txt "+annotations+"annotationList.txt | column -s $'\t' -t > "+pairPath)
    os.system("paste "+images+"imageList.txt "+annotations+"annotationList.txt | column -s $' ' -t > "+pairPath)
    return

def arrangeTF():  
    image_files = glob.glob(pairs+"*_image.png")
    with open(pairs+"imageList.txt", 'rb') as fi:
        img_lst = list(fi.readlines())
    anno_files = glob.glob(pairs+"*_anno.png")
    with open(pairs+"annotationList.txt", 'rb') as fa:
        anno_lst = list(fa.readlines())
    with open(pairPath[:-4]+'_tfTrain.txt', 'w+') as f:
        for eli, ela in zip(img_lst, anno_lst):
            eli = eli.decode('utf-8')[:-5]
            ela = ela.decode('utf-8')[:-5]
            f.write('{}.png {}.png\n'.format(eli, ela))
    return

if which=='images':
   arrangeImages()
   print('arranged images')
elif which=='annotations':
   arrangeAnnotations()
   print('arranged annotations')
elif which=='combined':
   arrangeTF()
   print('arranged combined pairs')
elif combine=='True':
   concat()
   print('combined lists')
else:
   print("wrong options, please choose either images or annotations, or combine")

