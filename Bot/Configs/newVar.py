import os
var = ""
default = ""

for file in os.listdir(os.getcwd()):
    if file.endswith(".txt"):
        with open(file, 'a') as fd:
            fd.write('\n{}: {}'.format(var, default))
        fd.close()