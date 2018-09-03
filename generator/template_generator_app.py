#!/usr/bin/env python
import sys

import os
import tempfile

import yaml
from flask import Flask, Markup, flash, request, render_template, redirect, url_for
from flask_cors import CORS, cross_origin
from flask import json
import logging

from openpyxl.compat import file
from yaml import dump as yaml_dump
from yaml import load as yaml_load
from utils import schema_loader
from utils import properties_builder
from werkzeug.utils import secure_filename


# from ingest-client import schema_template

LATEST_SCHEMAS = "http://api.ingest.{env}.data.humancellatlas.org/schemas/search/latestSchemas"

STATUS_LABEL = {
    'Valid': 'label-success',
    'Validating': 'label-info',
    'Invalid': 'label-danger',
    'Submitted': 'label-default',
    'Complete': 'label-default'
}

DEFAULT_STATUS_LABEL = 'label-warning'


HTML_HELPER = {
    'status_label': STATUS_LABEL,
    'default_status_label': DEFAULT_STATUS_LABEL
}

app = Flask(__name__, static_folder='static')
app.secret_key = 'cells'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
logger = logging.getLogger(__name__)

DISPLAY_NAME_MAP = {}


@app.route('/upload', methods=['POST'])
def upload_file():
    #read yaml file and process it
    return "foo"


@app.route('/load', methods=['GET'])
def load_schemas():
    # TO DO - remove hard-coded environment!
    schemas_url = LATEST_SCHEMAS.replace("{env}", "dev")
    urls = schema_loader.retrieve_latest_schemas(schemas_url, "dev.data")

    schema_properties = []

    for url in urls:
        schema = schema_loader.load_schema(url)

        props = properties_builder.extract_properties(schema)
        schema_properties.append(props)

        DISPLAY_NAME_MAP[props["name"]] = props["title"]

    return render_template('schemas.html', helper=HTML_HELPER, schemas=schema_properties)
    # return redirect(url_for('schemas'))


@app.route('/')
def index():
    return render_template('index.html', helper=HTML_HELPER)

@app.route('/generate', methods=['POST'])
def generate_yaml():

    if request.method == 'POST':
        response = request.form

        if 'schema' in response:
            selected_schemas = response.getlist('schema')

        if 'property' in response:
            selected_properties = response.getlist('property')

        pre_yaml = []

        for schema in selected_schemas:
            entry = {}
            tab = {}

            if schema in DISPLAY_NAME_MAP:
                tab["display_name"] = DISPLAY_NAME_MAP[schema]
            else:
                tab["display_name"] = schema
            columns = []
            for prop in selected_properties:
                if schema in prop:
                    print("Property " + prop + " belongs to schema " + schema)
                    columns.append(prop)
            tab["columns"] = columns
            entry[schema] = tab
            pre_yaml.append(entry)

        yaml_json = {}
        yaml_json["tabs"] = pre_yaml

        print(yaml_json)

        # yaml = yaml_dump(yaml_load(json.dump(yaml_json, indent=4)))
        # stream = file('document.yaml', 'w')
        yaml_data = yaml.dump(yaml_json, default_flow_style=False)
        print(yaml_data)

        _save_file(yaml_data)


    return redirect(url_for('index'))

# def build_yaml(pre_yaml):
#     schemas = pre_yaml.keys()
#
#     for schema in schemas:
#         properties = pre_yaml[schema]

def _save_file(data):
    dir = os.getcwd()
    tmpFile = open(dir + "/output.yaml", "w")
    tmpFile.write(data)
    tmpFile.close()



if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    app.run(host='0.0.0.0', port=5000)