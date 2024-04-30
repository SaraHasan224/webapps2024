import thriftpy2
from thriftpy2.rpc import make_server
from datetime import datetime

timestamp_thrift = thriftpy2.load('./timestamp.thrift', module_name='timestamp_thrift')
Timestamp = timestamp_thrift.TimestampService

class TimestampHandler:
    def getCurrentTimestamp(self):
        # Returns the current datetime in ISO 8601 format
        return datetime.utcnow().isoformat() + 'Z'

if __name__ == '__main__':
    print("Starting the timestamp server...")
    handler = TimestampHandler()
    server = make_server(Timestamp, handler, '127.0.0.1', 10000)
    server.serve()