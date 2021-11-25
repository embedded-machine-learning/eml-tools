@echo off 
setlocal enabledelayedexpansion 

set USERNAME=wendt
set USEREMAIL=alexander.wendt@tuwien.ac.at
set MODELNAME=tf2oda_ssdmobilenetv2_320_320_coco17_D100_pedestrian
set PYTHONENV=tf26
set SCRIPTPREFIX=C:\Projekte\21_SoC_EML\scripts-and-guides\scripts

echo #######################################
echo # View images                         #
echo #######################################

set FOLDERLIST[0]=PXL_20210928_135448560_Kopie.jpg
set FOLDERLIST[1]=PXL_20210928_135448560.jpg
::set FOLDERLIST[2]=PXL_20210928_135445997.jpg
::set FOLDERLIST[3]=PETS09_S2L2_t1455_view001
::set FOLDERLIST[4]=PETS09_S2L3_t1441_view001
::set FOLDERLIST[5]=TownCentre

set SUBFOLDER=val

:: Environment preparation
echo Activate environment %PYTHONENV%
call conda activate %PYTHONENV%
rem SET IMAGESET=PETS09_S1L1_t1357_view001

for /l %%n in (0, 1, 2) do ( 
   echo !FOLDERLIST[%%n]!
   call python %SCRIPTPREFIX%\inference_evaluation\obj_visualize_compare_bbox.py ^
   --labelmap="annotations/label_map.pbtxt" ^
   --output_dir="results" ^
   --image_path1="images/!FOLDERLIST[%%n]!" --annotation_dir1="images" --title1="EML Video Example GT" ^
   --color_gt
::   --image_path3="images/train/!FOLDERLIST[%%n]!_frame_0101.jpg" --annotation_dir3="annotations/xmls/train" --title3="!FOLDERLIST[%%n]! Image 0101" 
::   --use_three_images
)

echo Finished
