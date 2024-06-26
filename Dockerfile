FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt ./requirements.txt
COPY logo.png ./logo.png
RUN pip install -r requirements.txt
RUN pip install psycopg2-binary
EXPOSE 8501

COPY . /app
ENTRYPOINT ["streamlit", "run", "app.py", "--server.fileWatcherType", "none"]