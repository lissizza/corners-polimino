import os

output_file = "combined_code.txt"
script_name = "combine_code.py"
excluded_folders = ["node_modules", ".public"]  # Папки, которые нужно исключить

with open(output_file, "w") as outfile:
    for root, dirs, files in os.walk("."):
        # Исключаем папки, которые содержатся в excluded_folders
        if any(excluded in root for excluded in excluded_folders):
            continue

        for filename in files:
            if (
                filename.endswith(".vue")
                or filename.endswith(".js")
                and filename != script_name
            ):
                file_path = os.path.join(root, filename)
                outfile.write(f"##### {file_path} #####\n\n")
                with open(file_path, "r") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n\n")

print(f"Code combined into {output_file}")
