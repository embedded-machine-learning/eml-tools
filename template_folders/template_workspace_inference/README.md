# Template Folder Structure for inference on Devices for Tensor Flow
Template folder structure based on Tensorflow Object Detection API recommended folder structure.

## How to use it
1. Copy the whole folder structure to your project location
2. Execute remove_gitignore.py to remove all .gitignores in the sub folders
3. Copy the exported models (./exported-models) from your training project
4. Copy the inference .sh and .bat scripts and not the .py files to the folders
5. Adapt the scripts to use the correct paths and python files directly from the main repository eml-tools

Note: In the inference data structure, there are three exported-models folders: 
- exported-models-todo: Put models here that shall be tested, but not in the current run. This is important for debugging before starting with 
30 models at once
- exported-models: Here are the models that shall be run
- exported-models-finished: Put evaluated models here. In case some models fails, you don't want to run them again.

## Dataset
The datasets are kept in another folder parallel to project collection folder, i.e. ../../datasets/[YOUR DATATSET]. For evaluation, 
you usually create a separate validation dataset to avoid copying the whole unused training set to each end device

## Issues
If there are any issues or suggestions for improvements, please add an issue to github's bug tracking system or please send a mail 
to [Alexander Wendt](mailto:alexander.wendt@tuwien.ac.at)

<div align="center">
  <img src="../../_img/eml_logo_and_text.png", width="500">
</div>
