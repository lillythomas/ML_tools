import re,glob,time,os,sys,collections,csv
from collections import Counter
from subprocess import call
import multiprocessing
from PIL import Image
import numpy as np
import numpy.ma as ma
import pandas as pd
import argparse


parser = argparse.ArgumentParser()

parser.add_argument('--labels') # i.e. ./labels/
parser.add_argument('--outDir') # i.e. ./out/
parser.add_argument('--outName') # i.e. info


args = parser.parse_args()
print args

lbls = args.labels
od = args.outDir
on = args.outName

os.system('mkdir '+od+'tmp/')


def TMS(rootdir):
    list=[]
    for subdir, dirs, files in os.walk(rootdir):
        filename_split = os.path.splitext(subdir)
        filename_zero, fileext = filename_split
        basename = os.path.basename(filename_zero)
        for file in files:
            listt= os.path.join(subdir, file)
            list.append(listt)
    return list


def labelInfo(lbl):
    filename_split = os.path.splitext(lbl)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    labelArray= np.array(Image.open(lbl))
    print("unique values in %(x)s are: %(y)s" % {"x" : (basename), "y" : (np.unique(labelArray))})
    pixelCount = len(labelArray)*len(labelArray)
    print("pixel count in this image: %s" % pixelCount)
    #df_ = pd.DataFrame(index=list(range(pixelCount)), columns=np.unique(labelArray))
    #df_ = df_.fillna(0) # with 0s rather than NaNs
    #print(df_.columns, len(df_))
    cnt = Counter()
    labelList = labelArray.tolist()
    def flatten(seq,container=None):
        if container is None:
            container = []
        for s in seq:
            if hasattr(s,'__iter__'):
                flatten(s,container)
            else:
                container.append(s)
        return container
    labelList = flatten(labelList)
    for p in labelList:
        cnt[p] += 1
    print(cnt)
    df = pd.DataFrame.from_dict(cnt, orient='index').reset_index()
    df['Value'] = df['index']
    df['Count'] = df[0]
    df['Percent'] = df[0]/pixelCount
    df = df.drop(df.columns[[0,1]], 1)
    df['image_name'] = lbl
    df = df[['image_name', 'Value', 'Count', 'Percent']]
    #print(df, df.columns)
    df.to_csv(od+'tmp/label_'+basename+'.csv', index = False, encoding='utf-8')
    return

if args.labels:
    p = multiprocessing.Pool(30)
    for f in glob.glob(lbls+"*.png"):
        p.apply_async(labelInfo, [f])
    p.close()
    p.join()
else:
    print('invalid or insufficient options')

print("processed images to csvs")

files = glob.glob(od+'tmp/*.csv')
df = pd.concat([pd.read_csv(f, index_col=False) for f in files], join = 'outer')
df.to_csv(od+on+"_labels_info.csv")
print(df.columns)

print("concatenated csvs to one")
df_pivot = df.pivot("image_name", "Value", "Percent")
print(df_pivot.columns)
df_pivot.to_csv(od+on+"_labels_info_pivot.csv")

print("pivoted csv by values")

#print("no-data mean percent: %s" %(df_pivot[0].mean()))
#print("no-data median percent: %s" %(df_pivot[0].median()))
#print("no-data max percent: %s" %(df_pivot[0].max()))
#print("no-data min percent: %s" %(df_pivot[0].min()))
