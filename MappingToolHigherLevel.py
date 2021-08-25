# -*- coding: utf-8 -*-
"""
Created on Thu Jul  8 16:03:59 2021

@author: Stubb
"""

# cursed import strategy
from Resource2WayDiff import *

def add_dummy_parents(resource_dict):
    """
    PARAMETERS:
    resource_dict: dictionary of dictionaries
        Fhir resource in python dictionary form
        
    RETURNS:
        same dictionary with dummy (empty) elements to structure output
    """
    dummy_parents = []
    for k, v in resource_dict.items():
        for i, s in enumerate(k):
            if s == ".":
                dummy_parent = k[:i]
                if dummy_parent not in dummy_parents and (
                        dummy_parent not in resource_dict.keys()):
                    dummy_parents.append(dummy_parent)
    for dummy_parent in dummy_parents:
        resource_dict[dummy_parent] = {"mapping": {"identity": "CDSS5.1",
                                                   "map": "DISPLAY ONLY"}}
    return resource_dict

def get_potential_groupings(resource_name_dicts):
    """
    Parameters
    ----------
    resource_names : list of lists of strings
        should have resource names found for both IGs.

    Returns
    -------
    resources which might be the same (share common words)
    """
    
    alphabet = string.ascii_uppercase
    # gonna use these flags to determine words
    word_flags = alphabet + "-"
    
    # get the unique words out of the reources lists
    word_list = []
    for ig_name, classified_resources in resource_name_dicts.items():
        for classification, resource_names in classified_resources.items():
            for resource_name in resource_names:
                last_flag = 0
                for i, character in enumerate(resource_name):
                    if i > 1:
                        if character in word_flags:
                            word = resource_name[last_flag:i]
                            last_flag = i
                            if word.lower() not in word_list:
                                word_list.append(word.strip("-").lower())
                
                last_word = resource_name[last_flag:]
                if last_word.lower() not in word_list:
                    word_list.append(last_word.strip("-").lower())
    # (the unique part is here)
    word_list = list(set(word_list))
    
    # Now the wobbly part: ligning them up based on containing the same words
    groupings = {word:{"resources": [], "classifications": []}
                 for word in word_list}
    for word in word_list:
        # check for it existing in resources
        for ig_name, classified_resources in resource_name_dicts.items():
            for classification, resource_names in classified_resources.items():
                for resource_name in resource_names:
                    if word.lower() in resource_name.lower():
                        if classification != "shared" or (
                                                resource_name not in
                                                groupings[word]["resources"]):
                            groupings[word]["resources"].append(resource_name)
                            groupings[word]["classifications"].append(
                                                                classification)
    reduced_groupings = {}
    for word, group in groupings.items():
        if len(group["resources"]) > 1:
            if len(set(group["classifications"])) > 1:
                reduced_groupings[word] = group
            
    return reduced_groupings
            
                        


def file_name_to_resource_name(file_name, preamble):
    """
    Parameters
    ----------
    file_name : string
        the file name for the resource.

    Returns
    -------
    The file name with the preamble and extension removed
    Should just be the profile name
    """
    resource_name = file_name
    for word in [preamble, '.json', '.xml']:
        resource_name = resource_name.replace(word, "")
    return resource_name

def get_resources(paths, preambles, ig_names):
    """
    Parameters
    ----------
    paths : list of strings
        file paths to get to the resource folder.
    preambles (technically could be postamble as well): list of strings
        What the filename looks like outside of the resource name.
    ig_names :list of strings
        readable names for the resources.

    Returns
    -------
    list of files in each folder
    """
    
    # list of list of resources (L/R the IGs basically)
    resource_lists = []
    # for each IG
    for i, ig_name in enumerate(ig_names):
        
        # grab the list of files with the preambles
        # should be some clever regex thing, but it isn't
        path = paths[i]
        preamble = preambles[i]
        files = os.listdir(path)
        
        resource_files = [f for f in files if preamble in f]
        resource_names = [file_name_to_resource_name(f, preamble) for
                          f in resource_files]
        resource_lists.append(resource_names)
    return resource_lists
        
