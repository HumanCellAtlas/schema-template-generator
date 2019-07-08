[![Docker Repository on Quay](https://quay.io/repository/humancellatlas/schema-template-generator/status "Docker Repository on Quay")](https://quay.io/repository/humancellatlas/schema-template-generator)

# HCA spreadsheet template generator

The HCA spreadsheet template generator is an interactive UI to generate HCA metadata spreadsheets and YAML files based on the latest set of metadata schemas.

To run the service locally you'll need python 3 and all the dependencies in [requirements.txt](requirements.txt).


```
pip install -r requirements.txt
```


# Web application

## Running with python

Start the web application with

```
python generator/template_generator_app.py
```

Alternatively, you can build and run the app with docker. To run the web application with docker for build the docker image with

```
docker build . -t generator-demo:latest
```

then run the docker container. You will need to provide the URL to the [ingestion API](https://github.com/HumanCellAtlas/ingest-core)

```
docker run -p 5000:5000 -e INGEST_API=http://localhost:8080 generator-demo:latest
```

The application will be available at http://localhost:5000

