FROM python:3.11.13
WORKDIR /app
COPY ./agent_app.py /app
COPY ./agent.py /app
COPY ./db.py /app
COPY ./requirements.txt  /app

RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "agent_app.py" ] 