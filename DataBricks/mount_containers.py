# Databricks notebook source
# dbutils.fs.unmount("/mnt/raw")
# dbutils.fs.unmount("/mnt/cleansed")

# COMMAND ----------

# Define the storage account, container, and SAS token
storage_account_name = "cyclingstatsproject"
container_name = "raw"
sas_token = dbutils.secrets.get("containers_tokens", "raw_token")
# put the sas token in a secret in DB

# Mount the container
dbutils.fs.mount(
    source=f"wasbs://{container_name}@{storage_account_name}.blob.core.windows.net",
    mount_point=f"/mnt/{container_name}",
    extra_configs={
        f"fs.azure.sas.{container_name}.{storage_account_name}.blob.core.windows.net": sas_token
    }
)

# Verify the mount
display(dbutils.fs.ls(f"/mnt/{container_name}"))

# COMMAND ----------

#Define the storage account, container, and SAS token
#storage_account_name = "cyclingstatsproject"
container_name2 = "cleansed"
sas_token2 = dbutils.secrets.get("containers_tokens", "cleansed_token")
#put the sas token in a secret in DB

#Mount the container
dbutils.fs.mount(
    source=f"wasbs://{container_name2}@{storage_account_name}.blob.core.windows.net",
    mount_point=f"/mnt/{container_name2}",
    extra_configs={
        f"fs.azure.sas.{container_name2}.{storage_account_name}.blob.core.windows.net": sas_token2
    }
)

#Verify the mount
display(dbutils.fs.ls(f"/mnt/{container_name2}"))
