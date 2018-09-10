import json
import urllib

BASE_URL = "http://schema.{schema_env}.humancellatlas.org/"



def retrieve_latest_schemas(schemas_url, schema_env):

    urls = []

    with urllib.request.urlopen(schemas_url) as url:
        schemas = json.loads(url.read().decode())

        for schema in schemas["_embedded"]["schemas"]:
            schema_url = BASE_URL.replace("{schema_env}", schema_env)

            if schema["highLevelEntity"] and schema["highLevelEntity"] == "type":
                if "analysis_" not in schema["concreteEntity"]:
                    schema_url = schema_url + schema["highLevelEntity"]
                    if schema["domainEntity"]:
                        schema_url = schema_url + "/" + schema["domainEntity"]
                    if schema["subDomainEntity"] and schema["subDomainEntity"] != "":
                        schema_url = schema_url + "/" + schema["subDomainEntity"]
                    if schema["schemaVersion"]:
                        schema_url = schema_url + "/" + schema["schemaVersion"]
                    if schema["concreteEntity"]:
                        schema_url = schema_url + "/" + schema["concreteEntity"]

                    urls.append(schema_url)

        if "_links" in schemas and "next" in schemas["_links"]:
            more_urls = retrieve_latest_schemas(schemas["_links"]["next"]["href"], schema_env)

            urls.extend(more_urls)

    return urls


def load_schema(url):
    with urllib.request.urlopen(url) as encoded_url:
        schema = json.loads(encoded_url.read().decode())

    return schema
