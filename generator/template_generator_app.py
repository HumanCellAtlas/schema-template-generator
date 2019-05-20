#!/usr/bin/env python
import sys

import os
import tempfile

import yaml
from flask import Flask, Markup, flash, request, render_template, redirect, url_for, make_response, send_file
from flask_cors import CORS, cross_origin
import logging
import configparser
import datetime
from openpyxl import load_workbook
from ingest.template.schema_template import SchemaTemplate
from ingest.template.spreadsheet_builder import SpreadsheetBuilder

EXCLUDED_PROPERTIES = ["describedBy", "schema_version", "schema_type", "provenance"]

INGEST_API_URL = "http://api.ingest.{env}.data.humancellatlas.org"

STATUS_LABEL = {
    'Valid': 'label-success',
    'Validating': 'label-info',
    'Invalid': 'label-danger',
    'Submitted': 'label-default',
    'Complete': 'label-default'
}

ALLOWED_EXTENSIONS = set(['yaml', 'yml', 'xls', 'xlsx'])
UPLOAD_FOLDER = 'tmp/yaml_file'

DEFAULT_STATUS_LABEL = 'label-warning'


HTML_HELPER = {
    'status_label': STATUS_LABEL,
    'default_status_label': DEFAULT_STATUS_LABEL
}

app = Flask(__name__, static_folder='static')
app.secret_key = 'cells'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

logger = logging.getLogger(__name__)

DISPLAY_NAME_MAP = {}

CONFIG_FILE = ''

SCHEMA_TEMPLATE = {}

@app.route('/upload', methods=['POST'])
def upload_file():

    if 'yamlfile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['yamlfile']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and _allowed_file(file.filename):

        content = yaml.load(file.stream.read(), Loader=yaml.FullLoader)

        all_properties = _process_schemas()

        selected_schemas, selected_properties = _process_uploaded_file(content['tabs'])

        schema_properties = _preselect_properties(all_properties, selected_schemas, None, selected_properties)

        return render_template('schemas.html', helper=HTML_HELPER, schemas=schema_properties)


@app.route('/load_all', methods=['GET', 'POST'])
def load_full_schemas():
    all_properties = _process_schemas()

    response = request.form

    selected_schemas = []
    if 'schema' in response:
        selected_schemas = response.getlist('schema')

    selected_references = []
    if 'reference' in response:
        selected_references = response.getlist('reference')
        for ref in selected_references:
            if ref.split(":")[1] in DISPLAY_NAME_MAP:
                if ref.split(":")[0] in selected_schemas:
                    selected_schemas.append(ref.split(":")[1])
                    # selected_references.remove(ref)

    schema_properties = _preselect_properties(all_properties, selected_schemas, selected_references, None)

    return render_template('schemas.html', helper=HTML_HELPER, schemas=schema_properties)

@app.route('/load_select', methods=['GET'])
def selectSchemas():

    tab_config = SCHEMA_TEMPLATE.get_tabs_config()

    unordered = {}
    for schema in tab_config.lookup('tabs'):
        schema_name = list(schema.keys())[0]

        properties = schema[schema_name]['columns']
        schema_title = schema[schema_name]['display_name']

        schema_structure = tab_config.lookup('meta_data_properties')[schema_name]

        references = _extract_references(properties, schema_name, schema_title, schema_structure)
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

        if DISPLAY_NAME_MAP[schema]:
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

    if request.form['submitButton'] == 'yaml':
        yaml_data = yaml.dump(yaml_json, default_flow_style=False)
        now = datetime.datetime.now()
        filename = "hca_yaml-" + now.strftime("%Y-%m-%dT%H-%M-%S") + ".yaml"
        response = make_response(yaml_data)
        response.headers.set('Content-Type', 'application/x-yaml')
        response.headers.set('Content-Disposition', 'attachment',
                             filename=filename)
        return response

    elif request.form['submitButton'] == 'spreadsheet':

        temp_yaml_filename = ""
        with tempfile.NamedTemporaryFile('w', delete=False) as yaml_file:
            yaml.dump(yaml_json, yaml_file)
            temp_yaml_filename = yaml_file.name

        with tempfile.NamedTemporaryFile('w+b', delete=False) as ssheet_file:
            temp_filename = ssheet_file.name
            spreadsheet_builder = SpreadsheetBuilder(temp_filename, True)
            # TO DO currently automatically building WITH schemas tab - this should be customisable
            spreadsheet_builder.generate_workbook(tabs_template=temp_yaml_filename, schema_urls=SCHEMA_TEMPLATE.get_schema_urls(), include_schemas_tab=True)
            spreadsheet_builder.save_workbook()

            os.remove(temp_yaml_filename)
            now = datetime.datetime.now()
            export_filename = "hca_spreadsheet-" + now.strftime("%Y-%m-%dT%H-%M-%S") + ".xlsx"

            response = make_response(ssheet_file.read())
            response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response.headers.set('Content-Disposition', 'attachment',
                                 filename=export_filename)
            os.remove(temp_filename)
            return response


