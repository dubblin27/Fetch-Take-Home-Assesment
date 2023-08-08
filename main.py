#####################################
# Fetch Rewards - Take Home assesment
# Author: Sabrish Kumar Pradeep Kumar
# Email : dubblin27@gmail.com
#####################################

# Imports
import time
import json
import hashlib
import psycopg2
import boto3
import logging
from datetime import date
import traceback

# Configure logging
logging.basicConfig(filename='etl.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ETLProcessor:
    def __init__(self, sqs_queue_url, postgres_connection_string):
        self.sqs_queue_url = sqs_queue_url
        self.postgres_connection_string = postgres_connection_string

    def mask_field(self, value):
        # One-way hash the field value using SHA-256
        return hashlib.sha256(value.encode()).hexdigest()

    def parse_message(self, message):
        # Parse JSON message
        data = json.loads(message['Body'])
        
        try:
            # Flatten the JSON data and apply PII masking
            user_id = data['user_id']
            device_type = data['device_type']
            masked_ip = self.mask_field(data['ip'])
            masked_device_id = self.mask_field(data['device_id'])
            locale = data['locale']
            app_version = data['app_version'].split('.')[0]
            create_date = date.today()

            return user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date
        except Exception as e:
            # Log errors and problematic data
            logger.error(f"Error during batch insertion[Error]: {e}")
            logger.error(f"Error during batch insertion[Error Data]: {data}")
            return None

    def receive_batch_messages(self, batch_size=1000):
        # Connect to AWS SQS
        sqs = boto3.client('sqs', endpoint_url=self.sqs_queue_url)

        # Read batch of messages from the SQS Queue
        response = sqs.receive_message(QueueUrl=self.sqs_queue_url, MaxNumberOfMessages=batch_size, VisibilityTimeout=1)
        messages = response.get('Messages', [])
        print(len(messages))
        records_to_insert = []
        for message in messages:
            record = self.parse_message(message)
            # Skip problematic data
            if not record: 
                continue 
            records_to_insert.append(record)

        return records_to_insert

    def process_messages(self):
        try:
            # Connect to Postgres using a context manager
            with psycopg2.connect(self.postgres_connection_string) as conn:
                logger.info("ETL process started.")
                
                while True:
                    # Receive batch of messages and process them
                    records_to_insert = self.receive_batch_messages()
                    if not records_to_insert:
                        logger.info("No messages found in the queue.")
                        break

                    try:
                        # Insert the batch of data into the Postgres database
                        with conn.cursor() as cursor:
                            insert_query = """
                                INSERT INTO user_logins
                                (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
                                VALUES (%s, %s, %s, %s, %s, %s, %s )
                            """
                            cursor.executemany(insert_query, records_to_insert)
                            conn.commit()
                    except Exception as e:
                        logger.error(f"Error during batch insertion: {e}")

                    # Wait for a short period to avoid excessive API calls
                    time.sleep(1)

        except KeyboardInterrupt:
            logger.info("ETL process stopped by user.")
        except Exception as e:
            print(traceback.format_exc())
            logger.error(f"Unexpected error during ETL process: {e}")
        

if __name__ == "__main__":
    # Configurations
    SQS_QUEUE_URL = 'http://localhost:4566/000000000000/login-queue'
    POSTGRES_CONNECTION_STRING = "dbname=postgres user=postgres password=postgres host=localhost port=5432"

    # Create and run ETL process
    etl_processor = ETLProcessor(SQS_QUEUE_URL, POSTGRES_CONNECTION_STRING)
    etl_processor.process_messages()
