Project Plan: FFXIV Penumbra Mass Redirect Generator

Purpose:
GUI tool to generate Penumbra multi-group mod JSONs for mass file redirection, using file path templates and a fixed race list.
Summary of Functionality

    Input:
        File path pattern (with {race_id} and {filename} placeholders)
        Target filename (e.g., s_pose02_loop.pap)
        (Optional: other filenames for batch mode)
    Output:
        For each filename, a JSON structured as you provided, with all race options and proper file swaps.
    Race IDs:
        Fixed list (to be defined in the code/config)
    GUI:
        Simple desktop app (cross-platform)
        Fields for path pattern, filename, and race selection