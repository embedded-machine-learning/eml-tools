#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Convert PASCAL VOC to TFRecord. Sample TensorFlow XML-to-TFRecord converter

usage: generate_tfrecord.py [-h] [-x XML_DIR] [-l LABELS_PATH] [-o OUTPUT_PATH] [-i IMAGE_DIR] [-c CSV_PATH]

optional arguments:
  -h, --help            show this help message and exit
  -x XML_DIR, --xml_dir XML_DIR
                        Path to the folder where the input .xml files are stored.
  -l LABELS_PATH, --labels_path LABELS_PATH
                        Path to the labels (.pbtxt) file.
  -o OUTPUT_PATH, --output_path OUTPUT_PATH
                        Path of output TFRecord (.record) file.
  -i IMAGE_DIR, --image_dir IMAGE_DIR
                        Path to the folder where the input image files are stored. Defaults to the same directory as XML_DIR.
  -c CSV_PATH, --csv_path CSV_PATH
                        Path of output .csv file. If none provided, then no file will be written.

License_info:
# ==============================================================================
# ISC License (ISC)
# Copyright 2020 Christian Doppler Laboratory for Embedded Machine Learning
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE
# OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
# PERFORMANCE OF THIS SOFTWARE.
# ==============================================================================

# The following script uses several method fragments the following script from Tensorflow
# Source: https://github.com/tensorflow/models/tree/master/research/object_detection/dataset_tools and 
# https://github.com/EricThomson/tfrecord-view/blob/master/voc_to_tfr.py

"""

# Futures
from __future__ import print_function

# Built-in/Generic Imports
import os
import glob
import sys

# Libs
import pandas as pd
import io
import logging
import xml.etree.ElementTree as ET
import argparse
import re
import numpy as np
from lxml import etree
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress TensorFlow logging (1)
import tensorflow.compat.v1 as tf
from PIL import Image
from collections import namedtuple
import contextlib2

# Own modules
# Tensorflow object detection API has to be installed
from object_detection.utils import dataset_util, label_map_util
from object_detection.dataset_tools import tf_record_creation_util

__author__ = 'Alexander Wendt'
__copyright__ = 'Copyright 2020, Christian Doppler Laboratory for ' \
                'Embedded Machine Learning'
__credits__ = ['Tensorflow Object Detection API']
__license__ = 'ISC'
__version__ = '0.2.0'
__maintainer__ = 'Alexander Wendt'
__email__ = 'alexander.wendt@tuwien.ac.at'
__status__ = 'Experiental'


# Initiate argument parser
parser = argparse.ArgumentParser(description="Sample TensorFlow XML-to-TFRecord converter")
parser.add_argument("-x",
                    "--xml_dir",
                    help="Path to the folder where the input .xml files are stored.",
                    type=str)
parser.add_argument("-l",
                    "--labels_path",
                    help="Path to the labels (.pbtxt) file.", type=str)
parser.add_argument("-o",
                    "--output_path",
                    help="Path of output TFRecord (.record) file.", type=str)
parser.add_argument("-i",
                    "--image_dir",
                    help="Path to the folder where the input image files are stored. "
                         "Defaults to the same directory as XML_DIR.",
                    type=str, default=None)
parser.add_argument("-ie",
                    "--ignore_empty_instances",
                    help="Ignore empty instances.",
                    action='store_true', default=False)
parser.add_argument("-n",
                    "--number_shards",
                    help="Number of shards.",
                    type=int, default=10)

args = parser.parse_args()


# def xml_to_csv(path, filter=None):
#     """Iterates through all .xml files (generated by labelImg) in a given directory and combines
#     them in a single Pandas dataframe.
#
#     Parameters:
#     ----------
#     path : str
#         The path containing the .xml files
#     filter: list of image file names. Default None. If no filter is given, all xml files are used
#
#     Returns
#     -------
#     Pandas DataFrame
#         The produced dataframe
#     """
#     xml_file_list=[]
#
#     if filter is not None:
#         print("Filter available. Using only xml files with corresponding image files")
#         #xml_filename = os.path.join(xml_source, os.path.splitext(filename)[0] + '.xml')
#         xml_file_list = [os.path.join(path, os.path.splitext(image_name)[0] + '.xml') for image_name in filter]
#     else:
#         print("Filter not used. Select all xml files of the folder")
#         xml_file_list = glob.glob(path + '/*.xml')
#
#     xml_list = []
#     for xml_file in xml_file_list: #glob.glob(path + '/*.xml'):
#         tree = ET.parse(xml_file)
#         root = tree.getroot()
#         if len(root.findall('object')) == 0:  #Negative example, empty image
#             value = (root.find('filename').text,
#                      int(root.find('size')[0].text),
#                      int(root.find('size')[1].text),
#                      None,
#                      None,
#                      None,
#                      None,
#                      None
#                      )
#             xml_list.append(value)
#
#         for member in root.findall('object'):
#             value = (root.find('filename').text,
#                      int(root.find('size')[0].text),
#                      int(root.find('size')[1].text),
#                      member.find("name").text,
#                      int(member.find("bndbox")[0].text),
#                      int(member.find("bndbox")[1].text),
#                      int(member.find("bndbox")[2].text),
#                      int(member.find("bndbox")[3].text)
#                      )
#             xml_list.append(value)
#     column_name = ['filename', 'width', 'height',
#                    'class', 'xmin', 'ymin', 'xmax', 'ymax']
#     xml_df = pd.DataFrame(xml_list, columns=column_name)
#     return xml_df

