import tempfile
import shutil
import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
from race_data import RACES
from penumbra_json import generate_penumbra_json, generate_meta_json, generate_default_mod_json


def clean_mod_name_for_filename(name):
    # Remove unsafe filesystem characters and trim spaces
    return re.sub(r'[^A-Za-z0-9_\- ]+', '', name).strip().replace(' ', '_')

class PenumbraPathMapperApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Penumbra Path Mapper")
        self.geometry("750x750")
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
        row += 1

        ttk.Label(frm, text="Description:").grid(column=0, row=row, sticky='w')
        self.desc_entry = ttk.Entry(frm, width=50)
        self.desc_entry.grid(column=1, row=row, sticky='w')
        row += 1

        ttk.Label(frm, text="Website:").grid(column=0, row=row, sticky='w')
        self.website_entry = ttk.Entry(frm, width=50)
        self.website_entry.grid(column=1, row=row, sticky='w')
        row += 1

        ttk.Label(frm, text="Version:").grid(column=0, row=row, sticky='w')
        self.version_entry = ttk.Entry(frm, width=20)
        self.version_entry.grid(column=1, row=row, sticky='w')
        self.version_entry.insert(0, "1.0.0")
        row += 1

        # Path patterns
        ttk.Label(frm, text="File Path Patterns (one per line):").grid(column=0, row=row, sticky='nw')
        self.path_patterns_text = tk.Text(frm, height=8, width=70)
        self.path_patterns_text.grid(column=1, row=row, sticky='ew')
        self.path_patterns_text.insert("1.0", "chara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_loop.pap\nchara/human/{race_id}/animation/a0001/bt_common/emote/s_pose{variant}_start.pap")
        row += 1

        # Variants
        ttk.Label(frm, text="Number of Variants:").grid(column=0, row=row, sticky='w')
        self.variant_count_entry = ttk.Entry(frm, width=10)
        self.variant_count_entry.grid(column=1, row=row, sticky='w')
        self.variant_count_entry.insert(0, "4")
        row += 1

        # Group Name
        ttk.Label(frm, text="Group Name:").grid(column=0, row=row, sticky='w')
        self.group_name_entry = ttk.Entry(frm, width=20)
        self.group_name_entry.grid(column=1, row=row, sticky='w')
        self.group_name_entry.insert(0, "sit")
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
    
    def generate_full_mod(self):
        # Gather all values (same as before)
        mod_name = self.mod_name_entry.get().strip()
        author = self.author_entry.get().strip()
        desc = self.desc_entry.get().strip()
        website = self.website_entry.get().strip()
        version = self.version_entry.get().strip() or "1.0.0"
        patterns_raw = self.path_patterns_text.get("1.0", "end").strip()
        patterns = [p.strip() for p in patterns_raw.splitlines() if p.strip()]
        variant_count_str = self.variant_count_entry.get()
        group_name = self.group_name_entry.get().strip()
        out_dir = self.output_dir.get()

        if not all([mod_name, author, desc, version, patterns, variant_count_str, group_name]):
            messagebox.showerror("Error", "Please fill out all fields.")
            return

        try:
            variant_count = int(variant_count_str)
            if variant_count < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error", "Number of Variants must be a positive integer.")
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

            # Write all variant JSONs
            for i in range(1, variant_count + 1):
                variant = f"{i:02}"
                json_obj, file_name = generate_penumbra_json(patterns, variant, group_name, RACES)
                out_path = os.path.join(temp_dir, f"group_{group_name}{variant}.json")
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(json_obj, f, indent=2)

            # Zip the files, then rename to .pmp
            mod_safe_name = clean_mod_name_for_filename(mod_name)
            zip_path = os.path.join(out_dir, f"{mod_safe_name}.zip")
            pmp_path = os.path.join(out_dir, f"{mod_safe_name}.pmp")
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', temp_dir)
            if os.path.exists(pmp_path):
                os.remove(pmp_path)
            os.rename(zip_path, pmp_path)

        messagebox.showinfo("Success", f"Generated Penumbra mod package: {pmp_path}")

if __name__ == "__main__":
    app = PenumbraPathMapperApp()
    app.mainloop()