def get_classified_resources(resource_lists, ig_names):
    """
    Parameters
    ----------
    resource_lists : list of lists of strings
        resources names broken down by which IG they're in.

    Returns
    -------
    dictionary with resource names and classifications

    """
    # classify the resources
    resource_name_dicts = {ig_name:{"shared": [],
                                    ig_name: []} for ig_name in ig_names}
    
    for i, resource_list in enumerate(resource_lists):
        # need to compare with the other list to see if it's in there
        other_resource_list = resource_lists[(i+1)%2]
        for resource in resource_list:
            if resource in other_resource_list:
                resource_name_dicts[ig_names[i]]["shared"].append(resource)
            else:
                resource_name_dicts[ig_names[i]][ig_names[i]].append(
                                                                resource)
    return resource_name_dicts

def display_resources(resource_lists, known_mappings, output_file, ig_names):
    """
    Parameters
    ----------
    resource_lists : list of 2 lists strings
        names of resources in the respective IGs.
    output_file : string
        Name of excel to output to (MUST INCLUDE DIRECTORY IF NOT PWD).
    ig_names : list of strings
        readable names of IGs.

    Returns
    -------
    None. output to excel file only

    """

    # classify the resources
    resource_name_dicts = {ig_name:{"shared": [],
                                    ig_name: []} for ig_name in ig_names}
    
    for i, resource_list in enumerate(resource_lists):
        # need to compare with the other list to see if it's in there
        other_resource_list = resource_lists[(i+1)%2]
        for resource in resource_list:
            if resource in other_resource_list:
                resource_name_dicts[ig_names[i]]["shared"].append(resource)
            else:
                resource_name_dicts[ig_names[i]][ig_names[i]].append(
                                                                resource)

    
    # using the classification colours from 2 way diff stuff (gross import)
    colours = ["a0c991", "b8c7db"]
    class_colours = {"shared": "ffe9c4",
                     ig_names[0]: colours[0],
                     ig_names[1]: colours[1]
                        }
    white = "ffffff"
    black = "000000"
    
    # start up the excel worksheet
    workbook = pyxl.Workbook()
    worksheet = workbook.active
    
    
    black_border = get_coloured_border(black)
    white_border = get_coloured_border(white)
    
    # Layout is simple L/R with IG names as column headers

    i = 0
    for ig_name, classified_resources in resource_name_dicts.items():
        i += 1
        row = 1
        # getting widest resource name
        width = pl.amax([len(name) for name in classified_resources["shared"]]
                    + [len(name) for name in classified_resources[ig_name]])
        width += 1
        
        # location stuff
        column = pyxl.utils.get_column_letter(i)
        worksheet.column_dimensions[column].width = width
        # get the cell
        cell = worksheet["{0}{1}".format(column, row)]
        # add the IG name at the top
        cell.value = ig_name
        cell.border = black_border
        cell.fill = get_cell_colour(colours[i-1])
        # fill in the resource names (shared first)
        
        for classification, resource_names in classified_resources.items():
            for resource_name in resource_names:
                row += 1
                cell = worksheet["{0}{1}".format(column, row)]
                cell.value = resource_name
                cell.border = white_border
                colour = class_colours[classification]
                cell.fill = get_cell_colour(colour)
            
    
    grouped_resources = get_potential_groupings(resource_name_dicts)

    # put these in the excel sheet beside the other stuff
    i += 2
    column = pyxl.utils.get_column_letter(i)
    row = 1
    cell = worksheet["{0}{1}".format(column, row)]
    cell.value = "POTENTIAL RESOURCE GROUPINGS: Filtered by common words"
    cell.border = black_border
    worksheet.column_dimensions[column].width = 15
    
    for word, group in grouped_resources.items():
        
        column = pyxl.utils.get_column_letter(i)
        row = 2
        width = pl.amax([len(resource_name) for resource_name in
                         group["resources"]]) + 2
        worksheet.column_dimensions[column].width = width
        cell = worksheet["{0}{1}".format(column, row)]
        cell.value = word
        cell.border = black_border
        for j, resource_name in enumerate(group["resources"]):
            classification = group["classifications"][j]
            row += 1
            cell = worksheet["{0}{1}".format(column, row)]
            cell.value = resource_name
            cell.border = white_border
            colour = class_colours[classification]
            cell.fill = get_cell_colour(colour)            
            
        i += 1
        
    i += 1
    column = pyxl.utils.get_column_letter(i)
    row = 1
    cell = worksheet["{0}{1}".format(column, row)]
    cell.value = "KNOWN Mappings"
    cell.border = black_border
    worksheet.column_dimensions[column].width = 15
    
    for word, group in known_mappings.items():
        
        column = pyxl.utils.get_column_letter(i)
        row = 2
        width = pl.amax([len(resource_name) for resource_name in
                         group["resources"]]) + 2
        worksheet.column_dimensions[column].width = width
        cell = worksheet["{0}{1}".format(column, row)]
        cell.value = word
        cell.border = black_border
        for j, resource_name in enumerate(group["resources"]):
            classification = group["classifications"][j]
            row += 1
            cell = worksheet["{0}{1}".format(column, row)]
            cell.value = resource_name
            cell.border = white_border
            colour = class_colours[classification]
            cell.fill = get_cell_colour(colour)            
            
        i += 1
    
    # add legend
    i += 1
    column = column = pyxl.utils.get_column_letter(i)
    cell = worksheet['{}1'.format(column)]
    cell.value = 'LEGEND'
    cell.border = black_border
    worksheet.column_dimensions[column].width = 20
    index = 2
    for k, v in class_colours.items():
        #print(k, v)
        cell = worksheet[column + str(index)]
        cell.value = k
        cell.fill = get_cell_colour(v)
        cell.border = black_border
        index += 1
    
    # freeze the element names and headers
    worksheet.freeze_panes = 'A2'
    
    workbook.save(output_file)
            
    