#Following is from models/research/object_detection/dataset_util.py
def recursive_parse_xml_to_dict(xml):
  """Recursively parses XML contents to python dict.
  We assume that `object` tags are the only ones that can appear
  multiple times at the same level of a tree.
  Args:
    xml: xml tree obtained by parsing XML file contents using lxml.etree
  Returns:
    Python dictionary holding XML contents.
  """
  if not xml:
    return {xml.tag: xml.text}
  result = {}
  for child in xml:
    child_result = recursive_parse_xml_to_dict(child)
    if child.tag != 'object':
      result[child.tag] = child_result[child.tag]
    else:
      if child.tag not in result:
        result[child.tag] = []
      result[child.tag].append(child_result[child.tag])
  return {xml.tag: result}

# def xml_to_csv(path, filter=None):
#     """Iterates through all .xml files (generated by labelImg) in a given directory and combines
#     them in a single Pandas dataframe.
#
#     Parameters:
#     ----------
#     path : str
#         The path containing the .xml files
#     filter: list of image file names. Default None. If no filter is given, all xml files are used
#
#     Returns
#     -------
#     Pandas DataFrame
#         The produced dataframe
#     """
#     xml_file_list=[]
#
#     if filter is not None:
#         print("Filter available. Using only xml files with corresponding image files")
#         #xml_filename = os.path.join(xml_source, os.path.splitext(filename)[0] + '.xml')
#         xml_file_list = [os.path.join(path, os.path.splitext(image_name)[0] + '.xml') for image_name in filter]
#     else:
#         print("Filter not used. Select all xml files of the folder")
#         xml_file_list = glob.glob(path + '/*.xml')
#
#     xml_list = []
#     for xml_file in xml_file_list: #glob.glob(path + '/*.xml'):
#         tree = ET.parse(xml_file)
#         root = tree.getroot()
#         for member in root.findall('object'):
#             value = (root.find('filename').text,
#                      int(root.find('size')[0].text),
#                      int(root.find('size')[1].text),
#                      member.find("name").text,
#                      int(member.find("bndbox")[0].text),
#                      int(member.find("bndbox")[1].text),
#                      int(member.find("bndbox")[2].text),
#                      int(member.find("bndbox")[3].text)
#                      )
#             xml_list.append(value)
#     column_name = ['filename', 'width', 'height',
#                    'class', 'xmin', 'ymin', 'xmax', 'ymax']
#     xml_df = pd.DataFrame(xml_list, columns=column_name)
#     return xml_df


