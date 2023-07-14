FROM python:alpine3.17
WORKDIR ./app
COPY CloudEx03.py .
RUN pip install flask
RUN pip install flask_restful
RUN pip install requests
EXPOSE 8000
CMD ["python3", "CloudEx03.py"]