# Databricks notebook source
# MAGIC %run ./Data_Transformation_Definitions_and_Applications
# MAGIC

# COMMAND ----------

#list all genera_classification files in my raw container
json_file_paths = list_files_recursively('mnt/raw/races2', 'general_classification.json')
#Apply data transformations and move to cleansed container in a delta format 
consolidate_race_data(json_file_paths, '/mnt/cleansed/races', 'general_classification.json')
