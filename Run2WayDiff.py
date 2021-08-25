# -*- coding: utf-8 -*-
"""
Created on Sun Jun 27 20:00:19 2021

@author: GarrettStubbings (on github)
"""

# highly cursed and illegal import strategy
from Resource2WayDiff import *
from MappingToolHigherLevel import *

if __name__ == '__main__':
    
    
    data_dir = "Data/"
    
    ig_full_names = ['fhir-ips-master', 'OMD-CDS-S']
    igs = ['IPS', 'OMD-CDS-S']
    
    # resource directories
    # Probably need to be changed depending on where your data is
    resource_dirs = ["Data/fhir-ips-master/input/profiles/", #ips
                     "Data/omd-cdss/"]  # cdss
    
    
    
    reduce_cds = True
    if reduce_cds:
        output_dir = '{0}Vs{1}-Reduced/'.format(igs[0],igs[1])
    else:
        output_dir = '{0}Vs{1}/'.format(igs[0],igs[1])
    
    # make the output directory
    if output_dir[:-1] not in os.listdir('Output/'):
        os.mkdir('Output/' + output_dir)
    output_dir = 'Output/' + output_dir
    
    extension = "DirectResourceMapping/"
    if extension[:-1] not in os.listdir(output_dir):
        os.mkdir(output_dir + extension)
    output_dir += extension
    
    files = os.listdir(resource_dirs[1])
    
    # US-Core Preamble
    # preamble = 'StructureDefinition-us-core-'
    
    
    # PREAMBLE: the stuff in the file name that isn't the profile name
    #     EXAMPLE:    ProfileName(preambles).extension
    preambles = ["-uv-ips.structuredefinition", "Profile"]
    preamble = preambles[1]
    
    # Note that the OMD resources DO NOT inherit from the base resource
    # the "Diff" Is supposed to fully represent the resource
    # NOTE that the list is flipped because the comparison is "against" the
    # other implementation guide / base resource
    inherit_base = [True, False][::-1]
    views = ['Snapshot', "Diff"]
    # Adding dummies shows parent elements even if they arent present
    add_dummies = True
    # include mappings shows mappings  (DE Numbers in CDSS)
    include_mappings = 1
    # Go over all the files in the data directory
    for f in files:
        #print(f)
        if 'StructureDefinition' in f or 'OMD' in igs[1]:
            if preamble not in f:
                continue
            profile_name = f.replace(preamble,"").replace('.json','')
            print(profile_name)
            
            # Get the base FHIR Resource for Inheritance
            base_resource_dict = get_base_resource(profile_name)
            if base_resource_dict == "DNE":
                continue
            
            # Get the profiles in dictionary form
            profile_dicts = get_resource_dictionary(profile_name,
                            ig_full_names, igs, resource_dirs,
                            base_resource_dict, preambles,
                            views = views)
            # Output the 2-way diff
            output_diff_from_dicts(profile_name, profile_dicts, ig_full_names,
                                   igs, resource_dirs, output_dir,
                                   include_mappings, add_dummies = add_dummies)
            
            # THe old way of outputting the diffs
            """
            
            create_2_way_diff(profile_name, ig_full_names, igs,
                              resource_dirs, output_dir, 
                              include_mappings,
                              preambles,
                              inherit_base = inherit_base,
                              reduce_cds=reduce_cds,
                              views=views)
            """