def class_text_to_int(row_label, label_map_dict):
    return label_map_dict[row_label]


def split(df, group):
    data = namedtuple('data', ['filename', 'object'])
    gb = df.groupby(group)
    return [data(filename, gb.get_group(x)) for filename, x in zip(gb.groups.keys(), gb.groups)]


def create_tf_example(data, image_path, label_map_dict, ignore_empty_instances=False, verbose=1):
    """
    Convert image/xml-derived annotation dict to tensorflow example file to be
    incorporated into a TFRecord. Adapted from:
            https://github.com/tensorflow/models/blob/master/research/object_detection/dataset_tools/create_pascal_tf_record.py
    Notice that this function normalizes the bounding box coordinates provided
    by the raw data, so they are between [0, 1].
    Inputs:
        data: dict holding PASCAL XML fields for a single image (obtained by
            running recursive_parse_xml_to_dict)
        image_path: Path to image
        label_map_dict: A map from string label names to integers ids.
        ignore_difficult_instances: Whether to skip difficult instances in the
            dataset    (default: False).
        verbose (default 1): 1 to show image info during encoding, 0 otherwise
    Returns:
        example: The converted tf.Example.
    """
    with tf.gfile.GFile(image_path, 'rb') as fid:
        encoded_image = fid.read()

    if verbose: print(f"Encoding {image_path}")
    # For some reason after processing xml, it frequently returns width/height switched!
    width = int(data['size']['width'])
    height = int(data['size']['height'])

    # If no data['object'] there are no bounding boxes
    if 'object' in data:
        annotation_list = data['object']
        xmin = []
        ymin = []
        xmax = []
        ymax = []
        classes = []
        classes_text = []
        difficult_obj = []

        for annotation in annotation_list:
            #if not annotation.get('difficult') == None:
            #    difficult = bool(int(annotation['difficult']))
            #else:
            #    difficult = False
            #if ignore_difficult_instances and difficult:
            #    continue

            #difficult_obj.append(int(difficult))

            x1 = annotation['bndbox']['xmin']
            y1 = annotation['bndbox']['ymin']
            x2 = annotation['bndbox']['xmax']
            y2 = annotation['bndbox']['ymax']
            xmin.append(float(x1) / width)
            xmax.append(float(x2) / width)
            ymin.append(float(y1) / height)
            ymax.append(float(y2) / height)
            classes_text.append(annotation['name'].encode('utf8'))
            classes.append(label_map_dict[annotation['name']])

        obj_features = {
            'image/height': int64_feature(height),
            'image/width': int64_feature(width),
            'image/filename': bytes_feature(data['filename'].encode('utf8')),
            'image/encoded': bytes_feature(encoded_image),
            'image/object/bbox/xmin': float_list_feature(xmin),
            'image/object/bbox/xmax': float_list_feature(xmax),
            'image/object/bbox/ymin': float_list_feature(ymin),
            'image/object/bbox/ymax': float_list_feature(ymax),
            'image/object/class/text': bytes_list_feature(classes_text),
            'image/object/class/label': int64_list_feature(classes),
            'image/annotated': int64_feature(0)
        }

        tf_features = tf.train.Features(feature=obj_features)
        tf_example = tf.train.Example(features=tf_features)
        #if verbose: print("Image with annotations: ", image_path)

    elif not ignore_empty_instances:
        if verbose: print("No annotations available, empty image")
        obj_features = {
            'image/height': int64_feature(height),
            'image/width': int64_feature(width),
            'image/filename': bytes_feature(data['filename'].encode('utf8')),
            'image/encoded': bytes_feature(encoded_image),
            'image/annotated': int64_feature(0)
        }

        tf_features = tf.train.Features(feature=obj_features)
        tf_example = tf.train.Example(features=tf_features)
    else:
        print("Empty image. Ignoring")
        tf_example = None

    return tf_example

