FROM vulhub/flink:1.11.2
# 删除负责/jobmanager/logs读取文件的类，直接删掉漏洞接口
RUN rm -f /opt/flink/lib/flink-runtime-*.jar
WORKDIR /opt/flink



