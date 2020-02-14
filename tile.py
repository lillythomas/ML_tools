import os, sys, glob


def tileImage(f):
    filename_split = os.path.splitext(f)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    os.system('convert '+basename+'.jpg -crop 512x512 tiles/'+basename+'%03d.jpg')

for f in glob.glob('./*.jpg'):
    tileImage(f)
