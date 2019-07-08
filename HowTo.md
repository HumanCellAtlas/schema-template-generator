# How to use the HCA spreadsheet template generator

This guide presents the use cases addressed by the spreadsheet template generator. It assumes that you have the spreadsheet generator interface up and running. For information on how to start up the UI locally, see the [Read Me](README.md).

## Use case 1: Generate a spreadsheet or YAML file from all the available metadata schemas

This is the original use case the template generator was designed for. From the UI landing page, select the first option, "Load all schemas". You will be presented with a full list of all available metadata schemas and for each schema, all available fields. You can expand and collapse section as required, and select fields, as well as add new fields using the correct dot notation (eg schema_name.field_name or schema_name.wrapper_name.field_name).

Some fields are pre-selected in each schema and cannot be unselected - these are the required fields for that schema. A schema is only selected for inclusion in the output file if the checkbox at the top of the schema is ticked.

*Top tip*: if you need to select a lot of fields in a large schema, it may be easier to first tick all the fields in the schema via the "Select all fields in this section" button, then unselecting the ones you don't need!

Once you have completed your selection, use the appropriate download button at the bottom of the page to generate either a YAML or a spreadsheet file. You can also use the buttons consecutively to generate both files.

## Use case 2: Preselect metadata schemas to generate a spreadsheet or YAML file

If you already know which schemas you will need and want to avoid the hassle of having to select fields one by one, you can pre-select metadata schemas via the second option on the UI landing page. Once you have selected your relevant schemas and sub-schemas, the system will take you through to the same full schema page as for use case 1. Review your pre-selected schemas to make sure nothing is missing and generate your output files the same as in use case #1.

## Use case 3: Update an existing YAML file with additional metadata fields or schemas

If you have an existing YAML file that you need to add further fields or schemas to and that you don't want to hand-edit, you can upload the file using option 3 on the UI landing page. This will pre-populate the fields from your original YAML file in the all-schemas page. Select (or unselect!) fields and schemas as required, then generate a new YAML file or spreadsheet.


## Use case 4: Generate a spreadsheet from an existing YAML file

You can use the fourth option on the UI landing page to convert a YAML file to a spreadsheet without going via the field selection screen.

The driving use case for this option was the inability to change the ordering of fields in schemas in any of the previous three options. If you need any fields (eg linking IDs) to be in a particular position in your YAML file or spreadsheet tab, the easiest option is to manually move them around in the YAML file in a text editor your choice, then generate your spreadsheet from the updated YAML file using the direct YAML to spreadsheet option.


## Use case 5: Migrate an existing spreadsheet to the latest schema version

If you have a metadata spreadsheet, with or without data, that doesn't conform to the latest schema version, you can automatically have it updated using the fifth option on the UI landing page. Simply upload your spreadsheet and generator will use schema migrations and field by field comparisons to update both programmatic field names and user-friendly fields such as name and description.

***Important note***: The migration use case currently doesn't support the addition of new required fields, even though these are collected in the schema migrations document. If any of the schemas in your spreadsheet have been updated with a new required property, you will have to add this to your spreadsheet manually.

The reason for this design choice was that it is actually very difficult to identify new required properties, even using the migrations look-up, as identifying migrations is predicated around lookup existing properties and finding that they have changed, either through renaming, moving or deleting. In order to identify a new property, a careful field-by-field comparison of all properties in a spreadsheet to properties in the latest schemas would be necessary, followed by a further exclusion of previously existing properties that simply weren't included in the spreadsheet for other reasons.

In addition, required fields obviously have to be filled in order to pass validation. It was therefore deemed simpler for these to be added manually by a wrangler than programmatically.

