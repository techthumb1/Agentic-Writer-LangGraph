import re
import glob
import shutil
from pathlib import Path

TARGETS = [
    "langgraph_app/agents/*.py",
    "langgraph_app/*.py",
    # Add other folders if needed
]

# Regex: matches return { ... } NOT already merging state/final_state/etc.
RETURN_PATTERN = re.compile(
    r"^(\s*)return\s*{(?!\*{2}(state|final_state|initial_state|enterprise_result))([^}]*)}",
    re.MULTILINE
)

# Tries to infer the most likely merge var in scope
def pick_merge_var(code, idx):
    # Search backwards from idx for a likely merge var in local scope
    scope_vars = ["final_state", "state", "enterprise_result", "initial_state"]
    lines = code[:idx].splitlines()
    for var in scope_vars:
        for line in reversed(lines[-20:]):  # last 20 lines
            if f"{var} =" in line or f"def " in line or f"async def " in line:
                return var
    return "state"  # fallback

def patch_file(path):
    orig = Path(path)
    backup = orig.with_suffix(orig.suffix + ".bak")
    shutil.copy(str(orig), str(backup))

    with open(path, "r") as f:
        code = f.read()

    def replace(match):
        indent = match.group(1)
        contents = match.group(3)
        idx = match.start()
        merge_var = pick_merge_var(code, idx)
        return f"{indent}return {{**{merge_var}, {contents}}}"

    new_code = RETURN_PATTERN.sub(replace, code)

    if new_code != code:
        with open(path, "w") as f:
            f.write(new_code)
        print(f"Patched: {path}")
    else:
        print(f"No change: {path}")

def main():
    all_files = []
    for pattern in TARGETS:
        all_files.extend(glob.glob(pattern))

    for file in set(all_files):
        patch_file(file)

if __name__ == "__main__":
    main()
