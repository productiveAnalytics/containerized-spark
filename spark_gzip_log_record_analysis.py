#! /usr/bin/env python3
# author: LalitC

DEBUG:bool = True

import findspark
findspark.init()

from pprint import pprint

import logging
logger = logging.getLogger()
logging.basicConfig(format='%(asctime)s %(message)s',level=logging.INFO)

from pathlib import Path
import os
logger.info('current folder=%s', Path.cwd())

import sys
logger.info('Python version=%s', sys.version)
logger.info('System path=%s', sys.path)

from pyspark import SparkConf
conf:SparkConf = SparkConf().setAppName("pyspark-local")

# Corresponds to: 
#    pyspark --packages "org.apache.hadoop:hadoop-aws:3.2.1,com.amazonaws:aws-java-sdk-bundle:1.11.563"
conf.set('spark.jars.packages', 'org.apache.hadoop:hadoop-aws:3.2.1,com.amazonaws:aws-java-sdk-bundle:1.11.563')

# Note: ensure to set local env variables
# export AWS_ACCESS_KEY_ID=<my-aws-access-key>
# export AWS_SECRET_ACCESS_KEY=<my-aws-secret-key>
conf.set('spark.hadoop.fs.s3a.aws.credentials.provider', 'com.amazonaws.auth.EnvironmentVariableCredentialsProvider')
conf.set('spark.hadoop.fs.s3a.impl', 'org.apache.hadoop.fs.s3a.S3AFileSystem')
conf.set('spark.hadoop.fs.s3a.impl.disable.cache', 'true')
conf.set('com.amazonaws.services.s3.enableV4', 'true')

logger.info('Spark config=%s', conf.getAll())

# Create spark context
from pyspark import SparkContext
sc:SparkContext = SparkContext.getOrCreate(conf=conf)
sc.setLogLevel('INFO')
logger.info('Spark version=%s', sc.version)
logger.info('Spark Context (i.e. sc) :===%s', sc)

from pyspark.sql import SparkSession
spark = SparkSession.builder.config(conf=conf).getOrCreate()
logger.info('Spark Session (i.e. spark) :===%s', spark)

# import glob
# for fname in glob.glob('./*/*.gz'):
#     print(f'|---{fname}')

raw_log_df = spark.read.text('access_log/yyyy=2022/mm=04/dd=10/access_log_local_20220410.gz')
raw_log_df.printSchema()

logger.info('Total records=%s', raw_log_df.count())

if DEBUG:
    sample_raw_log_df = raw_log_df.sample(0.1)

    print('Showing raw log records')
    sample_raw_log_df.show(truncate=False)
else:
    sample_raw_log_df = raw_log_df


## Data format:
## link097.txdirect.net - - [01/Jul/1995:00:01:31 -0400] "GET /images/KSC-logosmall.gif HTTP/1.0" 200 1204

host_pattern:str = r'(^\S+\.[\S+\.]+\S+)\s'
ts_pattern:str = r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2} -\d{4})]'
method_uri_protocol_pattern:str = r'\"(\S+)\s(\S+)\s*(\S*)\"'
status_pattern:str = r'\s(\d{3})\s'
content_size_pattern:str = r'\s(\d+)$'

from pyspark.sql.functions import regexp_extract
logs_df = sample_raw_log_df.select(
    regexp_extract('value', host_pattern, 1).alias('host'),
    regexp_extract('value', ts_pattern, 1).alias('timestamp'),
    regexp_extract('value', method_uri_protocol_pattern, 1).alias('method'),
    regexp_extract('value', method_uri_protocol_pattern, 2).alias('endpoint'),
    regexp_extract('value', method_uri_protocol_pattern, 3).alias('protocol'),
    regexp_extract('value', status_pattern, 1).cast('integer').alias('status'),
    regexp_extract('value', content_size_pattern, 1).cast('integer').alias('content_size')
)

logs_df.printSchema()

if DEBUG:
    print('Showing parsed log records')
    logs_df.show(truncate=False)

logs_df.createOrReplaceTempView('log_table')

from pyspark.sql import SQLContext
sqlContext = SQLContext(sc)
top_N_df = sc.sql("""
select host, count(endpoint) as url_count 
from log_table 
group by host 
order by url_count
""")
top_N_df.head(10).show(truncate=True)