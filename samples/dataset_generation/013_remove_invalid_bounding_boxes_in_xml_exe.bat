echo #==============================================#
echo # CDLEML Process TF2 Object Detection API
echo #==============================================#

:: Constant Definition
set USERNAME=wendt
set USEREMAIL=alexander.wendt@tuwien.ac.at
set MODELNAME=tf2oda_ssdmobilenetv2_320_320_coco17_D100_pedestrian
set PYTHONENV=tf24
set BASEPATH=.
set SCRIPTPREFIX=..\..\scripts-and-guides\scripts

:: Environment preparation
echo Activate environment %PYTHONENV%
call conda activate %PYTHONENV%

echo #======================================================#
echo # Generate TF Records from images and XML as Pascal Voc
echo #======================================================# 

echo run script from ./samples/tmp

python C:\Projekte\21_SoC_EML\scripts-and-guides\scripts\data_preparation\remove_invalid_bounding_boxes_in_xml.py ^
--annotation_folder="annotations/voc_xmls" ^
--output_folder="annotations/voc_xmls/cleaned"

::python C:\Projekte\21_SoC_EML\scripts-and-guides\scripts\data_preparation\remove_invalid_bounding_boxes_in_xml.py ^
::--annotation_folder="annotations/voc_xmls/" ^
::--output_folder="annotations/voc_xmls/validation/cleaned"