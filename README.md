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
cd generator/
python template_generator_app.py
```

Alternatively, you can build and run the app with docker. To run the web application with docker for build the docker image with

```
docker build . -t generator-demo:latest
```

then run the docker container. You will need to provide the URL to the [ingestion API](https://github.com/HumanCellAtlas/ingest-core)

```
docker run -p 5000:5000 -e INGEST_API=http://localhost:8080 generator-demo:latest
```

The application will be available at <http://localhost:5000>


# Repo set-up

## Directories

### Root directory

- [README.md](README.md) 
- [HowTo.md](HowTo.md) - describes common use cases
- [requirements.txt](requirements.txt) - Python install requirements
- [Dockerfile][Dockerfile] - Docker build config

### `generator` directory

- [config.ini][config.ini] - some basic config such as tab ordering for the spreadsheet and default linking behaviour
- [template_generator_app.py](template_generator_app.py) - the main Python app that drives the generator

#### `templates` directory

Contains the html templates for the generator UI

- [base.html](.html) - Header and footer for the entire UI
- [index.html](.html) - Core element of the landing page, imports base
- [schema_properties.html](.html) - Wrapper for a set of schema properties
- [schema_selector.html](.html) - Selector page for pre-selecting schemas and modules
- [schemas.html](.html) - Full schema selection page, imports base and schema_properties


#### `static` directory

Includes css, images and js (javascript) directories and their contents

- CSS - a few customised elements including some imports from Bootstrap 4 that were needed even though Bootstrap 4 isn't currently compatible with the UI overall
- JS - mostly boilerplate plus a few customised elements

# Known bugs and unexpected behaviours

The following is a list of known bugs and unexpected behaviours of the spreadsheet template generator.

1. **Numeric fields and their units aren't pre-selected together:** Fields currently don't depend on each other so without an additional layer of hard-coding, it would be difficult to ensure that numeric fields and their units are pre-selected together. Review these selections carefully in the schema selection page.

1. **The field ordering in my YAML file changed after I uploaded it to add additional schemas:** This is a known issue with the field selection UI. To preserve the ordering of the fields in your YAML, edit it manually and generate the spreadsheet using the fourth option on the UI landing page. For more information, see Use case #4 in [the HowTo doc](HowTo.md).

1. **New required fields are not added as part of a spreadsheet migration:** This was a deliberate design choice. For more information, see Use case #5 in [the HowTo doc](HowTo.md).

1. **Tabs are not renamed as part of a spreadsheet migration:** Renaming of spreadsheet tabs isn't picked up during a migration. This includes child tabs such as "Contacts" or "Publications" - check them if they did not already conform to the new format of "Parent name - Child name"!

1. **Migration code inelegance:** Due to the way the spreadsheet migration is implemented, a section of the ingest-client spreadsheet generator code had to be replicated in the template generator. This has the potential to lead to discrepancies between the two implementations. It may be worth re-implementing the migration to first build a full spreadsheet for the latest schemas from scratch, then copy across the values from the old spreadsheet column by column using migration lookups.

