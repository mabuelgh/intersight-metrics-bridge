FROM python:3.10-alpine

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/

EXPOSE 5001

CMD ["python", "/code/intersight_metrics_bridge_main.py"]

# ENTRYPOINT ["tail", "-f", "/dev/null"]