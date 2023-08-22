# d3b-tiru-flywheel-code-repo

This repo is intended to be a resource for code examples using the Flywheel SDK.

Available scripts are organized into the following directories:

| Directory Name      | Description |
| ----------- | ----------- |
| collections | collection-level operations |
| dataviews | using Flywheel DataViews to get project/file metadata with SQL-like query |
| delete | deleting operations (tread with caution!) |
| file_classifications | updating or adding [Flywheel classifications](https://docs.flywheel.io/hc/en-us/articles/360007560934-Data-Classification) |
| files | file-level operations |
| gears | all things gear related (e.g., queing jobs, downloading output files) |
| other | miscellaneous operations |
| projects | project-level operations |
| upload-download | uploading and downloading data |
| users | user-level operations |

## Additional resources
- [Flywheel SDK Documentation](https://flywheel-io.gitlab.io/product/backend/sdk/branches/master/python/index.html)

## Script examples
1. upload-download/download-acq-file.py : Code to download flywheel acquisition files
2. dataviews/fw_project_data.py:  Code gives a dataview (csv) extract of subjects,sessions and all v2 projects on flywheel.
3. files/rename_file.py: Code renames a acquisition file based on user input.

## Other notes
- DataViews can be a powerful tool for loading info into a pandas DataFrame and filtering to specific fields of-interest (e.g., instead of looping through all subject/sessions/files in a project, can narrow down to specific subjects or files, for example, and then only continue processing those)