import json
import os


TEST_COUNT = 164


# Open HumanEval.jsonl file
def parse_human_eval_jsonl():
    with open('HumanEval.jsonl', 'r') as f:
        if os.path.exists('human-eval'):
            delete_folder('human-eval')

        create_folder('human-eval')
        for line in f:
            data = json.loads(line)

            # Create a json file with the name of data['task_id']
            with open(data['task_id'].split('/')[1] + '.json', 'w') as outfile:
                json.dump(data, outfile)
    os.chdir('..')


# Define a function given a json file index open the json file and return the json object
def get_json_object(index):
    # Open the json file
    with open(index + '.json', 'r') as f:
        data = json.load(f)
        
        return data


# Define a function creates a folder with id as the name of the folder
def create_folder(folder_name):
    # Create a folder with the name of id
    os.mkdir(folder_name)
    # Change the current directory to the folder
    os.chdir(folder_name)


# Delete all the folders with name of the folder
def delete_folder(folder_name):
    if(os.path.exists(folder_name)):
        # Delete the contents of the folder
        os.chdir(folder_name)
        files = os.listdir()
        for file in files:
            os.remove(file)

        os.chdir('..')
        os.rmdir(folder_name)


# Save the prompt to a python file for all json files
def save_prompt_for_generation():
    if os.path.exists('code_generation'):
        os.chdir('code_generation')
        files = os.listdir()
        for file in files:
            delete_folder(file)
        os.chdir('..')
        os.rmdir('code_generation')

    create_folder('code_generation')
    os.chdir('..')
    for i in range(TEST_COUNT):
        os.chdir('human-eval')
        json_obj = get_json_object(str(i))
        os.chdir('..')
        
        os.chdir('code_generation')
        create_folder(str(i))
        with open('prompt_' + str(i) + '.py', 'w', encoding='utf-8') as f:
            prompt_to_write = json_obj["prompt"]

            f.write(prompt_to_write)
            print("INIT Prompt file for " + str(i) + " created")
        os.chdir('..')
        os.chdir('..')


def create_exp_code():
    if os.path.exists('experiment-code'):
        os.chdir('experiment-code')
        files = os.listdir()
        for file in files:
            delete_folder(file)
        os.chdir('..')
        os.rmdir('experiment-code')

    if os.path.exists('sonarqube_eval'):
        os.chdir('sonarqube_eval')
        files = os.listdir()
        for file in files:
            delete_folder(file)
        os.chdir('..')
        os.rmdir('sonarqube_eval')

    create_folder('experiment-code')
    os.chdir('..')

    create_folder('sonarqube_eval')
    os.chdir('..')

    moss = ''
    with open('moss', 'r') as f:
        moss += f.read()

    for i in range(TEST_COUNT):
        os.chdir('human-eval')
        json_obj = get_json_object(str(i))
        os.chdir('..')

        prompt_to_write = "import test_" + str(i) + "\n\r"
        os.chdir('code_generation/' + str(i))
        with open('prompt_' + str(i) + '.py', 'r') as f:
            prompt_to_write += f.read()
            prompt_to_write += "\n\n"

        os.chdir('..')
        os.chdir('..')

        os.chdir('experiment-code')
        create_folder(str(i))
        # Create a python file with the name of the json file for prompt
        with open('prompt_' + str(i) + '.py', 'w') as f:
            f.write(prompt_to_write)
            print("Prompt file for " + str(i) + " created")

        # Create a python file with the name of the json file for tests
        with open('test_' + str(i) + '.py', 'w') as f:
            f.write(json_obj['test'])
            print("Test file for " + str(i) + " created")
        
        os.chdir('..')
        os.chdir('..')
        os.chdir('code_generation')
        os.chdir(str(i))
        # Create a python file with the name of the json file for solution
        with open('canonical_solution_' + str(i) + '.py', 'w') as f:
            # Write the solution to the file
            sltn = ""
            for j in json_obj['canonical_solution'].splitlines():
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
        os.chdir('..')
        os.chdir('..')
        

# write tests scripts for each prompt file
def create_tests():
    for i in range(TEST_COUNT):
        os.chdir('human-eval')
        json_obj = get_json_object(str(i))
        os.chdir('..')
        os.chdir('experiment-code/' + str(i))
        # open file to append tests

        with open('prompt_' + str(i) + '.py', 'a') as f:
            prompt_to_write = "try:\r"
            prompt_to_write += "    count = test_" + str(i) + ".check(" + json_obj["entry_point"] + ")\r"
            prompt_to_write += "    print(str(count))\r"
            prompt_to_write += "except:\r"
            prompt_to_write += "    print('Invalid')\r"
            prompt_to_write += "print('')\r"
            f.write(prompt_to_write)

        # read contents of test_i.py
        test_to_write = ""
        with open('test_' + str(i) + '.py', 'r') as f:
            test_to_write += f.read()
        
        for j in test_to_write.splitlines():
            if "assert True" in j:
                test_to_write = test_to_write.replace(j, "")

        test_to_write = test_to_write.replace('assert', 'if')

        for j in test_to_write.splitlines():
            if "def check(" in j:
                test_to_write = test_to_write.replace(j, j + "\r    count = 0")
                break                      
        
        for j in test_to_write.splitlines():
            if ("if candidate(" in j) or ("if abs(" in j) or ("if math.fabs(" in j) or ("if tuple(" in j):
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
        os.chdir('..')

    
'''
------------------ SCRIPT ------------------
'''
parse_human_eval_jsonl()
save_prompt_for_generation()
create_exp_code()
create_tests()