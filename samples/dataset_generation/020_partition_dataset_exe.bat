echo #====================================#
echo #Prepare dataset for training
echo #====================================#
echo #Partition dataset in a training and validation set

:: Constant Definition
set USERNAME=wendt
set USEREMAIL=alexander.wendt@tuwien.ac.at
set MODELNAME=tf2oda_ssdmobilenetv2_320_320_coco17_D100_pedestrian
set PYTHONENV=tf24
set BASEPATH=.
set SCRIPTPREFIX=C:\Projekte\21_SoC_EML\scripts-and-guides\scripts

python %SCRIPTPREFIX%\data_preparation\partition_dataset.py ^
-i "images" ^
--outputDir "images" ^
--xmlDir "images" ^
-x ^
-r 0.20 ^
--remove_source

::--remove_source #would remove the source file

rem #python 020_partition_dataset.py -i "images" --xmlDir "annotations/xmls" --file_id_dir "annotations" -r 0.10