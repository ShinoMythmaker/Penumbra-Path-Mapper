import tempfile
import shutil
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from race_data import RACES
from penumbra_json import generate_penumbra_json, generate_meta_json, generate_default_mod_json, generate_file_override_json


def clean_mod_name_for_filename(name):
    # Remove unsafe filesystem characters and trim spaces
    return re.sub(r'[^A-Za-z0-9_\- ]+', '', name).strip().replace(' ', '_')

def generate_mod_path(option_name, target_pattern):
    """Generate a unique mod path based on option name and target pattern"""
    # Clean the option name for use in file paths
    clean_option = re.sub(r'[^A-Za-z0-9_\- ]+', '', option_name).strip().replace(' ', '_').lower()
    
    # Replace {race_id} with "race" in the target pattern and use the full path
    pattern_with_race = target_pattern.replace("{race_id}", "race")
    
    # Create the mod path: option_name/full_pattern_path
    mod_path = f"{clean_option}/{pattern_with_race}"
    
    return mod_path

class PenumbraPathMapperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Penumbra Path Mapper")
        self.geometry("1200x850")
        self.create_widgets()

    def create_widgets(self):
        frm = ttk.Frame(self, padding="10")
        frm.pack(fill=tk.BOTH, expand=True)

        row = 0

        # Mod info
        ttk.Label(frm, text="Mod Name:").grid(column=0, row=row, sticky='w')
        self.mod_name_entry = ttk.Entry(frm, width=50)
        self.mod_name_entry.grid(column=1, row=row, sticky='w')
        row += 1

        ttk.Label(frm, text="Author:").grid(column=0, row=row, sticky='w')
        self.author_entry = ttk.Entry(frm, width=50)
        self.author_entry.grid(column=1, row=row, sticky='w')
        self.author_entry.insert(0, "Penumbra Path Mapper")
        row += 1

        ttk.Label(frm, text="Description:").grid(column=0, row=row, sticky='w')
        self.desc_entry = ttk.Entry(frm, width=50)
        self.desc_entry.grid(column=1, row=row, sticky='w')
        self.desc_entry.insert(0, "Mod for Penumbra")
        row += 1

        ttk.Label(frm, text="Website:").grid(column=0, row=row, sticky='w')
        self.website_entry = ttk.Entry(frm, width=50)
        self.website_entry.grid(column=1, row=row, sticky='w')
        self.website_entry.insert(0, "https://github.com/ShinoMythmaker/Penumbra-Path-Mapper")
        row += 1

        ttk.Label(frm, text="Version:").grid(column=0, row=row, sticky='w')
        self.version_entry = ttk.Entry(frm, width=20)
        self.version_entry.grid(column=1, row=row, sticky='w')
        self.version_entry.insert(0, "1.0.0")
        row += 1

        # Operations section with tabs
        ttk.Label(frm, text="Operations:").grid(column=0, row=row, sticky='nw')
        operations_frame = ttk.Frame(frm)
        operations_frame.grid(column=1, row=row, sticky='ew', pady=10)
        
        # Create notebook for tabs with larger height
        self.operations_notebook = ttk.Notebook(operations_frame)
        self.operations_notebook.pack(fill='both', expand=True)
        
        # Set minimum height for the operations area
        operations_frame.configure(height=600)
        operations_frame.pack_propagate(False)
        
        # Add operation button
        add_button_frame = ttk.Frame(operations_frame)
        add_button_frame.pack(fill='x', pady=(5, 0))
        ttk.Button(add_button_frame, text="+ Add File Redirection Operation", 
                  command=self.add_file_redirection_tab).pack(side='left')
        ttk.Button(add_button_frame, text="+ Add File Override Operation", 
                  command=self.add_file_override_tab).pack(side='left', padx=(10, 0))
        
        # Store operation tabs
        self.operation_tabs = []
        
        row += 1

        # Output directory
        ttk.Label(frm, text="Output Directory:").grid(column=0, row=row, sticky='w')
        self.output_dir = tk.StringVar()
        self.output_dir.set(".")
        ttk.Entry(frm, textvariable=self.output_dir, width=45).grid(column=1, row=row, sticky='w')
        ttk.Button(frm, text="Browse", command=self.browse_output_dir).grid(column=2, row=row, sticky="w")
        row += 1

        # Generate button
        ttk.Button(frm, text="Generate Full Mod", command=self.generate_full_mod).grid(column=1, row=row, pady=20)

        frm.columnconfigure(1, weight=1)

    def browse_output_dir(self):
        dirname = filedialog.askdirectory()
        if dirname:
            self.output_dir.set(dirname)
    
    def add_file_redirection_tab(self):
        """Add a new file redirection operation tab"""
        tab_number = len(self.operation_tabs) + 1
        tab_name = f"Redirection {tab_number}"
        
        # Create tab frame
        tab_frame = ttk.Frame(self.operations_notebook)
        self.operations_notebook.add(tab_frame, text=tab_name)
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Bind canvas resize to update scrollable frame width
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create the file redirection operation UI
        tab_data = self.create_file_redirection_operation(scrollable_frame, tab_number)
        tab_data['frame'] = tab_frame
        tab_data['name'] = tab_name
        tab_data['type'] = 'file_redirection'
        
        self.operation_tabs.append(tab_data)
        
        # Select the new tab
        self.operations_notebook.select(tab_frame)
    
    def add_file_override_tab(self):
        """Add a new file override operation tab"""
        tab_number = len(self.operation_tabs) + 1
        tab_name = f"Override {tab_number}"
        
        # Create tab frame
        tab_frame = ttk.Frame(self.operations_notebook)
        self.operations_notebook.add(tab_frame, text=tab_name)
        
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # Bind canvas resize to update scrollable frame width
        def configure_canvas_width(event):
            canvas.itemconfig(canvas_window, width=event.width)
        
        canvas.bind('<Configure>', configure_canvas_width)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Create the file override operation UI
        tab_data = self.create_file_override_operation(scrollable_frame, tab_number)
        tab_data['frame'] = tab_frame
        tab_data['name'] = tab_name
        tab_data['type'] = 'file_override'
        
        self.operation_tabs.append(tab_data)
        
        # Select the new tab
        self.operations_notebook.select(tab_frame)
    
    def create_file_redirection_operation(self, parent, tab_number):
        """Create the UI for a file redirection operation"""
        row = 0
        
        # Tab header with close button
        header_frame = ttk.Frame(parent)
        header_frame.grid(column=0, row=row, columnspan=2, sticky='ew', pady=(0, 10))
        ttk.Label(header_frame, text=f"File Redirection Operation {tab_number}", 
                 font=('TkDefaultFont', 10, 'bold')).pack(side='left')
        ttk.Button(header_frame, text="×", width=3, 
                  command=lambda: self.close_tab(tab_number-1)).pack(side='right')
        row += 1
        
        # Path patterns
        ttk.Label(parent, text="File Path Patterns (one per line):").grid(column=0, row=row, sticky='nw')
        path_patterns_text = tk.Text(parent, height=6, width=70)
        path_patterns_text.grid(column=1, row=row, sticky='ew', pady=(0, 10))
        path_patterns_text.insert("1.0", "chara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_loop.pap\nchara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_start.pap")
        row += 1

        # Variants
        ttk.Label(parent, text="Number of Variants:").grid(column=0, row=row, sticky='w')
        variant_count_entry = ttk.Entry(parent, width=10)
        variant_count_entry.grid(column=1, row=row, sticky='w', pady=(0, 5))
        variant_count_entry.insert(0, "4")
        row += 1

        # Group Name
        ttk.Label(parent, text="Group Name:").grid(column=0, row=row, sticky='w')
        group_name_entry = ttk.Entry(parent, width=20)
        group_name_entry.grid(column=1, row=row, sticky='w', pady=(0, 10))
        group_name_entry.insert(0, f"operation{tab_number}")
        row += 1

        # APPLIED TO RACES SECTION
        ttk.Label(parent, text="Applied to (files in your mod):").grid(column=0, row=row, sticky='nw', columnspan=2)
        row += 1

        # Applied to Gender Selection
        ttk.Label(parent, text="Applied to Genders:").grid(column=0, row=row, sticky='w')
        source_gender_frame = ttk.Frame(parent)
        source_gender_frame.grid(column=1, row=row, sticky='w')
        source_include_male = tk.BooleanVar(value=True)
        source_include_female = tk.BooleanVar(value=True)
        ttk.Checkbutton(source_gender_frame, text="Male", variable=source_include_male).pack(side='left')
        ttk.Checkbutton(source_gender_frame, text="Female", variable=source_include_female).pack(side='left', padx=(10, 0))
        row += 1

        # Applied to Race Selection
        ttk.Label(parent, text="Applied to Races:").grid(column=0, row=row, sticky='nw')
        source_race_frame = ttk.Frame(parent)
        source_race_frame.grid(column=1, row=row, sticky='ew', pady=(0, 5))
        
        # Create checkboxes for each applied to race
        source_race_vars = {}
        race_names = ["Midlander", "Highlander", "Elezen", "Miqo'te", "Roegadyn", "Lalafell", "Au Ra", "Hrothgar", "Viera"]
        
        # Add Select All / Deselect All buttons for applied to races
        source_button_frame = ttk.Frame(source_race_frame)
        source_button_frame.pack(fill='x', pady=(0, 5))
        ttk.Button(source_button_frame, text="Select All", 
                  command=lambda: self.select_all_races_in_tab(source_race_vars)).pack(side='left')
        ttk.Button(source_button_frame, text="Deselect All", 
                  command=lambda: self.deselect_all_races_in_tab(source_race_vars)).pack(side='left', padx=(5, 0))
        
        # Create applied to race checkboxes in a grid
        source_race_grid_frame = ttk.Frame(source_race_frame)
        source_race_grid_frame.pack(fill='both', expand=True)
        
        for i, race in enumerate(race_names):
            source_race_vars[race] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(source_race_grid_frame, text=race, variable=source_race_vars[race])
            cb.grid(row=i//3, column=i%3, sticky='w', padx=(0, 10), pady=2)
        
        source_race_grid_frame.columnconfigure(0, weight=1)
        source_race_grid_frame.columnconfigure(1, weight=1)
        source_race_grid_frame.columnconfigure(2, weight=1)
        row += 1

        # Separator
        ttk.Separator(parent, orient='horizontal').grid(column=0, row=row, columnspan=2, sticky='ew', pady=10)
        row += 1

        # OPTIONS SECTION
        ttk.Label(parent, text="Options (choices for players):").grid(column=0, row=row, sticky='nw', columnspan=2)
        row += 1

        # Options Gender Selection
        ttk.Label(parent, text="Options Genders:").grid(column=0, row=row, sticky='w')
        target_gender_frame = ttk.Frame(parent)
        target_gender_frame.grid(column=1, row=row, sticky='w')
        target_include_male = tk.BooleanVar(value=True)
        target_include_female = tk.BooleanVar(value=True)
        ttk.Checkbutton(target_gender_frame, text="Male", variable=target_include_male).pack(side='left')
        ttk.Checkbutton(target_gender_frame, text="Female", variable=target_include_female).pack(side='left', padx=(10, 0))
        row += 1

        # Options Race Selection
        ttk.Label(parent, text="Options Races:").grid(column=0, row=row, sticky='nw')
        target_race_frame = ttk.Frame(parent)
        target_race_frame.grid(column=1, row=row, sticky='ew')
        
        # Create checkboxes for each options race
        target_race_vars = {}
        
        # Add Select All / Deselect All buttons for options races
        target_button_frame = ttk.Frame(target_race_frame)
        target_button_frame.pack(fill='x', pady=(0, 5))
        ttk.Button(target_button_frame, text="Select All", 
                  command=lambda: self.select_all_races_in_tab(target_race_vars)).pack(side='left')
        ttk.Button(target_button_frame, text="Deselect All", 
                  command=lambda: self.deselect_all_races_in_tab(target_race_vars)).pack(side='left', padx=(5, 0))
        
        # Create options race checkboxes in a grid
        target_race_grid_frame = ttk.Frame(target_race_frame)
        target_race_grid_frame.pack(fill='both', expand=True)
        
        for i, race in enumerate(race_names):
            target_race_vars[race] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(target_race_grid_frame, text=race, variable=target_race_vars[race])
            cb.grid(row=i//3, column=i%3, sticky='w', padx=(0, 10), pady=2)
        
        target_race_grid_frame.columnconfigure(0, weight=1)
        target_race_grid_frame.columnconfigure(1, weight=1)
        target_race_grid_frame.columnconfigure(2, weight=1)
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
        
        return {
            'path_patterns_text': path_patterns_text,
            'variant_count_entry': variant_count_entry,
            'group_name_entry': group_name_entry,
            'source_include_male': source_include_male,
            'source_include_female': source_include_female,
            'source_race_vars': source_race_vars,
            'target_include_male': target_include_male,
            'target_include_female': target_include_female,
            'target_race_vars': target_race_vars
        }
    
    def create_file_override_operation(self, parent, tab_number):
        """Create the UI for a file override operation"""
        row = 0
        
        # Tab header with close button
        header_frame = ttk.Frame(parent)
        header_frame.grid(column=0, row=row, columnspan=2, sticky='ew', pady=(0, 10))
        ttk.Label(header_frame, text=f"File Override Operation {tab_number}", 
                 font=('TkDefaultFont', 10, 'bold')).pack(side='left')
        ttk.Button(header_frame, text="×", width=3, 
                  command=lambda: self.close_tab(tab_number-1)).pack(side='right')
        row += 1

        # Group Name
        ttk.Label(parent, text="Group Name:").grid(column=0, row=row, sticky='w')
        group_name_entry = ttk.Entry(parent, width=20)
        group_name_entry.grid(column=1, row=row, sticky='w', pady=(0, 10))
        group_name_entry.insert(0, f"override{tab_number}")
        row += 1

        # OPTIONS SECTION
        ttk.Label(parent, text="Options:").grid(column=0, row=row, sticky='nw', columnspan=2, pady=(0, 5))
        row += 1
        
        # Options container
        options_frame = ttk.Frame(parent)
        options_frame.grid(column=0, row=row, columnspan=2, sticky='ew', pady=(0, 10))
        
        # Store options data
        options_data = []
        
        # Add first option by default
        option_data = self.create_file_override_option(options_frame, 1, options_data)
        options_data.append(option_data)
        
        # Add option button
        add_option_frame = ttk.Frame(options_frame)
        add_option_frame.pack(fill='x', pady=(5, 0))
        ttk.Button(add_option_frame, text="+ Add Option", 
                  command=lambda: self.add_file_override_option(options_frame, options_data)).pack(side='left')
        
        row += 1

        # Separator
        ttk.Separator(parent, orient='horizontal').grid(column=0, row=row, columnspan=2, sticky='ew', pady=10)
        row += 1

        # APPLIED TO RACES SECTION
        ttk.Label(parent, text="Applied to (races that get this override):").grid(column=0, row=row, sticky='nw', columnspan=2)
        row += 1

        # Applied to Gender Selection
        ttk.Label(parent, text="Applied to Genders:").grid(column=0, row=row, sticky='w')
        applied_gender_frame = ttk.Frame(parent)
        applied_gender_frame.grid(column=1, row=row, sticky='w')
        applied_include_male = tk.BooleanVar(value=True)
        applied_include_female = tk.BooleanVar(value=True)
        ttk.Checkbutton(applied_gender_frame, text="Male", variable=applied_include_male).pack(side='left')
        ttk.Checkbutton(applied_gender_frame, text="Female", variable=applied_include_female).pack(side='left', padx=(10, 0))
        row += 1

        # Applied to Race Selection
        ttk.Label(parent, text="Applied to Races:").grid(column=0, row=row, sticky='nw')
        applied_race_frame = ttk.Frame(parent)
        applied_race_frame.grid(column=1, row=row, sticky='ew')
        
        # Create checkboxes for each applied to race
        applied_race_vars = {}
        race_names = ["Midlander", "Highlander", "Elezen", "Miqo'te", "Roegadyn", "Lalafell", "Au Ra", "Hrothgar", "Viera"]
        
        # Add Select All / Deselect All buttons
        applied_button_frame = ttk.Frame(applied_race_frame)
        applied_button_frame.pack(fill='x', pady=(0, 5))
        ttk.Button(applied_button_frame, text="Select All", 
                  command=lambda: self.select_all_races_in_tab(applied_race_vars)).pack(side='left')
        ttk.Button(applied_button_frame, text="Deselect All", 
                  command=lambda: self.deselect_all_races_in_tab(applied_race_vars)).pack(side='left', padx=(5, 0))
        
        # Create applied to race checkboxes in a grid
        applied_race_grid_frame = ttk.Frame(applied_race_frame)
        applied_race_grid_frame.pack(fill='both', expand=True)
        
        for i, race in enumerate(race_names):
            applied_race_vars[race] = tk.BooleanVar(value=True)
            cb = ttk.Checkbutton(applied_race_grid_frame, text=race, variable=applied_race_vars[race])
            cb.grid(row=i//3, column=i%3, sticky='w', padx=(0, 10), pady=2)
        
        applied_race_grid_frame.columnconfigure(0, weight=1)
        applied_race_grid_frame.columnconfigure(1, weight=1)
        applied_race_grid_frame.columnconfigure(2, weight=1)
        
        # Configure column weights
        parent.columnconfigure(1, weight=1)
        
        return {
            'group_name_entry': group_name_entry,
            'options_data': options_data,
            'options_frame': options_frame,
            'applied_include_male': applied_include_male,
            'applied_include_female': applied_include_female,
            'applied_race_vars': applied_race_vars
        }
    
    def create_file_override_option(self, parent, option_number, options_data):
        """Create a single file override option"""
        option_frame = ttk.LabelFrame(parent, text=f"Option {option_number}", padding="10")
        option_frame.pack(fill='x', pady=(0, 10))
        
        row = 0
        
        # Option name
        ttk.Label(option_frame, text="Option Name:").grid(column=0, row=row, sticky='w')
        option_name_entry = ttk.Entry(option_frame, width=30)
        option_name_entry.grid(column=1, row=row, sticky='w', pady=(0, 10))
        option_name_entry.insert(0, f"Option {option_number}")
        row += 1
        
        # File patterns section
        ttk.Label(option_frame, text="File/Pattern Pairs:").grid(column=0, row=row, sticky='nw', columnspan=3)
        row += 1
        
        # File patterns container
        file_patterns_frame = ttk.Frame(option_frame)
        file_patterns_frame.grid(column=0, row=row, columnspan=3, sticky='ew', pady=(0, 10))
        
        # Store file pattern data
        file_patterns_data = []
        
        # Add first file pattern by default
        pattern_data = self.create_file_pattern_pair(file_patterns_frame, 1, file_patterns_data, option_name_entry)
        file_patterns_data.append(pattern_data)
        
        # Add file pattern button
        add_pattern_frame = ttk.Frame(file_patterns_frame)
        add_pattern_frame.pack(fill='x', pady=(5, 0))
        ttk.Button(add_pattern_frame, text="+ Add File/Pattern Pair", 
                  command=lambda: self.add_file_pattern_pair(file_patterns_frame, file_patterns_data, option_name_entry)).pack(side='left')
        
        # Remove option button
        remove_button_frame = ttk.Frame(option_frame)
        remove_button_frame.grid(column=2, row=0, sticky='e')
        ttk.Button(remove_button_frame, text="Remove Option", 
                  command=lambda: self.remove_file_override_option(parent, option_frame, options_data)).pack()
        
        option_frame.columnconfigure(1, weight=1)
        
        return {
            'frame': option_frame,
            'option_name_entry': option_name_entry,
            'file_patterns_data': file_patterns_data,
            'file_patterns_frame': file_patterns_frame,
            'option_number': option_number
        }
    
    def create_file_pattern_pair(self, parent, pair_number, file_patterns_data, option_name_entry=None):
        """Create a file/pattern pair"""
        pair_frame = ttk.Frame(parent)
        pair_frame.pack(fill='x', pady=(0, 5))
        
        # Local file
        ttk.Label(pair_frame, text=f"File {pair_number}:").grid(column=0, row=0, sticky='w')
        local_file_var = tk.StringVar()
        local_file_entry = ttk.Entry(pair_frame, textvariable=local_file_var, width=40)
        local_file_entry.grid(column=1, row=0, sticky='ew', padx=(5, 0))
        ttk.Button(pair_frame, text="Browse", 
                  command=lambda: self.browse_local_file(local_file_var)).grid(column=2, row=0, padx=(5, 0))
        
        # Target pattern
        ttk.Label(pair_frame, text="Target Pattern:").grid(column=0, row=1, sticky='w')
        target_pattern_entry = ttk.Entry(pair_frame, width=50)
        target_pattern_entry.grid(column=1, row=1, columnspan=2, sticky='ew', padx=(5, 0), pady=(2, 0))
        # Make each file/pattern pair unique by including the pair number
        default_pattern = f"chara/human/{{race_id}}/animation/a0001/bt_common/emote/s_pose{pair_number:02d}_loop.pap"
        target_pattern_entry.insert(0, default_pattern)
        
        # Auto-generated mod path (read-only display)
        ttk.Label(pair_frame, text="Auto Mod Path:").grid(column=0, row=2, sticky='w')
        mod_path_var = tk.StringVar()
        mod_path_label = ttk.Label(pair_frame, textvariable=mod_path_var, width=50, 
                                  relief="sunken", background="white", foreground="gray")
        mod_path_label.grid(column=1, row=2, columnspan=2, sticky='ew', padx=(5, 0), pady=(2, 0))
        
        # Function to update mod path when option name or target pattern changes
        def update_mod_path():
            try:
                if option_name_entry:
                    option_name = option_name_entry.get().strip() or "option"
                    target_pattern = target_pattern_entry.get().strip()
                    
                    if target_pattern:
                        mod_path = generate_mod_path(option_name, target_pattern)
                        mod_path_var.set(mod_path)
                    else:
                        mod_path_var.set("")
            except Exception as e:
                # Silently handle any widget access errors
                pass
        
        # Bind events to update mod path automatically
        if option_name_entry:
            option_name_entry.bind('<KeyRelease>', lambda e: update_mod_path())
        target_pattern_entry.bind('<KeyRelease>', lambda e: update_mod_path())
        
        # Initialize mod path
        update_mod_path()
        
        # Remove button
        ttk.Button(pair_frame, text="Remove", 
                  command=lambda: self.remove_file_pattern_pair(parent, pair_frame, file_patterns_data)).grid(column=3, row=0, rowspan=3, padx=(5, 0))
        
        pair_frame.columnconfigure(1, weight=1)
        
        return {
            'frame': pair_frame,
            'local_file_var': local_file_var,
            'mod_path_var': mod_path_var,
            'target_pattern_entry': target_pattern_entry,
            'update_mod_path': update_mod_path
        }
    
    def add_file_override_option(self, parent, options_data):
        """Add a new file override option"""
        option_number = len(options_data) + 1
        option_data = self.create_file_override_option(parent, option_number, options_data)
        options_data.append(option_data)
        
        # Move the add button to the bottom
        for child in parent.winfo_children():
            if isinstance(child, ttk.Frame) and any(isinstance(grandchild, ttk.Button) and grandchild.cget('text') == '+ Add Option' for grandchild in child.winfo_children()):
                child.pack_forget()
                child.pack(fill='x', pady=(5, 0))
                break
    
    def remove_file_override_option(self, parent, option_frame, options_data):
        """Remove a file override option"""
        # Find and remove from options_data
        for i, option_data in enumerate(options_data):
            if option_data['frame'] == option_frame:
                options_data.pop(i)
                break
        
        # Destroy the frame
        option_frame.destroy()
        
        # Renumber remaining options
        for i, option_data in enumerate(options_data):
            option_data['option_number'] = i + 1
            option_data['frame'].configure(text=f"Option {i + 1}")
            option_data['option_name_entry'].delete(0, tk.END)
            option_data['option_name_entry'].insert(0, f"Option {i + 1}")
    
    def add_file_pattern_pair(self, parent, file_patterns_data, option_name_entry=None):
        """Add a new file/pattern pair"""
        pair_number = len(file_patterns_data) + 1
        pattern_data = self.create_file_pattern_pair(parent, pair_number, file_patterns_data, option_name_entry)
        file_patterns_data.append(pattern_data)
        
        # Move the add button to the bottom
        for child in parent.winfo_children():
            if isinstance(child, ttk.Frame) and any(isinstance(grandchild, ttk.Button) and grandchild.cget('text') == '+ Add File/Pattern Pair' for grandchild in child.winfo_children()):
                child.pack_forget()
                child.pack(fill='x', pady=(5, 0))
                break
    
    def remove_file_pattern_pair(self, parent, pair_frame, file_patterns_data):
        """Remove a file/pattern pair"""
        # Find and remove from file_patterns_data
        for i, pattern_data in enumerate(file_patterns_data):
            if pattern_data['frame'] == pair_frame:
                file_patterns_data.pop(i)
                break
        
        # Destroy the frame
        pair_frame.destroy()
        
        # Renumber remaining pairs
        for i, pattern_data in enumerate(file_patterns_data):
            pair_frame = pattern_data['frame']
            # Update the label for the first row
            for child in pair_frame.winfo_children():
                if isinstance(child, ttk.Label) and child.cget('text').startswith('File'):
                    child.configure(text=f"File {i + 1}:")
                    break
    
    def browse_local_file(self, file_var):
        """Browse for a local file to include in the mod"""
        filename = filedialog.askopenfilename(
            title="Select file to include in mod",
            filetypes=[
                ("All files", "*.*"),
                ("Animation files", "*.pap"),
                ("Texture files", "*.tex"),
                ("Model files", "*.mdl"),
                ("Material files", "*.mtrl")
            ]
        )
        if filename:
            file_var.set(filename)
    
    def close_tab(self, tab_index):
        """Close a specific operation tab"""
        if 0 <= tab_index < len(self.operation_tabs):
            tab_data = self.operation_tabs[tab_index]
            self.operations_notebook.forget(tab_data['frame'])
            self.operation_tabs.pop(tab_index)
            
            # Update tab numbers for each operation type
            redirection_count = 1
            override_count = 1
            
            for i, tab in enumerate(self.operation_tabs):
                if tab['type'] == 'file_redirection':
                    new_name = f"Redirection {redirection_count}"
                    self.operations_notebook.tab(tab['frame'], text=new_name)
                    tab['name'] = new_name
                    redirection_count += 1
                elif tab['type'] == 'file_override':
                    new_name = f"Override {override_count}"
                    self.operations_notebook.tab(tab['frame'], text=new_name)
                    tab['name'] = new_name
                    override_count += 1
    
    def select_all_races_in_tab(self, race_vars):
        """Select all races in a specific tab"""
        for var in race_vars.values():
            var.set(True)
    
    def deselect_all_races_in_tab(self, race_vars):
        """Deselect all races in a specific tab"""
        for var in race_vars.values():
            var.set(False)
    
    def generate_full_mod(self):
        # Gather mod metadata
        mod_name = self.mod_name_entry.get().strip()
        author = self.author_entry.get().strip()
        desc = self.desc_entry.get().strip()
        website = self.website_entry.get().strip()
        version = self.version_entry.get().strip() or "1.0.0"
        out_dir = self.output_dir.get()

        if not all([mod_name, author, desc, version]):
            messagebox.showerror("Error", "Please fill out all mod information fields.")
            return

        if not self.operation_tabs:
            messagebox.showerror("Error", "Please add at least one operation.")
            return

        # Validate all operations
        for i, tab_data in enumerate(self.operation_tabs):
            if not self.validate_operation(tab_data, i + 1):
                return

        # Use a temporary directory for packaging
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write meta.json
            meta = generate_meta_json(mod_name, author, desc, version, website)
            with open(os.path.join(temp_dir, "meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=4)

            # Write default_mod.json
            default_mod = generate_default_mod_json()
            with open(os.path.join(temp_dir, "default_mod.json"), "w", encoding="utf-8") as f:
                json.dump(default_mod, f, indent=4)

            # Process each operation and track generated files for renaming
            generated_files = []
            for tab_data in self.operation_tabs:
                if tab_data['type'] == 'file_redirection':
                    files = self.process_file_redirection_operation(tab_data, temp_dir)
                    generated_files.extend(files)
                elif tab_data['type'] == 'file_override':
                    files = self.process_file_override_operation(tab_data, temp_dir)
                    generated_files.extend(files)

            # Rename files with group IDs
            self.add_group_ids_to_files(temp_dir, generated_files)

            # Zip the files, then rename to .pmp
            mod_safe_name = clean_mod_name_for_filename(mod_name)
            zip_path = os.path.join(out_dir, f"{mod_safe_name}.zip")
            pmp_path = os.path.join(out_dir, f"{mod_safe_name}.pmp")
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', temp_dir)
            if os.path.exists(pmp_path):
                os.remove(pmp_path)
            os.rename(zip_path, pmp_path)

        messagebox.showinfo("Success", f"Generated Penumbra mod package: {pmp_path}")
    
    def validate_operation(self, tab_data, tab_number):
        """Validate a single operation tab"""
        if tab_data['type'] == 'file_redirection':
            patterns_raw = tab_data['path_patterns_text'].get("1.0", "end").strip()
            patterns = [p.strip() for p in patterns_raw.splitlines() if p.strip()]
            variant_count_str = tab_data['variant_count_entry'].get()
            group_name = tab_data['group_name_entry'].get().strip()

            # Get source and target race/gender selections
            source_include_male = tab_data['source_include_male'].get()
            source_include_female = tab_data['source_include_female'].get()
            source_selected_races = [race for race, var in tab_data['source_race_vars'].items() if var.get()]
            
            target_include_male = tab_data['target_include_male'].get()
            target_include_female = tab_data['target_include_female'].get()
            target_selected_races = [race for race, var in tab_data['target_race_vars'].items() if var.get()]

            if not all([patterns, variant_count_str, group_name]):
                messagebox.showerror("Error", f"Please fill out all fields in operation {tab_number}.")
                return False

            if not source_include_male and not source_include_female:
                messagebox.showerror("Error", f"At least one 'Applied to' gender must be selected in operation {tab_number}.")
                return False

            if not target_include_male and not target_include_female:
                messagebox.showerror("Error", f"At least one 'Options' gender must be selected in operation {tab_number}.")
                return False

            if not source_selected_races:
                messagebox.showerror("Error", f"At least one 'Applied to' race must be selected in operation {tab_number}.")
                return False

            if not target_selected_races:
                messagebox.showerror("Error", f"At least one 'Options' race must be selected in operation {tab_number}.")
                return False

            try:
                variant_count = int(variant_count_str)
                if variant_count < 1:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", f"Number of Variants must be a positive integer in operation {tab_number}.")
                return False

            # Create source races dictionary (files that exist in the mod)
            source_races = {}
            for race in source_selected_races:
                if source_include_male and f"{race} M" in RACES:
                    source_races[f"{race} M"] = RACES[f"{race} M"]
                if source_include_female and f"{race} F" in RACES:
                    source_races[f"{race} F"] = RACES[f"{race} F"]

            # Create target races dictionary (choices for players)
            target_races = {}
            for race in target_selected_races:
                if target_include_male and f"{race} M" in RACES:
                    target_races[f"{race} M"] = RACES[f"{race} M"]
                if target_include_female and f"{race} F" in RACES:
                    target_races[f"{race} F"] = RACES[f"{race} F"]

            if not source_races:
                messagebox.showerror("Error", f"No valid 'Applied to' race/gender combinations found in operation {tab_number}.")
                return False

            if not target_races:
                messagebox.showerror("Error", f"No valid 'Options' race/gender combinations found in operation {tab_number}.")
                return False

        elif tab_data['type'] == 'file_override':
            group_name = tab_data['group_name_entry'].get().strip()
            options_data = tab_data['options_data']

            if not group_name:
                messagebox.showerror("Error", f"Please provide a group name for operation {tab_number}.")
                return False

            if not options_data:
                messagebox.showerror("Error", f"Please add at least one option in operation {tab_number}.")
                return False

            # Validate each option
            for j, option_data in enumerate(options_data):
                option_name = option_data['option_name_entry'].get().strip()
                file_patterns_data = option_data['file_patterns_data']

                if not option_name:
                    messagebox.showerror("Error", f"Please provide a name for option {j+1} in operation {tab_number}.")
                    return False

                if not file_patterns_data:
                    messagebox.showerror("Error", f"Please add at least one file/pattern pair for option {j+1} in operation {tab_number}.")
                    return False

                # Validate each file/pattern pair
                for k, pattern_data in enumerate(file_patterns_data):
                    try:
                        local_file = pattern_data['local_file_var'].get().strip()
                        mod_path = pattern_data['mod_path_var'].get().strip()
                        target_pattern = pattern_data['target_pattern_entry'].get().strip()
                    except tk.TclError:
                        # Widget was destroyed, skip this entry
                        continue

                    if not all([local_file, mod_path, target_pattern]):
                        messagebox.showerror("Error", f"Please fill out all fields for file/pattern pair {k+1} in option {j+1} of operation {tab_number}.")
                        return False

                    if not os.path.exists(local_file):
                        messagebox.showerror("Error", f"Local file does not exist: {local_file}")
                        return False

            # Get applied to race/gender selections
            applied_include_male = tab_data['applied_include_male'].get()
            applied_include_female = tab_data['applied_include_female'].get()
            applied_selected_races = [race for race, var in tab_data['applied_race_vars'].items() if var.get()]

            if not applied_include_male and not applied_include_female:
                messagebox.showerror("Error", f"At least one 'Applied to' gender must be selected in operation {tab_number}.")
                return False

            if not applied_selected_races:
                messagebox.showerror("Error", f"At least one 'Applied to' race must be selected in operation {tab_number}.")
                return False

        return True
    
    def process_file_redirection_operation(self, tab_data, temp_dir):
        """Process a file redirection operation and write JSON files"""
        patterns_raw = tab_data['path_patterns_text'].get("1.0", "end").strip()
        patterns = [p.strip() for p in patterns_raw.splitlines() if p.strip()]
        variant_count = int(tab_data['variant_count_entry'].get())
        group_name = tab_data['group_name_entry'].get().strip()

        # Get source and target race/gender selections
        source_include_male = tab_data['source_include_male'].get()
        source_include_female = tab_data['source_include_female'].get()
        source_selected_races = [race for race, var in tab_data['source_race_vars'].items() if var.get()]
        
        target_include_male = tab_data['target_include_male'].get()
        target_include_female = tab_data['target_include_female'].get()
        target_selected_races = [race for race, var in tab_data['target_race_vars'].items() if var.get()]

        # Create source races dictionary
        source_races = {}
        for race in source_selected_races:
            if source_include_male and f"{race} M" in RACES:
                source_races[f"{race} M"] = RACES[f"{race} M"]
            if source_include_female and f"{race} F" in RACES:
                source_races[f"{race} F"] = RACES[f"{race} F"]

        # Create target races dictionary
        target_races = {}
        for race in target_selected_races:
            if target_include_male and f"{race} M" in RACES:
                target_races[f"{race} M"] = RACES[f"{race} M"]
            if target_include_female and f"{race} F" in RACES:
                target_races[f"{race} F"] = RACES[f"{race} F"]

        # Write variant JSONs for this operation and track generated files
        generated_files = []
        for i in range(1, variant_count + 1):
            variant = f"{i:02}"
            json_obj, file_name = generate_penumbra_json(patterns, variant, group_name, source_races, target_races)
            out_path = os.path.join(temp_dir, f"group_{group_name}{variant}.json")
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(json_obj, f, indent=2)
            
            generated_files.append({
                'file_path': out_path,
                'group_name': group_name,
                'variant': variant
            })
        
        return generated_files
    
    def process_file_override_operation(self, tab_data, temp_dir):
        """Process a file override operation and write JSON files"""
        group_name = tab_data['group_name_entry'].get().strip()
        options_data = tab_data['options_data']

        # Get applied to race/gender selections
        applied_include_male = tab_data['applied_include_male'].get()
        applied_include_female = tab_data['applied_include_female'].get()
        applied_selected_races = [race for race, var in tab_data['applied_race_vars'].items() if var.get()]

        # Create applied to races dictionary
        applied_races = {}
        for race in applied_selected_races:
            if applied_include_male and f"{race} M" in RACES:
                applied_races[f"{race} M"] = RACES[f"{race} M"]
            if applied_include_female and f"{race} F" in RACES:
                applied_races[f"{race} F"] = RACES[f"{race} F"]

        # Collect all options for this single group
        all_options_data = []
        
        for option_data in options_data:
            option_name = option_data['option_name_entry'].get().strip()
            file_patterns_data = option_data['file_patterns_data']
            
            # Copy all files for this option and collect file mappings
            files_mapping = []
            for pattern_data in file_patterns_data:
                try:
                    # Get widget values
                    local_file = pattern_data['local_file_var'].get().strip()
                    target_pattern = pattern_data['target_pattern_entry'].get().strip()
                    
                    # Force update the mod path before collecting
                    pattern_data['update_mod_path']()
                    mod_path = pattern_data['mod_path_var'].get().strip()
                    
                except tk.TclError:
                    # Widget was destroyed, skip this entry
                    continue
                except Exception:
                    # Handle any other widget access errors
                    continue

                if not local_file or not target_pattern:
                    continue

                # Copy the local file to the mod directory
                mod_file_path = os.path.join(temp_dir, mod_path)
                try:
                    os.makedirs(os.path.dirname(mod_file_path), exist_ok=True)
                    shutil.copy2(local_file, mod_file_path)
                except Exception:
                    continue
                
                files_mapping.append({
                    'mod_path': mod_path,
                    'target_pattern': target_pattern
                })
            
            # Add this option to the collection
            all_options_data.append({
                'option_name': option_name,
                'files_mapping': files_mapping
            })

        # Generate a single JSON file for all options in this group
        json_obj, file_name = generate_file_override_json(
            all_options_data, 
            group_name, 
            applied_races
        )
        
        out_path = os.path.join(temp_dir, f"group_{group_name}.json")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(json_obj, f, indent=2)
        
        # Return single file info
        generated_files = [{
            'file_path': out_path,
            'group_name': group_name,
            'variant': None  # No variants for file override operations
        }]
        
        return generated_files

    def add_group_ids_to_files(self, temp_dir, generated_files):
        """Add group IDs to generated JSON files"""
        # Group files by their base group name
        groups = {}
        for file_info in generated_files:
            group_name = file_info['group_name']
            if group_name not in groups:
                groups[group_name] = []
            groups[group_name].append(file_info)
        
        # Assign group IDs and rename files
        group_id = 1
        for group_name, files in groups.items():
            group_id_str = f"{group_id:03d}"  # Zero-padded 3 digits
            
            for file_info in files:
                old_path = file_info['file_path']
                old_filename = os.path.basename(old_path)
                
                # Create new filename with group ID in lowercase
                # Example: group_operation01.json -> group_001_operation01.json
                if old_filename.startswith("group_"):
                    new_filename = old_filename.replace("group_", f"group_{group_id_str}_", 1).lower()
                    new_path = os.path.join(temp_dir, new_filename)
                    
                    # Rename the file
                    os.rename(old_path, new_path)
            
            group_id += 1

if __name__ == "__main__":
    app = PenumbraPathMapperApp()
    app.mainloop()