#Following feature encoders are from models/research/object_detection/dataset_util.py
def int64_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def int64_list_feature(value):
  return tf.train.Feature(int64_list=tf.train.Int64List(value=value))


def bytes_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))


def bytes_list_feature(value):
  return tf.train.Feature(bytes_list=tf.train.BytesList(value=value))


def float_list_feature(value):
  return tf.train.Feature(float_list=tf.train.FloatList(value=value))

# def create_tf_example(group, path):
#     with tf.gfile.GFile(os.path.join(path, '{}'.format(group.filename)), 'rb') as fid:
#         encoded_jpg = fid.read()
#     encoded_jpg_io = io.BytesIO(encoded_jpg)
#     image = Image.open(encoded_jpg_io)
#     width, height = image.size
#
#     filename = group.filename.encode('utf8')
#     print("Process file: ", filename)
#     image_format = b'jpg'
#     xmins = []
#     xmaxs = []
#     ymins = []
#     ymaxs = []
#     classes_text = []
#     classes = []
#
#     # If no data['object'] there are no bounding boxes
#     if 'object' in group:
#         for index, row in group.object.iterrows():
#             xmins.append(row['xmin'] / width)
#             xmaxs.append(row['xmax'] / width)
#             ymins.append(row['ymin'] / height)
#             ymaxs.append(row['ymax'] / height)
#             classes_text.append(row['class'].encode('utf8'))
#             classes.append(class_text_to_int(row['class']))
#
#         tf_example = tf.train.Example(features=tf.train.Features(feature={
#             'image/height': dataset_util.int64_feature(height),
#             'image/width': dataset_util.int64_feature(width),
#             'image/filename': dataset_util.bytes_feature(filename),
#             'image/source_id': dataset_util.bytes_feature(filename),
#             'image/encoded': dataset_util.bytes_feature(encoded_jpg),
#             'image/format': dataset_util.bytes_feature(image_format),
#             'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
#             'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
#             'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
#             'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
#             'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
#             'image/object/class/label': dataset_util.int64_list_feature(classes),
#         }))
#     else:
#         print("WARNNG")
#     return tf_example

