"""Spark batch job: raw JSON claim events to partitioned curated Parquet."""

from __future__ import annotations

import argparse

from pyspark.sql import SparkSession, functions as F, types as T

SCHEMA = T.StructType(
    [
        T.StructField("claim_id", T.StringType(), False),
        T.StructField("policy_id", T.StringType(), False),
        T.StructField("vehicle_id", T.StringType(), False),
        T.StructField("event_time", T.StringType(), False),
        T.StructField("accident_date", T.StringType(), False),
        T.StructField("claim_type", T.StringType(), False),
        T.StructField("status", T.StringType(), False),
        T.StructField("claim_amount", T.DoubleType(), False),
        T.StructField("paid_amount", T.DoubleType(), False),
        T.StructField("city", T.StringType(), False),
        T.StructField("source_system", T.StringType(), False),
    ]
)


def transform(input_path: str, output_path: str, quarantine_path: str) -> None:
    spark = SparkSession.builder.appName("insurance-claims-transform").getOrCreate()
    raw = spark.read.schema(SCHEMA).json(input_path)
    typed = (
        raw.withColumn("event_timestamp", F.to_timestamp("event_time"))
        .withColumn("accident_dt", F.to_date("accident_date"))
        .withColumn("event_date", F.to_date("event_timestamp"))
    )
    quality_reason = (
        F.when(F.col("claim_id").isNull(), F.lit("missing_claim_id"))
        .when(F.col("claim_amount") < 0, F.lit("negative_claim_amount"))
        .when(F.col("paid_amount") < 0, F.lit("negative_paid_amount"))
        .when(F.col("paid_amount") > F.col("claim_amount"), F.lit("paid_exceeds_claim"))
        .when(F.col("accident_dt") > F.col("event_date"), F.lit("accident_after_event"))
    )
    checked = typed.withColumn("quality_reason", quality_reason)
    valid = (
        checked.filter(F.col("quality_reason").isNull())
        .dropDuplicates(["claim_id"])
        .withColumn("event_year", F.year("event_timestamp"))
        .withColumn("event_month", F.month("event_timestamp"))
    )
    invalid = checked.filter(F.col("quality_reason").isNotNull())

    valid.write.mode("overwrite").partitionBy("event_year", "event_month").parquet(output_path)
    invalid.write.mode("overwrite").json(quarantine_path)
    spark.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--quarantine", required=True)
    args = parser.parse_args()
    transform(args.input, args.output, args.quarantine)
