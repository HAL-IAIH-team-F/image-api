FROM python:3.12
WORKDIR /app
COPY ./requirements.lock ./requirements.lock
RUN PYTHONDONTWRITEBYTECODE=1 pip install --no-cache-dir --upgrade -r requirements.lock
#COPY ./migrations ./migrations
COPY ./app ./
#COPY ./alembic.ini ./alembic.ini

ENTRYPOINT ["bash", "-c"]
# alembic upgrade head &&
CMD ["uvicorn hew_back:app --host 0.0.0.0 --port 80"]
