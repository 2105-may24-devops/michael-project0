# Base image (implied: docker.io/library/python:3) the post-colon can default to latest version
FROM python:3
# most common commands: COPY and RUN

WORKDIR /app
COPY requirements.txt show.txt *.py bread.json /app/
# the other way to do this, is:
# COPY . .
# but to not copy extra stuff, dockerignore

RUN python3 -m pip install -r requirements.txt

#the command to run when container starts, overrideable
ENTRYPOINT ["python3", "app.py"]
