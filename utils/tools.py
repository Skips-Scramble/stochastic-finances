from pyspark.sql import DataFrame
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, DateType, IntegerType, FloatType

def make_type_schemas(name_list: list, cols_list: list, schema_type: type)-> list:
    """Function to make a schema list of DateType() columns"""
    schema_list = []
    for index, col in enumerate(cols_list):
        schema_list.append(StructField(name_list[index],schema_type, False))
    return schema_list

def make_as_df(
    spark: SparkSession,
    columns_list: list,
    schema: StructType
) -> DataFrame:
    """Function to take in columns and schema and return a pyspark dataframe"""

    cols_transposed = list(map(list, zip(*columns_list)))

    output_df = spark.createDataFrame(cols_transposed, schema)
    return output_df

def output_df():
    pass
