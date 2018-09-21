#!/usr/bin/env python
import sys

import os
import tempfile

import yaml
from flask import Flask, Markup, flash, request, render_template, redirect, url_for, make_response
from flask_cors import CORS, cross_origin
import logging

from utils import schema_loader
from utils import properties_builder
import configparser
import datetime


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

CONFIG_FILE = ''

@app.route('/upload', methods=['POST'])
def upload_file():
    #read yaml file and process it
    return "foo"


@app.route('/load_all', methods=['GET', 'POST'])
def load_full_schemas():
    urls = _getSchemaUrls()
    schema_properties = process_schemas(urls)

    if request.method == 'POST':
        response = request.form

        selected_schemas = []
        if 'schema' in response:
            selected_schemas = response.getlist('schema')

        selected_references = []
        if 'reference' in response:
            selected_references = response.getlist('reference')

        for schema in schema_properties:
            if schema["name"] in selected_schemas:
                schema["pre-selected"] = True
                properties = schema["properties"]

                for ref in selected_references:
                    t = ref.split(':')[0]
                    val = ref.split(':')[1]
                    if schema["name"] == t:
                        for prop in properties.keys():
                            if val in prop and properties[prop] == "not required":
                                schema["properties"][prop] = "pre-selected"

    return render_template('schemas.html', helper=HTML_HELPER, schemas=schema_properties)

def _getSchemaUrls():
    # TO DO - remove hard-coded environment!
    schemas_url = LATEST_SCHEMAS.replace("{env}", "dev")
    urls = schema_loader.retrieve_latest_schemas(schemas_url, "dev.data")
    return urls

def _loadConfig():
    config_file = configparser.ConfigParser(allow_no_value=True)
    config_file.read('config.ini')
    return config_file;


def process_schemas(urls):
    schema_properties = []
    unordered = {}
    process = ''

    for url in urls:
        schema = schema_loader.load_schema(url)

        props = properties_builder.extract_properties(schema)

        if "stand_alone" in props:
            standAlone = props["stand_alone"]
            for sa in standAlone:
                if sa["name"] not in unordered.keys():
                    unordered[sa["name"]] = sa
                else:
                    sa["name"] = props["name"] + '.'+ sa["name"]
                    unordered[sa["name"]] = sa
            del props["stand_alone"]
        if props["name"] == "process":
            process = props["properties"]
            for k in process.keys():
                if process[k] == "required":
                    process[k] = "not required"

        unordered[props["name"]] = props

        DISPLAY_NAME_MAP[props["name"]] = props["title"]

    if 'ordering' in CONFIG_FILE:
        for key in CONFIG_FILE['ordering'].keys():
            if key in unordered.keys():
                if CONFIG_FILE['ordering'][key] == 'process' and process != '':
                    unordered[key]["properties"].update(process)

                schema_properties.append(unordered[key])
            else:
                print(key + " is currently not a recorded property")
    return schema_properties

@app.route('/uploadYaml', methods=['POST'])
def uploadYaml():
    return render_template('index.html', helper=HTML_HELPER)

@app.route('/load_select', methods=['GET'])
def selectSchemas():
    urls = _getSchemaUrls()
    unordered = {}

    for url in urls:
        schema = schema_loader.load_schema(url)

        references = properties_builder.extract_references(schema)
        unordered[references["name"]] = references
    orderedReferences = []

    if 'ordering' in CONFIG_FILE:
        for key in CONFIG_FILE['ordering'].keys():
            if key in unordered.keys():
                orderedReferences.append(unordered[key])
            else:
                print(key + " is currently not a recorded property")

    return render_template('schema_selector.html', helper=HTML_HELPER, schemas=orderedReferences)


@app.route('/')
def index():
    return render_template('index.html', helper=HTML_HELPER)

@app.route('/generate', methods=['POST'])
def generate_yaml():

    response = request.form

    selected_schemas = []
    if 'schema' in response:
        selected_schemas = response.getlist('schema')

    selected_properties = []
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
            t = prop.split(':')[0]
            val = prop.split(':')[1]
            if schema == t:
                # print("Property " + prop + " belongs to schema " + schema)
                columns.append(val)
        tab["columns"] = columns
        entry[schema] = tab
        pre_yaml.append(entry)

    yaml_json = {}
    yaml_json["tabs"] = pre_yaml

    # print(yaml_json)

    yaml_data = yaml.dump(yaml_json, default_flow_style=False)

    now = datetime.datetime.now()
    filename = "hca_yaml-" + now.strftime("%Y-%m-%dT%H-%M-%S") + ".yaml"
    response = make_response(yaml_data)
    response.headers.set('Content-Type', 'application/x-yaml')
    response.headers.set('Content-Disposition', 'attachment',
                         filename=filename)
    return response

    # TO DO switch previous section and remove below - temp setting to avoid 100s of downloads in testing
    # print(yaml_data)
    # return redirect(url_for('index'))



def _save_file(data):
    dir = os.getcwd()
    tmpFile = open(dir + "/output.yaml", "w")
    tmpFile.write(data)
    tmpFile.close()



if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    CONFIG_FILE = _loadConfig()

    app.run(host='0.0.0.0', port=5000)