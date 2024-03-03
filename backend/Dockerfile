FROM python:3.11.6
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY eightpack eightpack
CMD ["python", "-m", "eightpack.app"]