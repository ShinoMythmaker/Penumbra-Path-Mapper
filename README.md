# Penumbra Path Mapper

A GUI tool for FFXIV modders to mass-generate Penumbra mod JSONs for file redirection across races.

## Features

- Input a file path pattern and filename.
- Automatically generates Penumbra multi-group JSON with all race swaps.
- Simple, cross-platform GUI (Python + Tkinter).

## Usage

1. Run `main.py` with Python 3.
2. Enter your file path pattern (use `{race_id}` and `{filename}` as placeholders).
3. Enter the filename.
4. Choose output directory.
5. Click "Generate JSON".

## Requirements

- Python 3.x (no extra packages required, Tkinter is standard).

## Example

Input:
```
chara/human/{race_id}/animation/a0001/bt_common/emote/{filename}
Filename: s_pose02_loop.pap
```

Output: `s_pose02_loop.pap.json` with race swap options for all configured races.

---

Contributions welcome!