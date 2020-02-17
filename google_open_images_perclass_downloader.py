import csv
import boto3
from botocore import UNSIGNED
from botocore.config import Config

BUCKET_NAME = 'open-images-dataset'
s3 = boto3.resource('s3', config=Config(signature_version=UNSIGNED))
CLASS_LIST = ['/m/01prls']

with open('train-annotations-bbox.csv', "r") as csvfile:
    bboxs = csv.reader(csvfile, delimiter=',', quotechar='|')
    for bbox in bboxs:
        if bbox[2] in CLASS_LIST:
            key = 'train/'+bbox[0] + '.jpg'
            destination = PATH + bbox[0] + '.jpg'
            s3.Bucket(BUCKET_NAME).download_file(key, destination)
