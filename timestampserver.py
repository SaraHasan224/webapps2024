import thriftpy2
from thriftpy2.rpc import make_server
import time

# Load the Timestamp thrift definition
timestamp_thrift = thriftpy2.load("timestamp.thrift", module_name="timestamp_thrift")
Timestamp = timestamp_thrift.TimestampService


# Define the handler class
class TimestampHandler:

    # Method to get the current system timestamp
    def getCurrentTimestamp(self):
        return int(time.time())

        # Method to echo the provided timestamp

    def echoTimestamp(self, timestamp):
        return timestamp


if __name__ == "_main_":
    # Instantiate the handler
    handler = TimestampHandler()

    # Create a server with the handler
    server = make_server(Timestamp, handler, '127.0.0.1', 9090)

    # Start serving requests
    print("Thrift server started. Listening on port 9090...")
    server.serve()