def display_grouped_elements(groups, meta_data_dict, output_directory,
                             reduce_cds):
    """
    Parameters
    ----------
    groups : Dictionaries of potential (or known) groupings of resources
        has whether it's a shared resource, or what IG it's from
    meta_data_dict: dictionary of dictionaries
        Has the IGs various data :
            path to resources, full name, preamble for resources
    output_directory: string
        folder to put the output in

    Returns
    -------
    None. Output will be to a folder of excel files
    
    THE PLAN:
        for each grouping, smash all of the element names out of all the
        resources in the group into one file.
        
        Elements will be sorted by name (with resource name stripped out),
        but the resource  name will be kept alongside for later
    """
    
    for group_name, group in groups.items():
        #print(group_name, group['resources'])
        combined_element_list = []
        element_dictionaries = {ig: {} for ig in meta_data_dict.keys()}
        for j, resource in enumerate(group["resources"]):
            classification = group["classifications"][j]
            if classification == "shared":
                #print(resource, "is shared!")
                igs = meta_data_dict.keys()
            else:
                igs = [classification]
            
            for ig in igs:
                base_resource_dict = get_base_resource(resource)

                resource_dict = get_resource_dictionary(resource,
                            meta_data_dict[ig]["FullName"], ig,
                            meta_data_dict[ig]["ResourceDirectory"],
                            base_resource_dict,
                            meta_data_dict[ig]["Preamble"],
                            reduce_cds=reduce_cds,
                            views = meta_data_dict[ig]["View"])[0]
                #resource_dict = add_dummy_parents(resource_dict)
                formatted_list =  [[element, 
                                   element.replace(resource + ".",""),
                                   ig, len(element)] for element in
                                   resource_dict.keys()]
                #for element, attributes in resource_dict.items():
                #    if 
                combined_element_list += formatted_list
                
                element_dictionaries[ig][resource] = [
                                        element#.replace(resource + ".","")
                                        for element in resource_dict.keys()]

        combined_element_list = sorted(combined_element_list,
                                       key=operator.itemgetter(3))
        element_dict = {}
        for j, element_info in enumerate(combined_element_list):
            element_name, element_id, ig, length = element_info
            add_element(element_dict, element_name, ig)
        #print(element_dict.keys())
        big_list = list_element_dict(element_dict, [])
        #pp.pprint(big_list)
        combined_element_list = big_list
        # print("\n\n", group_name)
        # pp.pprint(big_list)

        # Shove the stuff into an excel file:
        # Layout:
        #   IPS                 OMD                     Combined
        # Resource 1, 2, ..     resource 1, 2, ...
        # element lists down    element lists down      Big ol combined list
        
        output_file = output_directory + group_name + ".xlsx"
        
        # using the classification colours from 2 way diff stuff (gross import)
        ig_names = [k for k, v in meta_data_dict.items()]
        ig_full_names = [v['FullName'] for k, v in meta_data_dict.items()]
        class_colours = get_colour_dict(ig_names)
        white = "ffffff"
        black = "000000"
        
        # start up the excel worksheet
        workbook = pyxl.Workbook()
        worksheet = workbook.active
        
        
        black_border = get_coloured_border(black)
        white_border = get_coloured_border(white)
        
        
        i = 1
        start_col = 1
        # start with the IG by IG breakdown
        last_ig = "None"
        for ig, element_dict in element_dictionaries.items():
            for resource, elements in element_dict.items():
                row = 2
                column = pyxl.utils.get_column_letter(i)
                
                width = pl.amax([len(element_name) for element_name in
                             elements]) + 2
                worksheet.column_dimensions[column].width = width
                
                cell = worksheet["{0}{1}".format(column, row)]
                cell.value = resource
                cell.border = black_border
                
                cell_colour = get_cell_colour(class_colours[ig + " child"])
                #cell.fill = cell_colour
                
                for element_name in elements:
                    row += 1
                    cell = worksheet["{0}{1}".format(column, row)]
                    cell.value = element_name
                    cell.border = white_border
                    cell.fill = cell_colour
                i += 1
                
            

            cell = worksheet["{0}{1}".format(
                    pyxl.utils.get_column_letter(start_col), 1)]
            cell.value = ig
            cell.border = black_border
            cell.fill = get_cell_colour(class_colours[ig + " child"])
            worksheet.merge_cells(start_row=1, start_column=start_col,
                                  end_row=1, end_column=i-1)
            start_col = i
            last_ig = ig
            
        i += 2
        column = pyxl.utils.get_column_letter(i)
        width = pl.amax([len(e[0]) for e in combined_element_list])
        worksheet.column_dimensions[column].width = width
        shared_reduction = 0
        # now add the big sorted list thing that's surely going to be useless
        for j, element_info in enumerate(combined_element_list):
            element_name, element_class, element_type = element_info

            row = 2 + j
            cell = worksheet["{0}{1}".format(column, row)]
            cell.value = element_name
            cell.border = white_border
            cell_colour = get_cell_colour(class_colours[element_class + " " + 
                                                        element_type])
            cell.fill = cell_colour
            

        worksheet.freeze_panes = 'A2'
    
        workbook.save(output_file)


