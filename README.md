
# ETL Off a SQS Queue to PostgreSQL

This repository contains a Python application for reading JSON data from an AWS SQS Queue, performing data transformations, and writing the transformed data to a PostgreSQL database. The application is designed to work in a local environment using Docker and LocalStack for SQS emulation and a PostgreSQL container.

## Prerequisites

Before running the application, ensure that the following dependencies installed:

- Docker
- Docker Compose
- AWS CLI Local
- PostgreSQL client (psql)
- Python3
- Pip3

## Getting Started

1. Clone this repository:

   ```bash
   git clone https://github.com/dubblin27/Fetch-Take-Home-Assesment.git
   cd Fetch-Take-Home-Assesment/
   ```

2. Set up the local environment using Docker Compose:

   ```bash
   docker-compose up
   ```

3. Install Python dependencies:

   ```bash
   pip install boto3 psycopg2-binary
   ```

4. Run the ETL process using the following command:

   ```bash
   python3 main.py
   ```
4. See Ouputs (All outputs are present in etl.log):

   ```bash
    2023-08-08 23:51:23,782 - INFO - ETL process started.
    2023-08-08 23:51:23,795 - INFO - Found credentials in shared credentials file: ~/.aws/credentials
    2023-08-08 23:51:25,243 - INFO - No messages found in the queue.
   ```

## Configuration

Configure the following parameters in the `main.py` file before running the application:

- `SQS_QUEUE_URL`: The URL of the SQS Queue to read messages from.
- `POSTGRES_CONNECTION_STRING`: The connection string for the PostgreSQL database.

## Running the Application

Run the ETL process using the following command:

```bash
python3 main.py
```

## Checking if Data is present in the db 
- Test local access 
  - Read a message from the queue using awslocal, `awslocal sqs receive-message --queue-url http://localhost:4566/000000000000/login-queue`  
  - Connect to the Postgres database, verify the table is created 
    - psql -d postgres -U postgres -p 5432 -h localhost -W 
    - postgres=# select * from user_logins;

The application will start processing messages from the SQS Queue, performing data transformations and writing the data to the PostgreSQL database.

## PII Masking

The application includes a PII masking function that uses a one-way hash (SHA-256) to mask sensitive fields like `ip` and `device_id`. This ensures data privacy while allowing for the identification of duplicate values.

## Logging

The application logs are recorded in the `etl.log` file. We can find detailed information about the ETL process, including any errors or exceptions encountered.

## Next Steps

If I had more time, I would consider the following improvements to make the application more production-ready:

- Implementing error handling for database connections and transactions.
- Adding unit tests to ensure the correctness of the code.
- Implementing proper configuration management using environment variables.
- Using a more sophisticated hashing/masking strategy for PII data.
- Deploying the application to a cloud environment (AWS, Azure, etc.) using appropriate cloud services.
- More scaling of the code.
- Enhancing logging and monitoring to gain insights into the ETL process.

## Questions

**How would you deploy this application in production?**

For production deployment, consider container orchestration platforms like Kubernetes or AWS ECS. Set up a production-grade PostgreSQL instance and an actual SQS queue on AWS.

**What other components would you want to add to make this production-ready?**

- Implementing robust error handling and retry mechanisms.
- Setting up a monitoring and alerting system.
- Implementing data validation and cleansing processes.
- Using a secret management service for sensitive credentials.
- Implementing role-based access control for database and AWS resources.

**How can this application scale with a growing dataset?**

To scale with a growing dataset, you could consider using distributed data processing frameworks like Apache Spark or Apache Kafka Streams for data transformation and writing. Utilize cloud-based managed services for SQS and PostgreSQL for seamless scaling.

**How can PII be recovered later on?**

Since the masking is performed using a one-way hash, the PII cannot be directly recovered. However, we can maintain a separate system to map masked values to their original values securely.

**What are the assumptions you made?**

Assumptions made in this implementation include:
- The provided JSON data format remains consistent.
- The SQS queue URL and PostgreSQL connection string are correct and functional.
- The Docker images and configurations provided in the sample work as expected.
- The application runs in a single-threaded manner for simplicity.

# *THANK YOU*