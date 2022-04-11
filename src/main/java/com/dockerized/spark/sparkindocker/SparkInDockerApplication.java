package com.dockerized.spark.sparkindocker;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Entry-point for the Spark application
 * 
 * @author LalitC
 */

@SpringBootApplication
public class SparkInDockerApplication {

	public static void main(String[] args) {
		SpringApplication.run(SparkInDockerApplication.class, args);
	}

}
