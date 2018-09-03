FROM frolvlad/alpine-python2
MAINTAINER Dani Welter "dwelter@ebi.ac.uk"

RUN mkdir /app
COPY generator /app/generator
COPY generator/templates /app/templates
COPY generator/static /app/static
COPY generator/template_generator_app.py requirements.txt /app/
WORKDIR /app

RUN pip install -r /app/requirements.txt

ENV INGEST_API=http://localhost:8080

EXPOSE 5000
ENTRYPOINT ["python"]
CMD ["generator/generator_app.py"]