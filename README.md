# FHIRDifferentialComparison
This project contains code used for comparing the resources/profiles from 2 different FHIR IGs. The main focus is to outline where one IG is more or less constraining than the other on an element-by-element basis.

# Scripts

Run2WayDiff.py does the direct resource mapping, it looks for resources which are in both IGs (it will replace one with a base FHIR resource if the other is missing, and the base resource exists).
MappingToolHigherLevel adds some functionality for including manually mapped elements which combine multiple resources, which can get pretty wobbly.

The scripts are a mess and borrow functions from one-another.

# Additional Python Package Requirements
There are a handful of packages that will need to be installed, probably. xlsxwriter, openpyxl, json, xmltodict, and pprint probably arent on the base installation of python. You can install them with pip or whatever package manager works.

# Running an Example
After downloading the project (including the massive data folder) it should be ready to go.

Running the python scripts in the projects directory (Run2WayDiff.py and MappingToolHigherLevel.py are the ones with output) will generate the excel files you see in the output folder. Spyder works fine for this, just open them and press run.

To check that it's working you could delete some of the outputs and check that running it re-generates it. Alternatively you could remake the output folder (just save the current output folder as something else, then make a new empty output folder) and run everything again.
NOTE: There are 2 files (medicationmanual and observationmanual) in the element comparison folder which are required to generate those mappings. The first time you run the MappingToolHigherLevel script it will say something like Missing manual mappings, you will have to copy those manual mappings into the element comparison folder if you want those to work.
  
# Applying to other IGs
To get other IGs running you will have to go into the script and change the paths to the resources and the IG names (e.g. something like Data/CA-Baseline/Input/Resources/). You will also have to change how the files are named (e.g. files could be "structuredefinition-profile-PROFILENAME.json", so preamble would be "structuredefinition-profile-". This will be up to you to figure out given how your data is downloaded/stored.

# Options
You can chose to show elements from the snapshot or not by changing the view for the relevant IG (there's a list called views that has elements either "Snapshot" or "Diff"). There's also an option to add dummy parent elements (boolean called add_dummies) which will fill in some of the hierarchy (e.g. if only medication.code.coding.code is in diff, it will show medication.code.coding and medication.code as parents in the output despite them not being in the Diff).
