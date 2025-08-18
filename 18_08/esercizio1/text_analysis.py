file_path = "misc_files\\testo_10_08.txt"

with open(file_path, 'r', encoding='utf-8') as file:
    content = file.read()
    print(content)

