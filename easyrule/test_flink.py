from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream import TimeCharacteristic
from pyflink.datastream import Types

# 创建执行环境
env = StreamExecutionEnvironment.get_execution_environment()
env.set_stream_time_characteristic(TimeCharacteristic.EventTime)