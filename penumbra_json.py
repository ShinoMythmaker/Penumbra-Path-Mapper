def generate_penumbra_json(patterns, variant, group_name, source_races, target_races):
    """
    patterns: list of file path patterns with {race_id} and {variant}
    variant: string, zero-padded like '01', '02', etc.
    group_name: user-specified group name for the file and JSON "Name"
    source_races: dict of {race_name: race_id} - races that the mod files are applied to
    target_races: dict of {race_name: race_id} - races that players can choose as options
    Returns: (json_dict, filename_without_extension)
    """
    def substitute_variant(path):
        return path.replace("{variant}", variant)

    options = []
    
    # Add default "No Changes" option first
    default_option = {
        "Name": "Off",
        "Description": "Keep original game files unchanged",
        "Priority": 0,
        "Files": {},
        "FileSwaps": {},
        "Manipulations": []
    }
    options.append(default_option)
    
    # Add race-specific options
    for target_race, target_id in target_races.items():
        file_swaps = {}
        for pattern in patterns:
            for source_race, source_id in source_races.items():
                src = substitute_variant(pattern.replace("{race_id}", source_id))
                tgt = substitute_variant(pattern.replace("{race_id}", target_id))
                file_swaps[src] = tgt
        option = {
            "Name": target_race,
            "Description": "",
            "Priority": 0,
            "Files": {},
            "FileSwaps": file_swaps,
            "Manipulations": []
        }
        options.append(option)

    json_name = f"{group_name}{variant}"
    return ({
        "Version": 0,
        "Name": json_name,
        "Description": "",
        "Image": "",
        "Page": 0,
        "Priority": 0,
        "Type": "Single",
        "DefaultSettings": 1,
        "Options": options
    }, json_name)

def generate_file_override_json(all_options_data, group_name, applied_races):
    """
    all_options_data: list of dicts with 'option_name' and 'files_mapping' keys
    group_name: user-specified group name for the file and JSON "Name"
    applied_races: dict of {race_name: race_id} - races that this override applies to
    Returns: (json_dict, filename_without_extension)
    """
    def substitute_variant(path):
        return path.replace("{variant}", "")

    options = []
    
    # Create default "No Changes" option first
    default_option = {
        "Name": "Off",
        "Description": "Keep original game files unchanged",
        "Priority": 0,
        "Files": {},
        "FileSwaps": {},
        "Manipulations": []
    }
    options.append(default_option)
    
    # Create user-defined options
    for option_data in all_options_data:
        option_name = option_data['option_name']
        files_mapping = option_data['files_mapping']
        
        # Create the option with file overrides
        files = {}
        for race_name, race_id in applied_races.items():
            for file_mapping in files_mapping:
                target_pattern = file_mapping['target_pattern']
                mod_path = file_mapping['mod_path']
                target_path = substitute_variant(target_pattern.replace("{race_id}", race_id))
                files[target_path] = mod_path
        
        user_option = {
            "Name": option_name,
            "Description": "",
            "Priority": 0,
            "Files": files,
            "FileSwaps": {},
            "Manipulations": []
        }
        options.append(user_option)

    json_name = group_name
    return ({
        "Version": 0,
        "Name": json_name,
        "Description": "",
        "Image": "",
        "Page": 0,
        "Priority": 0,
        "Type": "Single",
        "DefaultSettings": 1,
        "Options": options
    }, json_name)

def generate_meta_json(name, author, description, version, website):
    return {
        "FileVersion": 3,
        "Name": name,
        "Author": author,
        "Description": description,
        "Version": version,
        "Website": website,
        "ModTags": []
    }

def generate_default_mod_json():
    return {
        "Files": {},
        "FileSwaps": {},
        "Manipulations": [],
        "Name": "",
        "Description": "",
        "Priority": 0
    }