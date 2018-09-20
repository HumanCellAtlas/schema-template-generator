
from utils import schema_loader

EXCLUDED_PROPERTIES = ["describedBy", "schema_version", "schema_type", "provenance"]


def extract_properties(schema):
    title = schema["title"]

    schema_id = ''
    if "$id" in schema:
        schema_id = schema["$id"]
    elif "id" in schema:
        schema_id = schema["id"]

    schema_type = ''

    if "type" in schema_id:
        schema_type = "type"
    elif "core" in schema_id:
        schema_type = "core"
    elif "module" in schema_id:
        schema_type = "module"

    required = []
    if "required" in schema and schema_type != "module":
        required = schema["required"]

    if "name" in schema:
        name = schema["name"]
    else:
        name = title

    properties = schema["properties"]

    props = {}
    props["title"] = title
    props["name"] = name

    prop_pairs = {}

    for property in properties:
        if property not in EXCLUDED_PROPERTIES:
            path = name + "." + property
            if "$ref" in properties[property]:
                ref = properties[property]["$ref"]
                ref_schema = schema_loader.load_schema(ref)
                ref_props = extract_properties(ref_schema)

                for key in ref_props["properties"].keys():
                    val = ref_props["properties"][key]
                    els = key.split(".")
                    newKey = path + "." + ".".join(els[1:])
                    prop_pairs[newKey] = val

            elif "items" in properties[property] and "$ref" in properties[property]["items"]:
                ref = properties[property]["items"]["$ref"]
                ref_schema = schema_loader.load_schema(ref)
                ref_props = extract_properties(ref_schema)

                if "_ontology" in ref:
                    for key in ref_props["properties"].keys():
                        val = ref_props["properties"][key]
                        els = key.split(".")
                        newKey = path + "." + ".".join(els[1:])
                        prop_pairs[newKey] = val
                else:
                    standAlone = {}
                    ref_pairs = {}
                    for key in ref_props["properties"].keys():
                        val = ref_props["properties"][key]
                        els = key.split(".")
                        newKey = path + "." + ".".join(els[1:])
                        ref_pairs[newKey] = val
                    standAlone["properties"] = ref_pairs
                    standAlone["title"] = ref_props["title"]
                    standAlone["name"] = ref_props["name"]

                    if "stand_alone" not in props:
                        props["stand_alone"] = []
                    props["stand_alone"].append(standAlone)

            else:
                if property in required:
                    prop_pairs[path] = "required"
                else:
                    prop_pairs[path] = "not required"

    props["properties"] = prop_pairs
    return props



def extract_references(schema):
    properties = schema["properties"]

    title = schema["title"]
    if "name" in schema:
        name = schema["name"]
    else:
        name = title

    required = []
    if "required" in schema:
        required = schema["required"]

    structure = {}
    structure["title"] = title
    structure["name"] = name

    references = {}
    for property in properties:
        if property not in EXCLUDED_PROPERTIES:
            if "$ref" in properties[property]:
                if property in required:
                    references[property] = "required"
                else:
                    references[property] = "not required"

    structure["references"] = references
    return structure




