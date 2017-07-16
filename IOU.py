import numpy as np
#import mahotas
from shapely.geometry import shape
import pandas as pd
import geopandas as gpd
import math
import shapefile as shp
from sklearn.metrics import jaccard_similarity_score
import rasterio
from PIL import Image
import gdal
from gdalconst import * 
from subprocess import call
import os, sys, glob, time


def render(poly):
    """Return polygon as grid of points inside polygon.
    Input : poly (list of lists)
    Output : output (list of lists)
    """
    xs, ys = zip(*poly)
    #minx, miny, maxx, maxy = zip(*poly)
    minx, maxx = min(xs), max(xs)
    miny, maxy = min(ys), max(ys)
    
    print("minx: ", minx, "miny: ", miny, "maxx: ", maxx, "maxy: ", maxy)
    
    for (x, y) in poly:
    	 print("x, y: ", x,y)
    	 print("(int(x - minx), int(y - miny)", (float(x - minx), float(y - miny)))

    newPoly = [(float(x - minx), float(y - miny)) for (x, y) in poly]
    
    print("newPoly: ", newPoly)

    X = maxx - minx + 1
    Y = maxy - miny + 1
    
    print("X: ", X, "Y: ", Y)

    grid = np.zeros((X, Y), dtype=np.int8)
    
    print("grid: ", grid)
    
    mahotas.polygon.fill_polygon(newPoly, grid)
    
    envelope = [(x + minx, y + miny) for (x, y) in zip(*np.nonzero(grid))]
    print("envelope: ", [(x + minx, y + miny) for (x, y) in zip(*np.nonzero(grid))])

    return envelope, [(x + minx, y + miny) for (x, y) in zip(*np.nonzero(grid))]
    
def getXY(pt):
	return (minx,miny,maxx,maxy)
	
poly = gpd.read_file('_.shp')
bboxseries = poly.bounds
bboxDF = pd.DataFrame(bboxseries)
bboxDF.to_csv('_.csv', header=None, index=False)
bboxDF2 = pd.read_csv('_coords.csv')
def bbox(l):
    for index, row in l.iterrows():
    	#minx,miny,maxx,maxy = row[0], row[1], row[2], row[3]
    	#print(minx,miny,maxx,maxy)
    	xs = row[0], row[2]
    	ys = row[1], row[3]
    	polyDict = zip(xs, ys)
    	print(polyDict)
    	return polyDict
polyDict = bbox(bboxDF2)
print(polyDict)
bboxList = bboxDF2.values.tolist()
#bboxList2 = polyDict.values.tolist()
print(bboxList)
#print(bboxList2)
#render(bboxList)
#render(polyDict)

def segments(poly):
        """A sequence of (x,y) numeric coordinates pairs """
        return zip(poly, poly[1:] + [poly[0]])

def area(poly):
    """A sequence of (x,y) numeric coordinates pairs """
    return 0.5 * abs(sum(x0*y1 - x1*y0
        for ((x0, y0), (x1, y1)) in segments(poly)))

def perimeter(poly):
    """A sequence of (x,y) numeric coordinates pairs """
    print("answer: ", abs(sum(math.hypot(x0-x1,y0-y1) for ((x0, y0), (x1, y1)) in segments(poly))))
    return abs(sum(math.hypot(x0-x1,y0-y1) for ((x0, y0), (x1, y1)) in segments(poly)))
    

print("poly.bounds: ", poly.bounds)

#with rasterio.open('_.tif') as r:
#	im = r.read()
#	p = r.profile()
#	print(p)

def getImInfo(filename):
	dataset = gdal.Open(filename, GA_ReadOnly)
	cols = dataset.RasterXSize
	rows = dataset.RasterYSize
	bands = dataset.RasterCount
	gt = dataset.GetGeoTransform()
	projection = dataset.GetProjection()
	gtiff = gdal.GetDriverByName('GTiff')
	ext=[]
	xarr=[0,cols]
	yarr=[0,rows]
	for px in xarr:
	    for py in yarr:
	        x=gt[0]+(px*gt[1])+(py*gt[2])
	        y=gt[3]+(px*gt[4])+(py*gt[5])
	        ext.append([x,y])
	        print x,y
	    yarr.reverse()
	return ext

def getImInfo(filename):
	src = gdal.Open(filename)
	ulx, xres, xskew, uly, yskew, yres  = src.GetGeoTransform()
	lrx = ulx + (src.RasterXSize * xres)
	lry = uly + (src.RasterYSize * yres)
	return ulx, lry, lrx, uly


im_extent = getImInfo('_.tif')

print("image extent: ", im_extent)

im = Image.open('_.tif')

print("im bbox: ", im.getbbox())

print(bboxseries.columns)

minx = min(bboxseries['minx'])
miny = min(bboxseries['miny'])
maxx = max(bboxseries['maxx'])
maxy = max(bboxseries['maxy'])

#print("image extents: ",im_extent[0][0],  im_extent[1][1], im_extent[2][0], im_extent[3][1])

#minx = im_extent[0][0]
#miny = im_extent[1][1]
#maxx = im_extent[2][0]
#maxy = im_extent[3][1]

minx, miny, maxx, maxy = getImInfo('_.tif')

print("minx,maxx,miny,maxy: ", minx,maxx,miny,maxy)


dx = 256
dy = 256

