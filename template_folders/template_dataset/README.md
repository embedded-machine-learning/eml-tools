# Template Folder Structure for Datasets for Training
Template folder structure for datasets that include Yolo formats, Coco and Pascal VOC formats. This folder structure is
used for training only. For validation, a reduced subset of this template is used.

## How to use it
1. Copy the whole folder structure to your project location.
2. Execute ```python remove_gitignore.py``` to remove all .gitignores in the sub folders
3. Move or copy your images and annotations to the appropriate folder
4. Copy the scripts to the root (.bat or .sh) and not the .py files.
5. Adapt the script .sh and .bat to use the python files directly from the main EML tool repository.
6. On all data, execute scripts for conversion to Pascal VOC, Coco and Yolo to have all annotations in the folders.

## Structure
The following structure is used:
- ./annotations/xmls: Pascal VOC,  training, validation labels in ./annotations/xmls/train and ./annotations/xmls/val and a small debug set for testing the algorithms in ./annotations/xmls/debug
- ./annotations: Coco labels 
- ./labels: Yolo, Training labels in ./labels/train and validation labels in ./labels/val
- ./images: Images, Training images in ./images/train, validation images in ./images/val
- ./prepared-records: Tensorflow prepared records. The records shall be named train.record and val.record as a default.
- ./scripts: Scripts Put finished scripts here

## Issues
If there are any issues or suggestions for improvements, please add an issue to github's bug tracking system or please send a mail 
to [Alexander Wendt](mailto:alexander.wendt@tuwien.ac.at)

<div align="center">
  <img src="../../_img/eml_logo_and_text.png", width="300">
</div>