def add_element(element_dict, element, ig):
    """
    Parameters
    ----------
    element_dict : dictionary of dictionaries of strings
        keys are elements, each element has status (parent/child),
        classification (shared/ig), and children
    element : string
        rlement to be added.
    ig: string.
        ig of origin for the added element

    Returns
    -------
    element dictionary with element added.
    """
    # check against all elements in the dictionary (will go down the tree)
    for k, v in element_dict.items():
        # if the element matches it's a shared element
        if k == element:
            # have to watch out for double dipping
            if v['classification'] != ig:
                v['classification'] = 'shared'
            return element_dict
        # if an existing name is part of the element name
        elif k in element:
            # change the status of the existing element to parent
            v['status'] = 'parent'
            
            
            # add the element as a child of the existing element
            return add_element(v['children'], element, ig)
    # if the element is nowhere in the dictionary add it as an element
    else:
        element_dict[element] = {'status': 'child',
                                 'classification': ig,
                                 'children': {}}
    return element_dict

def list_element_dict(element_dict, element_info_list):
    """
    This function recursively unpacks a resource dictionary into a list
    """
    # for each element in the dictionary
    for k, v in element_dict.items():
        if type(v) != dict:
            print("\n\nI just dont get it\n\n")
            print(k, v)
        if v['status'] == 'child':
            element_info_list += [[k, v['classification'], v['status']]]
        # if it's a parent we add on the children
        else:
            element_info_list += [[k, v['classification'], v['status']]]
            list_element_dict(v['children'],element_info_list)
    return element_info_list

        