nx = int(math.ceil(abs(maxx - minx)/dx))
ny = int(math.ceil(abs(maxy - miny)/dy))

w = shp.Writer(shp.POLYGON)
w.autoBalance = 1
w.field("ID")

def mapGrid(w,nx,ny,dx,dy):
    id=0
    for i in range(ny):
  	    for j in range(nx):
        	id+=1
            vertices = []
       	    parts = []
            vertices.append([min(minx+dx*j,maxx),max(maxy-dy*i,miny)])
            vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*i,miny)])
            vertices.append([min(minx+dx*(j+1),maxx),max(maxy-dy*(i+1),miny)])
            vertices.append([min(minx+dx*j,maxx),max(maxy-dy*(i+1),miny)])
            parts.append(vertices)
            w.poly(parts)
            w.record(id)
            print(w)
    w.save('./shape/')

mapGrid(w,nx,ny,dx,dy)


perimeter(polyDict)

tiles = [glob.glob('./*.png')]

print(len(tiles))

#os.system("find ./ -name *.png -exec gdaltindex ./_.shp {} \;") 

def compareGT2Pred(gt, pred):
    filename_split = os.path.splitext(pred)
    filename_zero, fileext = filename_split
    basename = os.path.basename(filename_zero)
    gt_im = Image.open(gt)
    pred_im = Image.open(pred)
    gt_arr = np.array(gt_im)
    pred_arr = np.array(pred_im)
    gt_arr_1d = gt_arr.flatten()
    pred_arr_1d = pred_arr.flatten()
    compare_arr = (gt_arr_1d==pred_arr_1d)
    difference_arr = (gt_arr_1d-pred_arr_1d)
    difference_arr[difference_arr==255]=1
    #union_arr = np.where(difference_arr == 0)
    union_arr = np.union1d(gt_arr_1d, pred_arr_1d)
    intersection_arr = np.intersect1d(gt_arr_1d, pred_arr_1d)
    iou = np.true_divide(union_arr,intersection_arr)
    jaccard = jaccard_similarity_score(gt_arr_1d, pred_arr_1d)
    print("union array: ", union_arr)
    print("intersection array: ", intersection_arr)
    print("length of difference array: ", len(difference_arr))
    print("length of union array: ", len(union_arr))
    print("IoU: ", str(iou))
    print("jaccard: ", jaccard)
    print("length of comparison array: ", len(compare_arr))
    print(gt_arr_1d==pred_arr_1d)	
    print(np.in1d(gt_arr_1d, pred_arr_1d))
    diff_mat = np.reshape(difference_arr, (256, 256))
    diff_mat[diff_mat==255]=1
    diff_im = Image.fromarray(diff_mat.astype(np.uint8))
    print("shape of difference image: ", np.shape(diff_im))
    print("unique values of difference image: ", np.unique(diff_im))
    outpath = './out/'
    diff_fn = outpath+basename+'_diff'
    diff_im.save(diff_fn+'.png')
    os.system("ls "+diff_fn+"*")
    os.system("gdal_polygonize.py "+diff_fn+".png"+" -mask "+diff_fn+".png"+" -f 'ESRI Shapefile' "+diff_fn+".shp "+basename+"_diff")	#+diff_fn)	#+basename+"_diff")
    return (gt_arr_1d==pred_arr_1d), (gt_arr_1d-pred_arr_1d), (np.in1d(gt_arr_1d, pred_arr_1d))
	
compare_arr, difference_arr, elementwise_concurrency = compareGT2Pred('_.png', '_pred.png')

print("length of compare array: ", len(compare_arr))	
print("shape of compare array: ", np.shape(compare_arr))	

print("length of difference array: ", len(difference_arr))	
print("shape of difference array: ", np.shape(difference_arr))	
print("min and max of difference array: ", min(difference_arr), max(difference_arr))
print("unique values of difference array: ", np.unique(difference_arr))


falsePixel_op = np.where(compare_arr == False)

#for row in compare_matrix:
#	print("searching row-wise: ", len(row))
	#print("searching row-wise: ", len(np.where(row == False)))

#print("number of non-matching pixels: ", len(np.apply_along_axis(falsePixel_op, axis=1, arr=compare_matrix)))
#print("number of non-matching pixels with np.any(axis=1): ", len(np.where(np.any(compare_matrix == False, axis=1))))
#print("number of non-matching pixels with np.any(axis=0): ", len(np.where(np.any(compare_matrix == False, axis=0))))


print("number of non-matching pixels in difference array: ", len(np.where(difference_arr != 0)[0]))	
print("number of matching pixels in difference array: ", len(np.where(difference_arr == 0)[0]))	

print("non-matching pixels in difference array: ", np.where(difference_arr != 0)[0])	
print("matching pixels in difference array: ", np.where(difference_arr == 0)[0])

print("non-matching pixel indexed locations in difference array: ", np.where(difference_arr != 0)[0])

print("number of non-matching pixels: ", len(np.where(compare_arr == False)[0]))	
print("number of matching pixels: ", len(np.where(compare_arr == True)[0]))	

print("non-matching pixels: ", np.where(compare_arr == False)[0])	
print("matching pixels: ", np.where(compare_arr == True)[0])

print("non-matching pixel indexed locations: ", np.where(compare_arr == False)[0])

print("shape of comparison array: ", np.shape(compare_arr))	
print("where the pixels are one-for-one: ", elementwise_concurrency)
