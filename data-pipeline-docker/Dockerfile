FROM apache/airflow:2.9.1

# Copy your requirements file
COPY requirements.txt /

# Install Python packages (like kafka-python, pymongo, etc.)
RUN pip install --no-cache-dir -r /requirements.txt