@app.route('/upload_xls', methods=['POST'])
def upload_spreadsheet():

    response = request.form

    if 'xlsfile' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['xlsfile']

    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)
    if file and _allowed_file(file.filename):
        # TO DO this is a hack to get past the 'No such file or directory' error but relies on directory being present - FIX!
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        wb = load_workbook(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

        if 'Schemas' in wb.sheetnames:
            schemas = wb['Schemas']
        elif 'schemas' in wb.sheetnames:
            schemas = wb['schemas']
        else:
            flash('Cannot migrate a spreadsheet without a Schemas tab')
            return redirect(request.url)

        latest_schemas = SCHEMA_TEMPLATE.get_schema_urls()

        done = False
        for row in schemas.iter_rows(min_row=2, max_col=1, max_row=100):
            if not done:
                for cell in row:
                    if cell.value is not None:
                        if cell.value in latest_schemas:
                            print(cell.value + ' is in the list of latest schemas')
                        else:
                            print(cell.value + ' is an outdated schema')
                            _migrate_schema(wb, cell.value)

                            schema_name = cell.value.split('/')[-1]

                            for schema in latest_schemas:
                                if schema_name == schema.split('/')[-1]:
                                    cell.value = schema

                    else:
                        done = True
            else:
                break
        print("All schemas processed")


        with tempfile.NamedTemporaryFile('w+b', delete=False) as ssheet_file:
            temp_filename = ssheet_file.name

            now = datetime.datetime.now()
            export_filename = "hca_spreadsheet-" + now.strftime("%Y-%m-%dT%H-%M-%S") + "_migrated.xlsx"
            wb.save(temp_filename)
            wb.close()

            response = make_response(ssheet_file.read())
            response.headers.set('Content-Type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response.headers.set('Content-Disposition', 'attachment',
                                 filename=export_filename)
            os.remove(temp_filename)
            return response


        # return render_template('schemas.html', helper=HTML_HELPER, schemas=schema_properties)
        # return render_template('index.html', helper=HTML_HELPER)


def _process_uploaded_file(file):
    selected_schemas = []
    # selected_references = []
    selected_properties = {}

    for schema in file:
        schema_name = list(schema.keys())[0]
        selected_schemas.append(schema_name)
        properties = schema[schema_name]['columns']

        props = []

        for prop in properties:
            props.append(prop)
        selected_properties[schema_name] = props

    return selected_schemas, selected_properties

def _preselect_properties(schema_properties, selected_schemas, selected_references, selected_properties):
    for schema in schema_properties:
        if schema["name"] in selected_schemas:
            schema["pre-selected"] = True
            properties = schema["properties"]

            if selected_references:
                for ref in selected_references:
                    t = ref.split(':')[0]
                    val = ref.split(':')[1]
                    if schema["name"] == t or schema["name"] == val:
                        for prop in properties.keys():
                            if (val == prop.split('.')[1] or (
                                    len(prop.split('.')) == 2 and prop.split('.')[0] != 'process')) and properties[
                                prop] == "not required":
                                schema["properties"][prop] = "pre-selected"
            if selected_properties:
                if schema["name"] in selected_properties:
                    sel_props = selected_properties[schema["name"]]

                    for prop in sel_props:
                        if prop in list(properties.keys()) and properties[prop] == "not required":
                                schema["properties"][prop] = "pre-selected"
                        elif prop not in list(properties.keys()):
                            schema["properties"][prop] = "pre-selected"
    return schema_properties

def _loadConfig(file):
    config_file = configparser.ConfigParser(allow_no_value=True)
    config_file.read(file)
    return config_file

def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def _process_schemas():

    tab_config = SCHEMA_TEMPLATE.get_tabs_config()

    unordered = {}
    all_properties = []
    for schema in tab_config.lookup('tabs'):
        property = {}

        schema_name = list(schema.keys())[0]

        property["title"] = schema[schema_name]["display_name"]
        property["name"] = schema_name
        property["select"] = False
        if "properties" not in property:
            property["properties"] = {}

        for p in schema[schema_name]['columns']:
            if len(p.split(".")) > 2:
                parent = ".".join(p.split(".")[:-1])

                # special case for modules with ontology imports where the field is required if the module is used, eg donor.timecourse.unit.text
                if len(p.split(".")) == 4:
                    if SCHEMA_TEMPLATE.lookup(parent+".required"):
                        parent = ".".join(parent.split(".")[:-1])
                if SCHEMA_TEMPLATE.lookup(parent+".required"):
                    if SCHEMA_TEMPLATE.lookup(p + ".required"):
                        property["properties"][p] = "required"
                    else:
                        property["properties"][p] = "not required"
                else:
                    property["properties"][p]="not required"
            else:
                if SCHEMA_TEMPLATE.lookup(p+".required"):
                    property["properties"][p]="required"
                else:
                    property["properties"][p]="not required"
        if property["name"] == "process":
            process = property["properties"]
            for k in process.keys():
                if process[k] == "required":
                    process[k] = "not required"

        unordered[property["name"]] = property

        DISPLAY_NAME_MAP[property["name"]] = property["title"]

    if 'biomaterial_linking' in CONFIG_FILE:
        for key in CONFIG_FILE['biomaterial_linking'].keys():
            if key in unordered.keys() and CONFIG_FILE['biomaterial_linking'][key] in unordered.keys():
                linking_field = list(unordered[CONFIG_FILE['biomaterial_linking'][key]]['properties'].keys())[0]
                unordered[key]['properties'][linking_field] = "not required"

    if 'protocol_linking' in CONFIG_FILE:
        for key in CONFIG_FILE['protocol_linking'].keys():
            if key in unordered.keys():
                protocols = []
                if "," in CONFIG_FILE['protocol_linking'][key]:
                    protocols = CONFIG_FILE['protocol_linking'][key].split(",")
                else:
                    protocols.append(CONFIG_FILE['protocol_linking'][key])

                for prot in protocols:
                    if prot in unordered.keys():
                        linking_field = list(unordered[prot]['properties'].keys())[0]
                        unordered[key]['properties'][linking_field] = "not required"

    if 'ordering' in CONFIG_FILE:
        for key in CONFIG_FILE['ordering'].keys():
            if key in unordered.keys():
                if CONFIG_FILE['ordering'][key] == 'process' and process != '':
                    unordered[key]["properties"].update(process)

                all_properties.append(unordered[key])
            elif CONFIG_FILE['ordering'][key] != '':
                parent = CONFIG_FILE['ordering'][key]
                if parent in unordered.keys():
                    new_property = {}

                    new_property["title"] = tab_config.lookup('meta_data_properties')[parent][key]['user_friendly']
                    new_property["name"] = key
                    new_property["select"] = False
                    if "properties" not in new_property:
                        new_property["properties"] = {}

                    for prop in unordered[parent]['properties']:
                        if key in prop:
                            new_property["properties"][prop] = unordered[parent]['properties'][prop]

                    for moved_prop in new_property["properties"]:
                        unordered[parent]['properties'].pop(moved_prop)

                    DISPLAY_NAME_MAP[new_property["name"]] = new_property["title"]

                    all_properties.append(new_property)

                    print(key + " is a recorded sub-property")
            else:
                print(key + " is currently not a recorded property")

    return  all_properties

def _extract_references(properties, name, title, schema):

    direct_properties = []
    for property in properties:
        prop = property.split('.')[1]
        direct_properties.append(prop)

    structure = {}
    structure["title"] = title
    structure["name"] = name

    references = {}

    for dp in direct_properties:
        if dp not in EXCLUDED_PROPERTIES:
            if schema[dp] and schema[dp]['value_type'] and schema[dp]['value_type'] == 'object' and dp not in references.keys():
                if schema[dp]['required']:
                    references[dp] = "required"
                else:
                    references[dp] = "not required"

                print(dp + " is an object property")

    structure["references"] = references
    return structure


def _migrate_schema(workbook, schema_url):
    schema_key = schema_url.split('/')[-1]
    schema_version = schema_url.split('/')[-2]

    if schema_key == 'process':
        _migrate_process_schema(workbook, schema_key, schema_version)

    linked_tabs = []

    if 'ordering' in CONFIG_FILE:
        if 'ordering' in CONFIG_FILE:
            for key in CONFIG_FILE['ordering'].keys():
                if CONFIG_FILE['ordering'][key] == schema_key:
                    linked_tabs.append(key)


    tab_config = SCHEMA_TEMPLATE.get_tabs_config()

    for schema in tab_config.lookup('tabs'):
        if schema_key == list(schema.keys())[0]:
            tab_name = schema[schema_key]['display_name']

            _update_tab(workbook, schema_key, tab_name, schema_version)

            if linked_tabs:
                for tab in linked_tabs:
                    linked_tab_name = tab_config.lookup('meta_data_properties')[schema_key][tab]['user_friendly']
                    _update_tab(workbook, schema_key, linked_tab_name, schema_version)


def _update_tab(workbook, schema_name, tab_name, schema_version):
    current_tab = workbook[tab_name]

    for col in current_tab.iter_cols(min_row=4, max_row=4):
        for cell in col:
            print(cell.value)

            if cell.value is not None and schema_name in cell.value:
                new_property = SCHEMA_TEMPLATE.lookup(cell.value, schema_version)

                if 'replaced_by' in new_property:
                    print(new_property)
                    cell.value = new_property['replaced_by']


def _migrate_process_schema(workbook, schema, schema_version):

    process_tabs = []

    if 'ordering' in CONFIG_FILE:
        if 'ordering' in CONFIG_FILE:
            for key in CONFIG_FILE['ordering'].keys():
                if CONFIG_FILE['ordering'][key] == schema:
                    process_tabs.append(key)

    tab_config = SCHEMA_TEMPLATE.get_tabs_config()

    for schema in tab_config.lookup('tabs'):
        if list(schema.keys())[0] in process_tabs:
            tab_name = schema[list(schema.keys())[0]]['display_name']

            _update_tab(workbook, schema, tab_name, schema_version)


if __name__ == '__main__':

    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    # if '/generator' in dir:
    #     dir = dir.replace('/generator', '')
    # base_uri = dir + "/"


    CONFIG_FILE = _loadConfig('config.ini')

    env = ''
    if 'system' in CONFIG_FILE and 'environment' in CONFIG_FILE['system']:
        env = CONFIG_FILE['system']['environment']
    api_url = INGEST_API_URL.replace("{env}", env)

    SCHEMA_TEMPLATE = SchemaTemplate(ingest_api_url=api_url,migrations_url='https://schema.dev.data.humancellatlas.org/property_migrations')

    app.run(host='0.0.0.0', port=5000)