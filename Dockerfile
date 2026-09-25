# syntax=docker/dockerfile:1
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends g++ gcc \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p bin data \
  && gcc -O2 -o bin/rice_calc_c polyglot/c/rice_calc.c \
  && g++ -O2 -o bin/rice_calc_cpp polyglot/cpp/rice_calc.cpp

ENV PORT=5173
ENV FLASK_DEBUG=0
EXPOSE 5173

CMD ["python", "server.py"]
