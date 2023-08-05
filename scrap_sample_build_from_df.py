import findspark

findspark.init()

import random
import string
from pathlib import Path
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    FloatType,
)

import pyspark.sql.functions as spark_funcs

import numpy as np

from utils.tools import output_df

col_length = 1000
new_cols = 10

list_1 = [x for x in range(col_length)]
list_2 = [random.choice(string.ascii_letters) for _ in range(col_length)]


def generate_new_list():
    return [round(np.random.normal(5, 1), 6) for _ in range(col_length)]


def make_base_df(spark, list_1, list_2):
    """Make schemas for base data"""
    schema = StructType(
        [
            StructField("col_1", IntegerType(), False),
            StructField("col_2", StringType(), False),
        ]
    )
    columns_list = [list_1, list_2]
    cols_transposed = list(map(list, zip(*columns_list)))

    return spark.createDataFrame(cols_transposed, schema)


def main() -> None:
    spark = SparkSession.builder.appName("stochastic_finances").getOrCreate()

    base_df = make_base_df(spark, list_1, list_2)

    for i in range(new_cols):
        base_df.withColumn(f'new_col_{i}', np.random.normal(5,1))

    output_df(base_df, Path(r"./outputs/test_2.csv"))
