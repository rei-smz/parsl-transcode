# 使用 Ubuntu 为基础镜像
FROM ubuntu:20.04

# 设置环境变量以避免在安装时出现交互式提示
ENV DEBIAN_FRONTEND=noninteractive

# 安装 ffmpeg 和 Python3
RUN apt-get update && \
    apt-get install -y ffmpeg python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 使用 pip 安装 Python 库
RUN pip3 install minio

ENV MINIO_ENDPOINT="http://your-minio-service:9000" \
    BUCKET_NAME="your-bucket-name"

# 设置工作目录
WORKDIR /app

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

# 可以添加更多的设置或命令，例如复制应用代码到工作目录
# COPY ./my_app /app

# 启动时运行的命令（可以根据需要修改）
# CMD ["python3", "-m", "http.server", "8000"]
ENTRYPOINT ["/app/start.sh"]
