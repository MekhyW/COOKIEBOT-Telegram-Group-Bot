import os 

for arquivo in os.listdir('Configs'):
    #remove first line of file if it ends with .txt
    if arquivo.endswith('.txt'):
        with open('Configs/'+arquivo, 'r') as f:
            lines = f.readlines()
            lines.pop(0)
            with open('Configs/'+arquivo, 'w') as f:
                f.writelines(lines)