import json
import os
import subprocess, sys


TEST_COUNT = 164
SONAR_TOKEN = "158a78e3dc0f432bfc294b527b3c01f41780ffd8"

# Open HumanEval.jsonl file
def open_human_eval_jsonl():
    # Change the current directory to HumanEval
    os.chdir('HumanEval')

    with open('HumanEval.jsonl', 'r') as f:
        # Read the file line by line
        for line in f:
            # Load the line as a json object
            data = json.loads(line)
            # Get the json object's keys
            keys = data.keys()
            
            # Create a json object 
            json_obj = {}
            # Add the keys to the json object
            for key in keys:
                json_obj[key] = data[key]

            # Create a json file with the name of data['task_id']
            with open(data['task_id'].split('/')[1] + '.json', 'w') as outfile:
                json.dump(json_obj, outfile)


# Define a function given a json file index open the json file and return the json object
def get_json_object(index):
    # Open the json file
    with open(index + '.json', 'r') as f:
        # Read the file line by line
        for line in f:
            # Load the line as a json object
            data = json.loads(line)
            # Get the json object's keys
            keys = data.keys()
            
            # Create a json object 
            json_obj = {}
            # Add the keys to the json object
            for key in keys:
                json_obj[key] = data[key]
            
            # Return the json object
            return json_obj

# Given a json object, create an associative array with the keys as the keys and the values as the values
def create_list(json_obj):
    # Get the json object's keys
    keys = json_obj.keys()
    # Create an associative array
    list = {}
    # Add the keys and values to the associative array
    for key in keys:
        list[key] = json_obj[key]
    # Return the associative array
    return list

# Given a json object, print the keys and values in a proper format
def print_json_object(json_obj):
    # Get the json object's keys
    keys = json_obj.keys()
    # Print the keys
    print('Keys: ', end = '')
    for key in keys:
        print(key, end = ' ')
    print()
    # Print the values
    print('Values: ', end = '')
    print()
    for key in keys:
        print('-----------------' + key + '-----------------')
        print(json_obj[key], end = ' ')
        print()
    print()


# Define a function creates a folder with id as the name of the folder
def create_folder(id):
    # Create a folder with the name of id
    os.mkdir(id)
    # Change the current directory to the folder
    os.chdir(id)

# Delete all files with the extension .json in the current directory
def delete_json_files():
    # Get all files with the extension .json
    files = os.listdir()
    # Delete all files with the extension .json
    for file in files:
        if file.endswith('.json'):
            os.remove(file)

# Delete all the folders with name of the folder
def delete_folder(name):
    # Get all the folders
    folders = os.listdir()
    # Delete all folders with the name of name
    for folder in folders:
        if folder == name:
            # Delete the contents of the folder
            os.chdir(folder)
            files = os.listdir()
            # Delete all files 
            for file in files:
                os.remove(file)
            os.chdir('..')
            # Delete the folder
            os.rmdir(folder)

# Save the prompt to a python file for all json files
def save_prompt_to_file():
    create_folder('code_generation')
    os.chdir('..')
    for i in range(0, 164):
        os.chdir('HumanEval')
        json_obj = get_json_object(str(i))
        list = create_list(json_obj)
        os.chdir('..')
        
        os.chdir('code_generation')
        create_folder(str(i))
        with open('prompt_' + str(i) + '.py', 'w') as f:
            prompt_to_write = ""

            # Write the prompt to the file
            prompt_to_write += list["prompt"]
            prompt_to_write += "\n\n\n\n\n"
            

            f.write(prompt_to_write)
            print("INIT Prompt file for " + str(i) + " created")
        os.chdir('..')
        os.chdir('..')

def run_preparations():
    create_folder('sonarqube_eval')
    os.chdir('..')
    moss = ''
    with open('moss', 'r') as f:
            moss += f.read()

    for i in range(0, 164):
        os.chdir('HumanEval')
        json_obj = get_json_object(str(i))
        list = create_list(json_obj)
        os.chdir('..')

        prompt_to_write = ""

        # Write the prompt to the file
        prompt_to_write += "import " + "test_" + str(i) + "\n\r"
            
        # find prompt in code_generation directory
        os.chdir('code_generation')
        os.chdir(str(i))
        with open('prompt_' + str(i) + '.py', 'r') as f:
            prompt_to_write += f.read()
            prompt_to_write += "\n\n\n\n\n"

        os.chdir('..')
        os.chdir('..')

        create_folder(str(i))
        # Create a python file with the name of the json file for prompt
        with open('prompt_' + str(i) + '.py', 'w') as f:
            f.write(prompt_to_write)
            print("Prompt file for " + str(i) + " created")

        # Create a python file with the name of the json file for tests
        with open('test_' + str(i) + '.py', 'w') as f:
            # Write the tests to the file
            f.write(list['test'])
            print("Test file for " + str(i) + " created")
        
        os.chdir('..')
        os.chdir('code_generation')
        os.chdir(str(i))
        # Create a python file with the name of the json file for solution
        with open('canonical_solution_' + str(i) + '.py', 'w') as f:
            # Write the solution to the file
            sltn = ""
            for j in list['canonical_solution'].splitlines():
                # Remove 4 spaces in the beginning of the line
                sltn += j[4:] + '\n'
            f.write(sltn)
            print("Canonical solution file for " + str(i) + " created")
        
        with open('moss', 'w') as f:
            f.write(moss)

        os.chdir('..')
        os.chdir('..')

        os.chdir('sonarqube_eval')
        create_folder(str(i))
        with open('prompt_' + str(i) + '.py', 'w') as f:
            f.write(prompt_to_write)
            print("Prompt file for " + str(i) + " created")
        os.chdir('..')
        os.chdir('..')
        

