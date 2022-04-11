# Containerized Spark

## Create docker images

### base image (if version changed, make change to down-stream Dockerfile in line: FROM spark_base/<version_id>)
```
docker build -f docker/Dockerfile_spark_base -t spark_base:v1 .
```

### Spark Master image (tag = spark_master:v1)
```
docker build -f docker/Dockerfile_spark_master -t spark_master:v1 .
```

### Spark Worker image (tag = spark_worker:v1)
```
docker build -f docker/Dockerfile_spark_worker -t spark_worker:v1 .
```

### Spark submit image (tag = spark_submit:v1)
```
docker build -f docker/Dockerfile_spark_submit -t spark_submit:v1 .
```

## Create docker network: spark-cluster-network
```
docker swarm init
docker network create -d overlay --attachable spark-cluster-network
```

Confirm the overlay network ```docker network ls```

## Run containers by attaching to our docker network: spark-cluster-network

### Master node container (name = spark-master)
```
docker run -it --name spark-master --network spark-cluster-network -p 8080:8080 spark_master:v1
```

Confirm the master alive by visiting ```http://localhost:8080/```

### Worker-1 container (local port: 8081)
```
docker run -it --name spark-worker-1 --network spark-cluster-network -p 8081:8081 --env MEMORY=2G --env CORES=2 --env MASTER_CONTAINER_NAME=spark-master spark_worker:v1
```

### Worker-2 container (local port: 8082)
```
docker run -it --name spark-worker-2 --network spark-cluster-network -p 8082:8081 --env MEMORY=2G --env CORES=2 --env MASTER_CONTAINER_NAME=spark-master spark_worker:v1
```

### Spark Submit
```
docker run -it --name spark-submit --network  spark-cluster-network -p 4040:4040 --env MASTER_CONTAINER_NAME
=spark-master spark_submit:v1 bash
```