def output_diff_from_dicts(profile_name, profile_dicts, ig_full_names, igs,
                                                data_directories,
                                                output_dir, include_mappings,
                                                inherit_base = [True, True],
                                                reduce_cds=True,
                                                add_dummies = False):
    """
    Parameters
    ----------
    profile_name : string
        name of the profile/resource.
    profile_dicts : list of dictionaries
        list containing the resources in dictionary form.
    ig_full_names : list of strings
        full names of the igs (not sure where i still use this), was for
        file names originally
    igs : list of strings
        human readable IG names.
    data_directories : list of strings
        paths to the resources.
    output_dir : string
        output directory for the mapping.
    include_mappings : boolean
        Whether or not to include the mapping attribute
    inherit_base : list of booleans, optional
        Whether or not to inherit the base resource elements.
        The default is [True, True].
    reduce_cds : Boolean, optional
        Whether or not to reduce the CDS to elements only containing Data
        Element Numbers. The default is True.
    add_dummies : boolean, optional
        whether or not to add dummy parent elements for visual purposes.
        The default is False.

    Returns
    -------
    None, Output directly to an excel file

    """
    base_resource_dict = {}
    
    combined_element_list = []
    for i,ig in enumerate(igs):
        resource_dict = profile_dicts[i]
        if add_dummies:
            resource_dict = add_dummy_parents(resource_dict)
        formatted_list =  [[element,
                           ig_full_names[i], len(element)] for element in
                           resource_dict.keys()]

        combined_element_list += formatted_list


    combined_element_list = sorted(combined_element_list,
                                   key=operator.itemgetter(2))
    element_dict = {}
    for j, element_info in enumerate(combined_element_list):
        element_name, ig, length = element_info
        add_element(element_dict, element_name, ig)
    #print(element_dict.keys())
    big_list = list_element_dict(element_dict, [])
    ordered_element_names = []
    element_classifications = []
    for i in range(len(big_list)):
        element_name = big_list[i][0]
        element_classification = big_list[i][1]
        element_status = big_list[i][2]
        ordered_element_names.append(element_name)
        
        element_classification = element_classification + " " + element_status
        element_classifications.append(element_classification)
        

    table = build_dif_table(ordered_element_names, igs, profile_dicts,
                            base_resource_dict, element_classifications, 
                            include_mappings)
    file_name = "{0}{1}.xlsx".format(output_dir, profile_name)
    attributes = ['Mapping']*include_mappings + ['Flags', 'Cardinality',
                                    'Type', 'Binding', 'Slice Description']
    export_excel(table, file_name, attributes)
    format_excel(file_name, element_classifications, table,
                 ig_full_names, attributes)

def grouped_resource_diff(grouped_resources, meta_data_dict, output_dir,
                          reduce_cds, include_mappings=True):
    """

    Returns
    -------
    None.

    THE PLAN:
        The goal is to have an output that runs the 2 way diff stuff with
        the resources which are combined into the Frankenstein resource by the
        grouping.
        
        Might be able to simply build a super dictionary by shoving all of the
        elements from all of the resources for a given IG into one big one.
        Likely naive approach ends up with Many-Repeating elements (will have
            issues with overlapping keys)
        Will need to figure out a way to sort this out:
            Assume / enforce Identical: Pick a winner and remove dupes:
                Looks clean but any over-writing is HORRIBLE
            Shove em all in with added identifiers:
                e.g. will need a new key with profile name in it + add it in
                    e.g. mapping for display purposes
            
            
    The plan almost works, but is ditched in favour of manual mapping since
    most of the time things are not syntactically standardized.
    """
    igs = list(meta_data_dict.keys())
    ig_full_names = [v['FullName'] for k, v in meta_data_dict.items()]
    data_directories = [v['ResourceDirectory'] for k, v in
                        meta_data_dict.items()]
    for group_name, group_dict in grouped_resources.items():
        
        
        combined_resource_dicts = {ig : {} for ig, _ in meta_data_dict.items()}
        for resource, classification in zip(group_dict['resources'],
                                            group_dict['classifications']):
            
            # get the resource in dictionary form
            
            # if it's shared grab it from both IGs
            if classification == "shared":
                relevant_igs = igs
            else:
                relevant_igs = [classification]
            for ig in relevant_igs:
                base_resource_dict = get_base_resource(resource)
                profile_dict_list = get_resource_dictionary(resource,
                                meta_data_dict[ig]["FullName"],
                                ig, meta_data_dict[ig]["ResourceDirectory"],
                                base_resource_dict,
                                meta_data_dict[ig]["Preamble"],
                                reduce_cds, meta_data_dict[ig]["View"])
                
                # Go through the elements and add them to the combined
                # dictionary (HERE IS WHERE THE DETAILS GO)
                profile_dict = profile_dict_list[0]
                for element_name, element_attributes in profile_dict.items():
                    
                    # STARTING WITH SKIPPING (BAD NEWS)
                    if element_name not in combined_resource_dicts[ig].keys():
                        combined_resource_dicts[ig][element_name] = (
                                                            element_attributes)
        combined_resource_list = [combined_resource_dicts[ig] for ig in igs]
        #pp.pprint(combined_resource_list)
        
        output_diff_from_dicts(group_name, combined_resource_list,
                               ig_full_names, igs,
                               data_directories, output_dir,
                               include_mappings)
        
        #elements_list = sorted(combin)
    

