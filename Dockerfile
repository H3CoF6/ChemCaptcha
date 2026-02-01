# 构建前端webui的dist
FROM node:18-alpine AS frontend-builder

WORKDIR /build/fsrc

COPY fsrc/package*.json ./
RUN npm install
COPY fsrc/ .
RUN npm run build

# 构建后端
FROM python:3.10-slim
WORKDIR /app/bsrc

RUN apt-get update && apt-get install -y \
    curl \
    gzip \
    && rm -rf /var/lib/apt/lists/*


COPY bsrc/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p data/mol data/sdf data/db data/log data/fonts

WORKDIR /app/bsrc/data/sdf

# 根据需求自行修改，我选了一个分子量较大的，要简单可以旋转前500k个分子式

RUN curl -O https://ftp.ncbi.nlm.nih.gov/pubchem/Compound/CURRENT-Full/SDF/Compound_167500001_168000000.sdf.gz
RUN gzip -d Compound_167500001_168000000.sdf.gz  # 解后即焚

WORKDIR /app/bsrc

# 记得改！！
ENV FILE_NAME=Compound_167500001_168000000.sdf.gz

ENV PYTHONUNBUFFERED=1

# 欺骗rich
ENV TERM=xterm-256color

COPY --from=frontend-builder /build/fsrc/dist ./app/static
COPY bsrc/ .

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]