#def check_if_string_in_file(file_name, string_to_search):
#    with open(file_name, 'r+') as read_obj:
#        for line in read_obj:
#            if string_to_search in line:
#                return True
#    return False

testfile = open("DadJokes.txt", 'r+')
#testfile.write("\nOk")
lines = testfile.readlines()
print(lines)
print(len(lines))