def display_manual_diff(group, input_file, output_file, meta_data_dict,
                        include_mappings = True):
    """
    Reads in results of a manual mapping to compare resources which do not
    match, or have elements which are equivalent but do not match
    syntactically.
    """
    igs = [k for k in meta_data_dict.keys()]
    ig_full_names = []
    combined_resource_dicts = {ig : {} for ig, _ in meta_data_dict.items()}
    for resource, classification in zip(group['resources'],
                                        group['classifications']):
        
        # get the resource in dictionary form
        
        # if it's shared grab it from both IGs
        if classification == "shared":
            relevant_igs = igs
        else:
            relevant_igs = [classification]
        for ig in relevant_igs:
            base_resource_dict = get_base_resource(resource)
            profile_dict_list = get_resource_dictionary(resource,
                            meta_data_dict[ig]["FullName"],
                            ig, meta_data_dict[ig]["ResourceDirectory"],
                            base_resource_dict,
                            meta_data_dict[ig]["Preamble"],
                            reduce_cds, meta_data_dict[ig]["View"])
            
            # Go through the elements and add them to the combined
            # dictionary (HERE IS WHERE THE DETAILS GO)
            profile_dict = profile_dict_list[0]
            for element_name, element_attributes in profile_dict.items():
                
                # STARTING WITH SKIPPING (BAD NEWS)
                if element_name not in combined_resource_dicts[ig].keys():
                    combined_resource_dicts[ig][element_name] = (
                                                        element_attributes)
    
    
    workbook = pyxl.load_workbook(filename = input_file)
    worksheet = workbook.active
    alphabet = string.ascii_uppercase
    
    i = 1
    row = 1
    headers = [ig + " Elements" for ig in igs] + ["Reference"]
    #print(headers)
    header_cols = []
    while len(header_cols) < 3:
        column = pyxl.utils.get_column_letter(i)
        cell = worksheet["{0}{1}".format(column, row)]
        if cell.value:
            #print(cell.value)
            value = cell.value
            if value in headers:
                header_cols.append(column)
        i += 1
        if i > 20:
            break
    #print(header_cols)
    # now grab everythnig
    element_dict = {}
    row = 2
    no_more_left = False
    max_row = worksheet.max_row
    while row < max_row:
        row_data = []
        for col in header_cols:
            cell = worksheet["{0}{1}".format(col, row)]
            #row_data.append(cell.value)
            if cell.value:
                row_data.append(cell.value)
            else:
                row_data.append("none")
        #print(row_data)
        # if the mapping is possible (e.g. a valid reference) note it
        if row_data[2].lower() == "yes":
            #print("\n Yo We Found a Doable One:",row_data[0], "\n")
            combined_resource_dicts[igs[1]][row_data[0]] = {"mapping": {
                                                        "identity": "CDSS5.1",
                                                        "map": "Possible"}}
            
        if row_data[0] == "none" and row_data[1] == "none":
            no_more_left = True
            row += 1
            continue
            
        # if the left element exists
        if row_data[0] != "none":
            element_name = row_data[0]
            element_dict[element_name] = {"status": "child",
                                         "classification": igs[0],
                                         "children": {}}
            
            
            if row_data[1] != "none":
                # if the thing next to it is identical its shared 
                if row_data[0] == row_data[1]:
                    element_dict[element_name]["classification"] = "shared"
                else:
                    element_dict[element_name]["status"] = "parent"
                    element_dict[element_name]["children"][row_data[1]] = {
                                                     "status": "child",
                                                     "classification": igs[1],
                                                     "children": {}}
            elif row_data[2].lower() == "yes":
                element_dict[element_name]["classification"] = "shared"
        else:
            if no_more_left:
                element_name = row_data[1]
                element_dict[element_name] = {"status": "child",
                                             "classification": igs[1],
                                             "children": {}}
            else:
                # if the L is empty and the R is not, the previous element is a
                # parent
                element_dict[element_name]["status"] = "parent"
                element_dict[element_name]["children"][row_data[1]] = {
                                                 "status": "child",
                                                 "classification": igs[1],
                                                 "children": {}}
                
        row += 1
    # unfurl into a list of stuff
    #pp.pprint(element_dict)
    big_list = list_element_dict(element_dict, [])
    #pp.pprint(big_list)
    ordered_element_names = []
    element_classifications = []
    for i in range(len(big_list)):
        element_name = big_list[i][0]
        element_classification = big_list[i][1]
        element_status = big_list[i][2]
        ordered_element_names.append(element_name)

        element_classification = element_classification + " " + element_status
        element_classifications.append(element_classification)
                    
    profile_dicts = [v for k, v in combined_resource_dicts.items()]
    base_resource_dict = {}
    table = build_dif_table(ordered_element_names, igs, profile_dicts,
                        base_resource_dict, element_classifications, 
                        include_mappings)
    
    attributes = ['Mapping']*include_mappings + ['Flags', 'Cardinality',
                                    'Type', 'Binding', 'Slice Description']
    export_excel(table, output_file, attributes)
    format_excel(output_file, element_classifications, table,
                 igs, attributes)

