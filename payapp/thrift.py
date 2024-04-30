from django.db import models
from thriftpy2.protocol import TBinaryProtocolFactory, TBinaryProtocol
# from thriftpy2.thrift import
# from thriftpy2.transport import TMemoryBuffer
# from your_thrift_module import Timestamp  # Replace with your Thrift-generated timestamp module
from datetime import datetime

from thriftpy2.transport import TMemoryBuffer


class ThriftTimestampField(models.Field):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        return 'BINARY'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        transport = TMemoryBuffer(value)
        protocol = TBinaryProtocol(transport)
        timestamp = Timestamp()
        timestamp.read(protocol)
        return timestamp

    def to_python(self, value):
        if isinstance(value, Timestamp):
            return value
        return None

    def get_prep_value(self, value):
        if value is None:
            return None
        transport = TMemoryBuffer()
        protocol = TBinaryProtocol(transport)
        value.write(protocol)
        return transport.getvalue()

    def pre_save(self, model_instance, add):
        # Set current time if the value is None and adding a new object
        if add and not getattr(model_instance, self.attname):
            setattr(model_instance, self.attname, Timestamp(datetime.utcnow().timestamp()))
        return super().pre_save(model_instance, add)
