FRO python:alpine3.17
WORKDIR ./app
COPY CloudE .
RUN pip install requests
EXPOSE 8000
CMD ["python3", "CloudEx03.py"]
