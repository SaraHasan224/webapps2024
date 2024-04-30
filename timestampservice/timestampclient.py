import thriftpy2
from thriftpy2.rpc import make_client
from thriftpy2.thrift import TException

timestamp_thrift = thriftpy2.load(
    'timestampservice/timestamp.thrift', module_name='timestamp_thrift')
Timestamp = timestamp_thrift.TimestampService

class TimestampClient:
    def __init__(self, host='127.0.0.1', port=10000):
        self.client = make_client(Timestamp, host, port)

    def get_current_timestamp(self):
        try:
            # This is a blocking call.
            return self.client.getCurrentTimestampISO()
        except TException as e:
            print('Failed to get timestamp:', e)
            return None

def main():
    timestamp_client = TimestampClient()
    current_timestamp = timestamp_client.get_current_timestamp()
    if current_timestamp:
        print('Current Timestamp:', current_timestamp)

if __name__ == '__main__':
    main()