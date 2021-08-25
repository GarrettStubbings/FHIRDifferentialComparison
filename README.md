# FHIRDifferentialComparison
This project contains code used for comparing the resources/profiles from 2 different FHIR IGs. The main focus is to outline where one IG is more or less constraining than the other on an element-by-element basis.

# Additional Python Package Requirements
There are a handful of packages that will need to be installed, probably. xlsxwriter, openpyxl, json, xmltodict, and pprint probably arent on the base installation of python. You can install them with pip or whatever package manager works.

# Running an Example
After downloading the project (including the massive data folder) it should be ready to go.

Running the python scripts in the projects directory (Run2WayDiff.py and MappingToolHigherLevel.py are the ones with output) will generate the excel files you see in the output folder. Spyder works fine for this, just open them and press run.

To check that it's working you could delete some of the outputs and check that running it re-generates it. Alternatively you could remake the output folder (just save the current output folder as something else, then make a new empty output folder) and run everything again.
NOTE: There are 2 files (medicationmanual and observationmanual) in the element comparison folder which are required to generate those mappings. The first time you run the MappingToolHigherLevel script it will say something like Missing manual mappings, you will have to copy those manual mappings into the element comparison folder if you want those to work.
  