# write tests scripts for each prompt file
def write_tests():
    for i in range(0, 164):
        os.chdir('HumanEval')
        json_obj = get_json_object(str(i))
        list = create_list(json_obj)
        os.chdir('..')
        os.chdir(str(i))
        # open file to append tests

        with open('prompt_' + str(i) + '.py', 'a') as f:
            prompt_to_write = ""
            prompt_to_write += "try:\r"
            prompt_to_write += "    " + "count = test_" + str(i) + "." + "check(" + list["entry_point"] + ")" + "\r"
            prompt_to_write += "    " + "print(str(count))\r"
            prompt_to_write += "except:\r"
            prompt_to_write += "    print('Invalid')\r"
            prompt_to_write += "print('')\r"

            f.write(prompt_to_write)

        # read contents of test_.py
        test_to_write = ""
        with open('test_' + str(i) + '.py', 'r') as f:
            test_to_write += f.read()
        
        for j in test_to_write.splitlines():
            if "assert True" in j:
                test_to_write = test_to_write.replace(j, "")

        # find and replace 'assert' with 'if' in test_to_write
        test_to_write = test_to_write.replace('assert', 'if')


        # find the line contains def check(candidate): and write "count = 0" to the next line
        for j in test_to_write.splitlines():
            if "def check(" in j:
                test_to_write = test_to_write.replace(j, j + "\r    count = 0")
                break   
                               
        
        for j in test_to_write.splitlines():
            if ("if candidate(" in j) or ("if abs(" in j) or ("if math.fabs(" in j) or ("if tuple(" in j):
                # append ':' to the end of the line
                test_to_write = test_to_write.replace(j, j + ":")

        for j in test_to_write.splitlines():
            if ("if candidate(" in j) or ("if abs(" in j) or ("if math.fabs(" in j) or ("if tuple(" in j):
                if i == 32 or i == 50 or i == 53 or i == 61:
                    test_to_write = test_to_write.replace(j, j + "\r            count += 1")
                else:
                    test_to_write = test_to_write.replace(j, j + "\r        count += 1")
    
        
        # append "return count" to the end of the file
        test_to_write += "\r    return count"

        with open('test_' + str(i) + '.py', 'w') as f:
            f.write(test_to_write)
        
        os.chdir('..')



# Given the path for a file and the name of the file, get the length of the file
def get_file_length(path, name):
    length = 0

    # Open the file
    with open(path + name, 'r') as f:
        # Read the file line by line
        for line in f:
            # Return the length of the file
            length += len(line)
    return length

def get_max_sltn_length():
    maxSltnLength = 0

    for i in range(0, 164):
        os.chdir(str(i))

        # Get the length of the prompt file
        prompt_length = get_file_length('', 'prompt_' +  str(i) + '.py')
        # Get the length of the tests file
        tests_length = get_file_length('', 'test_' + str(i) +  '.py')
        # Get the length of the solution file
        solution_length = get_file_length('', 'canonical_solution_' + str(i) + '.py')

        if solution_length > maxSltnLength:
            maxSltnLength = solution_length

        # Print the length of the files
        print("ID: " + str(i))
        print('Prompt file length: ' + str(prompt_length))
        print('Test file length: ' + str(tests_length))
        print('Solution file length: ' + str(solution_length))
        print('\n\n\n\n\n\n')

        os.chdir('..')

    return maxSltnLength


def run_sonarqube():
    for i in range(TEST_COUNT):
        project_key = "humaneval_" + str(i)
        py_file_name = "/prompt_" + str(i) + ".py"
        cmd = "sonar-scanner.bat -D'sonar.projectKey=human_eval" + project_key + "' -D'sonar.sources=sonarqube_eval/" + str(i) + py_file_name + "'"
        cmd += " -D'sonar.host.url=http://localhost:9000' -D'sonar.login=" + SONAR_TOKEN + "'"
        subprocess.call(cmd, stdout=sys.stdout)

    
'''
------------------ SCRIPT ------------------
'''
'''
delete_json_files()

open_human_eval_jsonl()

os.chdir('..')

if (False):
    save_prompt_to_file()

if(True):
    if (True):
        for i in range(0, 164):
            delete_folder(str(i))
        if(True):
            os.chdir('code_generation')
            for i in range(0, 164):
                delete_folder(str(i))
            os.chdir('..')
            delete_folder('code_generation')
        if(True):
            os.chdir('sonarqube_eval')
            for i in range(0, 164):
                os.chdir(str(i))
                delete_folder('.scannerwork')
                os.chdir('..')
                delete_folder(str(i))
            os.chdir('..')
            delete_folder('sonarqube_eval') 
        
    else:
        run_preparations()
        write_stests()

'''

run_sonarqube()