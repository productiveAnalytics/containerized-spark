package com.dockerized.spark.sparkindocker.processor;

import java.util.Objects;

import org.springframework.beans.factory.InitializingBean;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.stereotype.Component;


import org.apache.spark.SparkConf;
import org.apache.spark.sql.SparkSession;
import org.apache.spark.sql.Dataset;
import org.apache.spark.sql.Row;
import static org.apache.spark.sql.functions.col;
import static org.apache.spark.sql.functions.regexp_extract;

import lombok.extern.log4j.Log4j2;

@Component("top_n_analyzer")
@Log4j2
public class TopNAnalyzer implements InitializingBean, CommandLineRunner {

    @Value("${data.file_name:}")
    private String dataFilename;

    @Value("${app.name:local-spark-app}")
    private String sparkAppName;

    @Value("${spark.master:local[*]}")
    private String sparkMaster;

    private SparkConf sparkConf;

    public void afterPropertiesSet() {
        // validate
        Objects.requireNonNull(this.dataFilename, "Data file must be provided");

        configureSpark();
        Objects.requireNonNull(this.sparkConf, "Spark Config must not be null");
        
        log.debug("TopNAnalyzer is ready!");
    }

    private void configureSpark() {
        SparkConf conf = new SparkConf();

        conf.setMaster(this.sparkMaster);
        conf.setAppName(this.sparkAppName);

        this.sparkConf = conf;
    }

    @Override
    public void run(String... args) throws Exception {
        int topNRecords = 0;
        if (args.length > 0) {
            topNRecords = Integer.parseInt(args[0]);
        }

        process(topNRecords);
    }

    private void process(final int topN) {
        SparkSession spark = SparkSession.builder().config(this.sparkConf).getOrCreate();
        
        Dataset<Row> value_df = spark.read().text(this.dataFilename);
        value_df.show(5);
    }
}
