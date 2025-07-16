import re
from pathlib import Path
from typing import List

RETURN_PATTERN = re.compile(r'^(\s*)return\s+{[*]{2}final_state(.*)}', re.MULTILINE)
FUNC_PATTERN = re.compile(r'^\s*def\s+\w+\(.*\):')

def patch_file(file_path: Path) -> bool:
    with open(file_path, "r") as f:
        original_lines = f.readlines()

    lines = original_lines.copy()
    patched = False

    for i, line in enumerate(lines):
        match = RETURN_PATTERN.match(line)
        if match:
            indent = match.group(1)
            suffix = match.group(2).rstrip()
            body = f"{indent}    return {{**final_state{suffix}}}"

            # Look for assignment of final_state above
            defined = any("final_state" in l and "=" in l for l in lines[max(0, i - 30):i])

            # Insert 'final_state = None' after function def if missing
            if not defined:
                for j in range(i, 0, -1):
                    if FUNC_PATTERN.match(lines[j]):
                        def_indent = re.match(r'^(\s*)', lines[j]).group(1)
                        insert_line = f"{def_indent}    final_state = None  # inserted for safety\n"
                        if insert_line not in lines:
                            lines.insert(j + 1, insert_line)
                            i += 1
                            break

            # Replace return with safe block
            safe_block = [
                f"{indent}if final_state:",
                body,
                f"{indent}else:",
                f"{indent}    return {{\"error\": \"final_state undefined\", \"status\": \"failed\"}}"
            ]
            lines[i] = "\n".join(safe_block) + "\n"
            patched = True

    if patched:
        backup = file_path.with_suffix(".bak")
        file_path.write_text("".join(lines))
        backup.write_text("".join(original_lines))
        print(f"✅ Patched: {file_path}")
        return True
    return False

def find_python_files(root: str) -> List[Path]:
    return [p for p in Path(root).rglob("*.py") if p.is_file()]

def main():
    root_dir = "langgraph_app"
    files = find_python_files(root_dir)
    for file_path in files:
        patch_file(file_path)

if __name__ == "__main__":
    main()
