# Template Folder Structure for Training on Server for Tensor Flow
Template folder structure based on Tensorflow Object Detection API recommended folder structure.

## How to use it
1. Copy the whole folder structure to your project location
2. Execute remove_gitignore.py to remove all .gitignores in the sub folders
3. Copy the pre-trained models (./pre-trained-models) to your training project
4. Copy the inference .sh and .bat scripts and not the .py files to the folders
5. Adapt the scripts to use the correct paths and python files directly from the main repository eml-tools

## Structure
The following structure is used:
- cfg: Training jobs for Yolo and Pytorch are put here
- exported-models: Exported models are put here
- jobs: Training jobs from Tensorflow are pur here
- models: Training models checkpoints
- pre-trained-models: If models are only fine tuned, the original models are put here
- results: Results are written here
- scripts: Put finished scripts here
- tmp: used for e.g. temporary index files that are used between scripts

## Dataset
The datasets are kept in another folder parallel to project collection folder, i.e. ../../datasets/[YOUR DATATSET]. For evaluation, 
you usually create a separate validation dataset to avoid copying the whole unused training set to each end device

## Issues
If there are any issues or suggestions for improvements, please add an issue to github's bug tracking system or please send a mail 
to [Alexander Wendt](mailto:alexander.wendt@tuwien.ac.at)

<div align="center">
  <img src="../../_img/eml_logo_and_text.png", width="500">
</div>
