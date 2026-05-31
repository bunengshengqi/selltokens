FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
EXPOSE 8001

# 生产默认：只初始化数据库结构，不写入 demo 数据。
# 如需在开发环境塞演示数据，可在 docker compose 里覆盖 command:
#   command: python app.py --init-db --seed --host 0.0.0.0 --port 8001
CMD ["python", "app.py", "--init-db", "--host", "0.0.0.0", "--port", "8001"]
