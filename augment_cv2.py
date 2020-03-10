import cv2
import numpy as np
#import imgaug as ia
#import imgaug.augmenters as iaa
import os,glob

images = glob.glob("fused_labels/*.png")



angle90 = 90
angle180 = 180
angle270 = 270

scale = 1.0


for i, im in enumerate(images):
    imr = cv2.imread(im)
    #imr = cv2.cvtColor(imr, cv2.COLOR_BGR2RGB) #  IF RGB NOT LABELS
    img = imr.copy()
    (h, w) = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle90, scale)
    rotated90 = cv2.warpAffine(img, M, (h, w))
    #rotated90 = cv2.cvtColor(rotated90, cv2.COLOR_BGR2RGB)
    cv2.imwrite(im[:-4]+'_rotate90.png', rotated90)
    img = imr.copy()
    (h, w) = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle180, scale)
    rotated180 = cv2.warpAffine(img, M, (h, w))
    #rotated180 = cv2.cvtColor(rotated180, cv2.COLOR_BGR2RGB)
    cv2.imwrite(im[:-4]+'_rotate180.png', rotated180)
    img = imr.copy()
    (h, w) = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle270, scale)
    rotated270 = cv2.warpAffine(img, M, (h, w))
    #rotated270 = cv2.cvtColor(rotated270, cv2.COLOR_BGR2RGB)
    cv2.imwrite(im[:-4]+'_rotate270.png', rotated270)
    img = imr.copy()
    horizontal_img = cv2.flip( img, 0 )
    vertical_img = cv2.flip( img, 1 )
    #horizontal_img = cv2.cvtColor(horizontal_img, cv2.COLOR_BGR2RGB)
    #vertical_img = cv2.cvtColor(vertical_img, cv2.COLOR_BGR2RGB)
    cv2.imwrite(im[:-4]+'_horizontal_flip.png', horizontal_img)
    cv2.imwrite(im[:-4]+'_vertical_flip.png', vertical_img)
