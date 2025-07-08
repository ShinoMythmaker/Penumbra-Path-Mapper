def generate_penumbra_json(patterns, variant, group_name, races):
    """
    patterns: list of file path patterns with {race_id} and {variant}
    variant: string, zero-padded like '01', '02', etc.
    group_name: user-specified group name for the file and JSON "Name"
    races: dict of {race_name: race_id}
    Returns: (json_dict, filename_without_extension)
    """
    def substitute_variant(path):
        return path.replace("{variant}", variant)

    options = []
    for target_race, target_id in races.items():
        file_swaps = {}
        for pattern in patterns:
            for source_race, source_id in races.items():
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
        "Type": "Multi",
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