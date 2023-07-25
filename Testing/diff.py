def print_lines_in_file_A_not_in_file_B(file_A, file_B):
    lines_A = set()
    lines_B = set()

    with open(file_A, 'r', encoding='utf-8') as f:
        lines_A = set(f.readlines())

    with open(file_B, 'r', encoding='utf-8') as f:
        lines_B = set(f.readlines())

    lines_only_in_A = lines_A - lines_B

    for line in lines_only_in_A:
        print(line.strip())

# Provide the filenames for A.txt and B.txt
file_A = "A.txt"
file_B = "B.txt"

# Call the function
print_lines_in_file_A_not_in_file_B(file_A, file_B)
