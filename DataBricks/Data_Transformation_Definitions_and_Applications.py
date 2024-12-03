# Databricks notebook source
import pyspark.sql.functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import StringType, IntegerType
import re

# COMMAND ----------

# Function to list all paths containg a specific file name
def list_files_recursively(path, file_name):
    all_files = []
    # List all items in the path
    items = dbutils.fs.ls(path)

    for item in items:
        if item.isDir():
            # If it's a directory, recursively list its contents
            all_files.extend(list_files_recursively(item.path, file_name))
        elif item.name.endswith(file_name):
            # Add the file to the list
            all_files.append(item.path)
    return all_files

# COMMAND ----------

# Function to parse race name and year from the file path
def parse_path(file_path, file_name):
    #pattern = rf".*/races/(.*/(.*)/{file_name})"
    pattern = rf".*/races\d*/(.*?)/(\d+)/{file_name}"
    match = re.match(pattern, file_path)
    #match = re.match(r".*/races/(.*)/(.*)/general_classification\.json", file_path)
    if match:
        race_name = match.group(1)
        year = match.group(2)
        return race_name, year
    return None, None

# COMMAND ----------

# Time-related helper functions
def time_to_seconds(time_str):
    hh, mm, ss = map(int, time_str.split(':'))
    return hh * 3600 + mm * 60 + ss

def seconds_to_time(total_seconds):
    hh = total_seconds // 3600
    mm = (total_seconds % 3600) // 60
    ss = total_seconds % 60
    return f'{hh}:{mm:02d}:{ss:02d}'

def calculate_total_time(rank, time, first_rank_time):
    time_in_seconds = time_to_seconds(time)
    total_time_in_seconds = (
        time_in_seconds if rank == '1' else time_to_seconds(first_rank_time) + time_in_seconds
    )
    return seconds_to_time(total_time_in_seconds)

calculate_total_time_udf = F.udf(calculate_total_time, StringType())

# Step 1: Define the custom Python function
def convert_to_hmss_format(rnk, time_str, prev_time):
    # Special case for the first row
    if rnk == '1':
        return time_str

    # Check if the time starts with ",," (indicating the same time as the previous row)
    if time_str.startswith(',,'):
        parts = prev_time.split(':')
        if len(parts) == 5:
            return(f"{parts[0]}:{parts[1]:02}:{int(parts[2][0:2]):02}")
        if len(parts) == 3:
            return(f"00:{int(parts[0]):02}:{int(parts[1][0:2]):02}")

    # Time conversion logic
    parts = time_str.split(':')
    if len(parts) == 5:
        return(f"{parts[0]}:{parts[1]:02}:{int(parts[2][0:2]):02}")
    if len(parts) == 3:
        return(f"00:{int(parts[0]):02}:{int(parts[1][0:2]):02}")

# Step 2: Register the UDF with Spark
convert_time_udf = F.udf(convert_to_hmss_format, StringType())

# COMMAND ----------

# General Transformation Function
def transform_classification_data(df, classification_name, race_name, year):
    """
    Transforms race classification data by adding metadata, formatting columns,
    and calculating new time-based metrics.

    Args:
        df (DataFrame): Input DataFrame with race classification data.
        classification_name (str): Name of the classification.
        race_name (str): Name of the race.
        year (int): Year of the race.

    Returns:
        DataFrame: Transformed DataFrame with columns reordered.
    """
    # Add metadata columns
    df = (
        df.withColumn("Race_name", F.lit(race_name))
          .withColumn("Year", F.lit(year))
    )
    
    if classification_name != "Teams classification":
        df = (df.withColumn("Index", F.expr("locate(Team, Rider)"))
            .withColumn("Rider", F.trim(F.expr("substring(Rider, 1, Index - 1)")))
        )
    if classification_name in ["Final GC", "Youth classification", "Teams classification"]:
        # Format time and calculate total time
        df = df.withColumn("Prev_time", F.lag("Time").over(Window.orderBy("Rnk")))
        df = df.withColumn(
            "formatted_Time", convert_time_udf(df["Rnk"], df["Time"], df["Prev_time"])
        )
        first_rank_time = df.filter(F.col("Rnk") == 1).select("formatted_Time").collect()[0][0]
        df = df.withColumn(
            "TotalTime", calculate_total_time_udf(F.col("Rnk"), F.col("formatted_Time"), F.lit(first_rank_time))
        )
        
    # Drop unnecessary columns
    existing_columns = df.columns
    columns_to_drop = ["Prev_time", "Time", "formatted_Time", "H2H", "▼▲", "Time_won_lost", "Index", "Prev", "Today"]
    columns_to_drop = [col for col in columns_to_drop if col in existing_columns]
    df = df.drop(*columns_to_drop)  
        
        
    # Rename columnsƒ
    df = df.withColumnRenamed("BIB", "Race_number")
    
    # Cast shared columns to appropriate data types
    cast_dict = {
        "Age": IntegerType(),
        "Race_number": IntegerType(),
        "Rnk": IntegerType(),
        "Points" : IntegerType(),
    }
    for col_name, data_type in cast_dict.items():
        if col_name in df.columns:
            df = df.withColumn(col_name, F.col(col_name).cast(data_type))
    
    
    # Define column ordering rules
    column_order_mapping = {
        "Final GC": ["Rider", "Rnk", "TotalTime", "Team"],
        "Points classification": ["Rider", "Rnk", "Points", "Team"],
        "Youth classification": ["Rider", "Rnk", "TotalTime", "Team"],
        "Mountains classification": ["Rider", "Rnk", "Points", "Team"],
        "Teams classification": ["Team", "Rnk", "TotalTime", "Class"]
    }
    desired_order = column_order_mapping[classification_name]
    end_columns = ["Race_name", "Year"]
    existing_columns = df.columns
    reordered_columns = [col for col in desired_order if col in existing_columns] + \
                        [col for col in existing_columns if col not in desired_order + end_columns] + \
                        [col for col in end_columns if col in existing_columns]
    df = df.select(*reordered_columns)
    
    return df


# COMMAND ----------

# Consolidate GC classifications by race
def consolidate_race_data(json_paths, cleansed_root, file_name):
    for file_path in json_paths:
        race_name, year = parse_path(file_path, file_name)
        
        if race_name and year:
            df_raw = spark.read.option("multiline", "true").json(file_path)
            classification_names = df_raw.columns
            
            for classification in classification_names:
                df = df_raw.select(F.explode(F.col(classification)).alias("row"))

                # Flatten the nested structure
                df_flat = df.select("row.*")

                if "Time won/lost" in df_flat.columns:
                    df_flat = df_flat.withColumnRenamed("Time won/lost", "Time_won_lost")
                        
                df_transformed = transform_classification_data(df_flat, classification, race_name, year)
                        
                delta_path = f"{cleansed_root}/{race_name}/{classification}"

                #write to delta
                df_transformed.write.mode("append").format("delta").option("mergeSchema", "true").save(delta_path)