##############################################################################
if __name__ == '__main__':
    
    data_dir = "Data/"
    ig_full_names = ['fhir-ips-master', 'OMD-CDS-S']
    igs = ['IPS', 'OMD-CDS-S']
    resource_dirs = [data_dir + ig + '/input/profiles/' for ig in
                                                             ig_full_names]
    resource_dirs[1] = data_dir + 'omd-cdss/'
    
    preambles = ["-uv-ips.structuredefinition", "Profile"]
    views = ["Snapshot", "Diff"]
    meta_data_dict = {ig: {"Preamble": preambles[i],
                           "FullName": ig_full_names[i],
                           "ResourceDirectory": resource_dirs[i],
                           "View": views[i]}
                      for i, ig in enumerate(igs)}
    
    
    
    reduce_cds = True
    
    if reduce_cds:
        output_dir = '{0}Vs{1}-Reduced/'.format(igs[0],igs[1])
    else:
        output_dir = '{0}Vs{1}/'.format(igs[0],igs[1])
    
    if output_dir[:-1] not in os.listdir('Output/'):
        os.mkdir('Output/' + output_dir)
    output_dir = 'Output/' + output_dir
    
    #### RESource level overview stuff - Just looking at what's in either IG
    output_file = output_dir + 'ResourceOverview.xlsx'

    known_mappings = {"DiagnosticReport": {
                        "resources": ["DiagnosticReport", "DocumentManifest"],
                        "classifications": ["shared", igs[1]]}
                      }
    resource_lists = get_resources(resource_dirs, preambles, igs)
    display_resources(resource_lists, known_mappings, output_file, igs)
    
    
    # ELement level comparison - look for potential mappings between groups
    element_comparison_folder = get_folder(output_dir, "ElementComparison/")
    
    resource_name_dicts = get_classified_resources(resource_lists, igs)
    potential_groupings = get_potential_groupings(resource_name_dicts)

    grouped_resources = dict(known_mappings, **potential_groupings)
    
    display_grouped_elements(grouped_resources, meta_data_dict,
                             element_comparison_folder, reduce_cds)
    
    
    # Mapping of grouped elements
    
    # note that resourceManual.xlsx has be reformatted manualy for input into
    # the functions below.
    
    grouped_mapping_folder = get_folder(output_dir, "GroupedMapping/")
    grouped_resource_diff(grouped_resources, meta_data_dict,
                          grouped_mapping_folder, reduce_cds)
    
    
    #########################################################################
    
    # This is a section for manual mapping as input
    # Manual mapping will have to be done following appropriate formatting
    # for any of this to work (See Example On GitHub/Wiki?)
    
    if "medicationManual.xlsx" in os.listdir(output_dir +
                                             "ElementComparison/"):
    
        medication_example = grouped_resources['medication']
        display_manual_diff(medication_example,
                            (output_dir + "ElementComparison/" +
                            "medicationManual.xlsx"),
                            (output_dir + "GroupedMapping/" +
                            "medicationMapped.xlsx"),
                            meta_data_dict)
        
        observation_example = grouped_resources['observation']
        display_manual_diff(observation_example,
                            (output_dir + "ElementComparison/" +
                            "observationManual.xlsx"),
                            (output_dir + "GroupedMapping/" +
                            "observationMapped.xlsx"),
                            meta_data_dict)
    else:
        print("No Manual Mapping Found for medication/observation Profiles")