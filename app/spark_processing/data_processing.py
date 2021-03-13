from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext
from pyspark.sql import Row, SQLContext
import sys
import asyncio
import websockets
import json
import types


async def send_data(data):
    uri = "ws://app_web_server_1:9011"
    async with websockets.connect(uri) as websocket:
        await websocket.send(data)


# Lazily instantiated global instance of SparkSession
def get_sql_context_instance(spark_context):
    if ("sqlContextSingletonInstance" not in globals()):
        globals()["sqlContextSingletonInstance"] = SQLContext(spark_context)
    return globals()["sqlContextSingletonInstance"]


def process_rdd(time, rdd):
    print("========= %s =========" % str(time))
    try:
        # Get the singleton instance of SparkSession
        sql_context = get_sql_context_instance(rdd.context)

        # Convert RDD[String] to RDD[Row] to DataFrame
        rowRdd = rdd.map(lambda w: Row(hashtag=w[0], hashtag_count=w[1]))
        hashtags_df = sql_context.createDataFrame(rowRdd)

        # Creates a temporary view using the DataFrame
        hashtags_df.registerTempTable("hashtags")

        # Do word count on table using SQL and print it
        hashtag_counts_df = sql_context.sql(
            "select hashtag, hashtag_count from hashtags order by hashtag_count desc limit 10"
        )
        hashtag_counts_df.show()

        top_tags = [
            t.hashtag for t in hashtag_counts_df.select("hashtag").collect()
        ]
        # extract the counts from dataframe and convert them into array
        tags_count = [
            p.hashtag_count
            for p in hashtag_counts_df.select("hashtag_count").collect()
        ]
        list_hashtags = map(lambda row: row.asDict(),
                            hashtag_counts_df.collect())

        asyncio.run(send_data(json.dumps(list(list_hashtags))))
    except:
        print(sys.exc_info())
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def updateFunc(new_values, last_sum):
    return sum(new_values) + (last_sum or 0)


conf = SparkConf()
conf.setAppName("TwitterStreamApp")
# create spark context with the above configuration
sc = SparkContext(conf=conf)
sc.setLogLevel("ERROR")

ssc = StreamingContext(sc, 2)
ssc.checkpoint("checkpoint_TwitterApp")

socket_stream = ssc.socketTextStream("app_twitter_stream_1", 9009)

# split each tweet into words
words = socket_stream.flatMap(lambda line: line.split(" "))
# filter the words to get only hashtags, then map each hashtag to be a pair of (hashtag,1)
hashtags = words.filter(lambda w: '#' in w).map(lambda x: (x, 1))
# adding the count of each hashtag to its last count
hashtagsCounts = hashtags.reduceByKeyAndWindow(lambda x, y: x + y,
                                               lambda x, y: x - y, 600, 2)
hashtagsCounts.foreachRDD(process_rdd)
# start the streaming computation
ssc.start()
# wait for the streaming to finish
ssc.awaitTermination()
