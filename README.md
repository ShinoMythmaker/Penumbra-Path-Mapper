# Penumbra Path Mapper

A comprehensive GUI tool for FFXIV modders to create complete Penumbra mod packages (.pmp files) with automatic file redirection across races and genders.

## What is this?

The Penumbra Path Mapper simplifies the process of creating FFXIV mods that work across multiple races and genders. Instead of manually creating complex JSON files for each race combination, this tool automatically generates all the necessary Penumbra configuration files based on your input patterns.

## Key Features

- **Complete Mod Package Generation**: Creates ready-to-install .pmp files with all necessary metadata
- **Flexible Race/Gender Selection**: Separate "Applied to" and "Options" configurations
- **Pattern-Based File Mapping**: Use `{race_id}` and `{variant}` placeholders in file paths
- **Multiple Variants Support**: Generate multiple variations of the same mod in one package
- **Cross-Platform GUI**: Built with Python + Tkinter for easy use on any platform

## How It Works

### Applied to vs Options

- **Applied to**: Which races/genders your mod files are designed for (the source files)
- **Options**: Which races/genders players can choose from in Penumbra (the target options)

This separation allows you to create mods with files for specific races but offer them as options for different races.

### Example Scenario

Let's say you have sitting animation files for **Midlander Female** and **Au Ra Female**, but you want players to be able to apply these animations to **all female races**:

1. **Applied to**: Select "Female" gender and "Midlander", "Au Ra" races
2. **Options**: Select "Female" gender and all races you want to offer
3. **File Pattern**: `chara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_loop.pap`

The tool will generate options where:
- "Viera F" option redirects Midlander F files → Viera F paths, Au Ra F files → Viera F paths
- "Miqo'te F" option redirects Midlander F files → Miqo'te F paths, Au Ra F files → Miqo'te F paths
- And so on for each selected race

## Usage

1. **Install Requirements**: Python 3.x (Tkinter is included by default)
2. **Run the Application**: `python3 main.py`
3. **Fill in Mod Information**:
   - Mod Name, Author, Description, Website, Version
4. **Configure File Patterns**:
   - Enter file path patterns using `{race_id}` and `{variant}` placeholders
   - Set number of variants (e.g., 4 for pose01, pose02, pose03, pose04)
   - Set group name for organization
5. **Select Applied to Races**: Choose which races/genders your mod files target
6. **Select Options**: Choose which races/genders players can select in Penumbra
7. **Generate**: Click "Generate Full Mod" to create your .pmp file

## File Pattern Examples

### Animation Files
```
chara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_loop.pap
chara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_start.pap
```

## Output

The tool generates a complete Penumbra mod package (.pmp file) containing:
- `meta.json`: Mod metadata (name, author, description, etc.)
- `default_mod.json`: Default mod configuration
- `group_[name][variant].json`: Configuration files for each variant with race redirection options

## Race IDs Reference

The tool supports all FFXIV races:
- Midlander M/F: c0101/c0201
- Highlander M/F: c0301/c0401  
- Elezen M/F: c0501/c0601
- Miqo'te M/F: c0701/c0801
- Roegadyn M/F: c0901/c1001
- Lalafell M/F: c1101/c1201
- Au Ra M/F: c1301/c1401
- Hrothgar M/F: c1501/c1601
- Viera M/F: c1701/c1801

## Requirements

- Python 3.x
- No additional packages required (uses standard library only)

## Installation

1. Clone or download this repository
2. Ensure Python 3.x is installed
3. Run `python main.py`

---

**Perfect for**: Animation modders, equipment modders, hair modders, or anyone creating FFXIV mods that need to work across multiple races and genders.

**Contributions welcome!**