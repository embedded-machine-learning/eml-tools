echo #==============================================#
echo # CDLEML Process TF2 Object Detection API
echo #==============================================#

:: Constant Definition
set USERNAME=wendt
set USEREMAIL=alexander.wendt@tuwien.ac.at
set MODELNAME=
set PYTHONENV=tf26
set SCRIPTPREFIX=C:\Projekte\21_SoC_EML\scripts-and-guides\scripts

:: Environment preparation
echo Activate environment %PYTHONENV%
call conda activate %PYTHONENV%

echo #======================================================#
echo # Generate TF Records from images and XML as Pascal Voc
echo #======================================================# 

python %SCRIPTPREFIX%\conversion\convert_voc_to_tfrecord_mod.py ^
 -x "annotations/voc_xmls/train" ^
 -i "images/train" ^
 -l "annotations/label_map.pbtxt" ^
 -o "prepared-records/train.record" ^
 -n 1