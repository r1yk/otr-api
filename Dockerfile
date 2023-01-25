# FROM otrr1y/otr-env:latest

# FROM python:3.10
# RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# RUN apt update
# RUN apt install -y ./google-chrome-stable_current_amd64.deb

# RUN wget https://chromedriver.storage.googleapis.com/99.0.4844.51/chromedriver_linux64.zip
# RUN unzip chromedriver_linux64.zip -d /usr/bin
# RUN export PATH=/usr/bin/chromedriver:$PATH
FROM python:3.10

WORKDIR /usr/src/opentrailreport
COPY . .
RUN pip install --no-cache-dir -r api_requirements.txt

EXPOSE 8080
CMD uvicorn app:app --host 0.0.0.0 --port 8080