def write_tf_records_alt(class_labels, image_dir, xml_dir, output_path, num_shards, ignore_empty_instances):
    # Repo
    #class_labels = {"dog": 1, "cat": 2}
    #images_path #data_path = r"annotated_images/"
    #output_path = data_path + r'cats_dogs.record'

    verbose = 1
    path = os.path.join(image_dir)
    images = [f for f in os.listdir(path) if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(.jpg|.jpeg|.png)$', f)]

    #filename_query = os.path.join(images_path, '*.png')  # can change to any format (bmp, png etc)
    #image_paths = np.sort(glob.glob(filename_query))

    #writer = tf.python_io.TFRecordWriter(output_path)

    xml_preparation_list = []
    for idx, image_name in enumerate(images):
        image_path = os.path.join(image_dir, image_name)
        xml_path = os.path.join(xml_dir, image_name.split('.')[-2] + '.xml')

        xml_data = xml_to_dict(xml_path)

        tfrecord_preparation = (image_path, xml_data)
        xml_preparation_list.append(tfrecord_preparation)
        #tf_example = create_tf_example(xml_data, image_path, class_labels, verbose=verbose)

        #writer.write(tf_example.SerializeToString())

    #writer.close()

    write_tf_records_only(output_path, num_shards, xml_preparation_list, class_labels, ignore_empty_instances, verbose=verbose)


    print("Done encoding data TFRecord file")


def xml_to_dict(xml_path):
    with tf.gfile.GFile(xml_path, 'rb') as fid:
        xml_str = fid.read()
    xml = etree.fromstring(xml_str)
    xml_data = recursive_parse_xml_to_dict(xml)['annotation']
    return xml_data


def write_tf_records_only(output_filename, num_shards, xml_preparation_list, class_labels, ignore_empty_instances, verbose=1):
    with contextlib2.ExitStack() as tf_record_close_stack:
        output_tfrecords = tf_record_creation_util.open_sharded_output_tfrecords(
            tf_record_close_stack, output_filename, num_shards)
        for idx, xml_preparation in enumerate(xml_preparation_list):
            image_path, xml_data = xml_preparation
            if idx % 100 == 0:
                logging.info('On image %d of %d', idx, len(xml_preparation_list))
            try:
                #Create the example
                #tf_example = create_tf_example(grouped_example, image_dir)
                tf_example = create_tf_example(xml_data, image_path, class_labels, ignore_empty_instances, verbose=verbose)



                if tf_example:
                    shard_idx = idx % num_shards
                    output_tfrecords[shard_idx].write(tf_example.SerializeToString())
                else:
                    print("Empty example. Nothing to add.")
            except ValueError:
                logging.warning('Invalid example: %s, ignoring.', image_path.filename)

    print('Successfully created the TFRecord file: {}'.format(args.output_path))
    #if csv_path is not None:
    #    examples.to_csv(args.csv_path, index=None)
    #    print('Successfully created the CSV file: {}'.format(args.csv_path))

# def write_tf_records(output_filename, num_shards, image_dir, xml_dir, csv_path=None):
#     '''
#
#     :param output_filename: Path to where output file is saved.
#     :param num_shards: Number of shards for output file.
#     :param tf_examples: List of examples to write to the file
#
#     :return: Nothing
#     '''
#
#     path = os.path.join(image_dir)
#     images = [f for f in os.listdir(path)
#               if re.search(r'([a-zA-Z0-9\s_\\.\-\(\):])+(.jpg|.jpeg|.png)$', f)]
#
#     examples = xml_to_csv(xml_dir, images)
#     grouped_examples = split(examples, 'filename')
#
#     output_dir = os.path.split(output_filename)[0]
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)
#
#     with contextlib2.ExitStack() as tf_record_close_stack:
#         output_tfrecords = tf_record_creation_util.open_sharded_output_tfrecords(
#             tf_record_close_stack, output_filename, num_shards)
#         for idx, grouped_example in enumerate(grouped_examples):
#             if idx % 100 == 0:
#                 logging.info('On image %d of %d', idx, len(grouped_examples))
#             try:
#                 #Create the example
#                 tf_example = create_tf_example(grouped_example, path)
#                 if tf_example:
#                     shard_idx = idx % num_shards
#                     output_tfrecords[shard_idx].write(tf_example.SerializeToString())
#             except ValueError:
#                 logging.warning('Invalid example: %s, ignoring.', grouped_example.filename)
#
#     print('Successfully created the TFRecord file: {}'.format(args.output_path))
#     if csv_path is not None:
#         examples.to_csv(args.csv_path, index=None)
#         print('Successfully created the CSV file: {}'.format(args.csv_path))

def write_single_tf_record_file(grouped, path):
    '''
    Write grouped

    :param grouped:
    :param path:
    :return:
    '''
    writer = tf.python_io.TFRecordWriter(args.output_path)
    for group in grouped:
        tf_example = create_tf_example(group, path)
        writer.write(tf_example.SerializeToString())
    writer.close()


def main(_):
    #path = os.path.join(args.image_dir)
    #examples = xml_to_csv(args.xml_dir)
    #grouped = split(examples, 'filename')

    #tf_example_group = []
    #for group in grouped:
    #    tf_example = create_tf_example(group, path)
    #    tf_example_group.append(tf_example)

    if args.image_dir is None:
        args.image_dir = args.xml_dir

    label_map = label_map_util.load_labelmap(args.labels_path)
    label_map_dict = label_map_util.get_label_map_dict(label_map)

    write_tf_records_alt(label_map_dict, args.image_dir, args.xml_dir, args.output_path, args.number_shards,
                         args.ignore_empty_instances)

    #write_tf_records(args.output_path, args.number_shards, args.image_dir, args.xml_dir)
    print("Program End")
    sys.exit(0) #Exit code, else program throws error

if __name__ == '__main__':
    tf.app.run()

