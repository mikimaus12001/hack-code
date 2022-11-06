FROM python:3.10.4

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

ENTRYPOINT [ "python" ]
CMD ["app.py"]

#EXPOSE 3200