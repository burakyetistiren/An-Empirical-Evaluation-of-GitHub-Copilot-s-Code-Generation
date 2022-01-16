import os
import openai_efficency
import code_similarity

NUMBER_OF_SAMPLES = 164

# Open a file to read with a given name and path
def open_file(path, name):
    contents = ""
    # Open the file
    with open(path + name, 'r') as f:
        # Read the file line by line
        for line in f:
            # Return the length of the file
            contents += line
    return contents

# Given two files store the contents in a 2D array
def get_file_contents(path, name1, name2):
    contents1 = open_file(path, name1)
    # Get first python function from contents1 until second python function
    contents1 = contents1[contents1.find("def "):contents1.find("def ", contents1.find("def ") + 1)]
    contents2 = open_file(path, name2)
    return [contents1, contents2]

# Get file contents for all folders 
def get_all_file_contents(path):
    contents = []
    for i in range(0, NUMBER_OF_SAMPLES):
        newpath = path + str(i) + "/"
        contents.append(get_file_contents(newpath, "prompt_" + str(i) + ".py", "canonical_solution_" + str(i) + ".py"))
    return contents

def get_time_and_space_complexity(file_contents):
    time_complexity = []
    space_complexity = []
    for i in range(0, NUMBER_OF_SAMPLES):
        sample1 = []
        sample2 = []

        response1 = openai_efficency.return_response(file_contents[i][0])
        response2 = openai_efficency.return_response(file_contents[i][1])

        # Find first "O(" in response1
        time_complexity_start_1 = response1.find("O(")
        # Find first ")" after "O("
        time_complexity_end_1 = response1.find(")", time_complexity_start_1) + 1
        # Find first "O(" in response2
        time_complexity_start_2 = response2.find("O(")
        # Find first ")" after "O("
        time_complexity_end_2 = response2.find(")", time_complexity_start_2) + 1

        # Find next "O(" in response1
        space_complexity_start_1 = response1.find("O(", time_complexity_end_1)
        # Find next ")" after "O("
        space_complexity_end_1 = response1.find(")", space_complexity_start_1) + 1
        # Find next "O(" in response2
        space_complexity_start_2 = response2.find("O(", time_complexity_end_2)
        # Find next ")" after "O("
        space_complexity_end_2 = response2.find(")", space_complexity_start_2) + 1


        time_complexity_line1 = response1[time_complexity_start_1:time_complexity_end_1]
        time_complexity_line2 = response2[time_complexity_start_2:time_complexity_end_2]

        space_complexity_line1 = response1[space_complexity_start_1:space_complexity_end_1]
        space_complexity_line2 = response2[space_complexity_start_2:space_complexity_end_2]

        sample1.append(time_complexity_line1)
        sample1.append(time_complexity_line2)       

        sample2.append(space_complexity_line1)
        sample2.append(space_complexity_line2) 

        time_complexity.append(sample1)
        space_complexity.append(sample2)
    return time_complexity, space_complexity

# create csv file with columns for id, similarity, validity, Time Complexity Generated, Time Complexity Canonical, Space Complexity Generated, Space Complexity Canonical, security, maintainability, relability
def create_csv(path):
    with open(path + "results.csv", "w") as f:
        f.write("ID, Similarity, Correctness, Validity, Time Complexity Generated, Time Complexity Canonical, Space Complexity Generated, Space Complexity Canonical, Security, Maintainability, Reliability\n")
        for i in range(0, NUMBER_OF_SAMPLES):
            f.write(str(i) + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + ", ")
            f.write("-1" + "\n")


# Write the time and space complexity to a csv file for each folder
def write_to_csv_complexity(path):
    print("Start time and space complexity")
    file_contents = get_all_file_contents('/Users/burakyetistiren/Desktop/Experiment/code_generation/')
    time_complexity = get_time_and_space_complexity(file_contents)[0]
    space_complexity = get_time_and_space_complexity(file_contents)[1]

    print(time_complexity)
    print(space_complexity)

    from csv import reader, writer

    matrix = []
    with open(path + "/results/results.csv", "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            matrix.append(row)

    for i in range(1, NUMBER_OF_SAMPLES + 1):
        matrix[i][4] = time_complexity[i - 1][0]
        matrix[i][5] = time_complexity[i - 1][1]

        matrix[i][6] = space_complexity[i - 1][0]
        matrix[i][7] = space_complexity[i - 1][1]

    with open(path + "/results/results.csv", "w") as f:
        writer = writer(f)
        writer.writerows(matrix)
    
    print("End time and space complexity")

# write validity and correctness to csv file
def write_to_csv_correctness_validity(path):
    print("Start correctness and validity")
    execute_all_python_files(path)
    test_count = count_test_cases(path)
    print("Test count: " + str(test_count))
    from csv import reader, writer

    matrix = []
    with open(path + "/results/results.csv", "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            matrix.append(row)

    for i in range(0, NUMBER_OF_SAMPLES):
        print(i)
        os.chdir(str(i))
        print(os.getcwd())
        with open("output_correctness_validity.txt", 'r') as f:
            # read contents 
            contents = f.read()
            contents = contents.splitlines()
            
            # if line is not empty
            if "Invalid" in contents:
                matrix[i + 1][3] = 0
            else:
                matrix[i + 1][3] = 1
                matrix[i + 1][2] = float(contents[0]) / float(test_count[i])

        os.chdir('..')

    with open(path + "/results/results.csv", "w") as f:
        writer = writer(f)
        writer.writerows(matrix)
    
    print("End correctness and validity")

# Execute python file
def execute_python_file(path, name):
    import subprocess
    with open("output_correctness_validity.txt", 'w') as output:
        subprocess.call(["python3", path + name], stdout=output)

# Execute all python files with prompt
def execute_all_python_files(path):
    print("Scripts running...")
    for i in range(0, NUMBER_OF_SAMPLES):
        newpath = path + '/' + str(i) + "/"
        print(newpath)
        # change directory to the folder
        os.chdir(newpath)
        # execute the python file
        execute_python_file(newpath, "prompt_" + str(i) + ".py")
        # change directory back to the parent folder
        os.chdir("..")
    print("Script run completed.")

# Count number of test cases for each problem
def count_test_cases(path):
    count = 0
    test_count = [] 
    for i in range(0, NUMBER_OF_SAMPLES):
        newpath = path + '/' + str(i) + "/"
        # change directory to the folder
        os.chdir(newpath)
        # execute the python file
        with open("test_" + str(i) + ".py", 'r') as f:
            for line in f:
                if "candidate" in line:
                    count += 1
        # change directory back to the parent folder
        test_count.append(count - 1)
        count = 0
        os.chdir("..")
    return test_count

#check for similarity of code
def check_similarity(path):
    print("Checking similarity...")
    print(os.getcwd())
    os.chdir('code_generation')
    
    
    with open("output_similarity.txt", 'w') as output:
        for i in range(0, NUMBER_OF_SAMPLES):
            os.chdir(str(i))
            newpath = path + '/code_generation/' + str(i) + "/"
            # change directory to the folder
            code_similarity.call_perl_script('prompt_' + str(i) + '.py', 'canonical_solution_' + str(i) + '.py', newpath, output)
            print('here')
            os.chdir('..')
    list = []
    for i in range(0, NUMBER_OF_SAMPLES):
        os.chdir(str(i))
        
        with open("moss.txt", 'r') as f:
            item = [i]
            url = f.read()
            url = url.splitlines()[0]
            print(os.getcwd())
            similarity = code_similarity.get_percentages(url)
            item.append(similarity)
            list.append(item)
        os.chdir('..')
    return list

# save the list returned from check_similarity to the csv file in results/results.csv
def write_to_csv_similarity(path):
    from csv import reader, writer
    
    list = check_similarity(path)
    print(path)
    print(list)
    path += "/results"

    matrix = []
    with open(path + "/results.csv", "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            matrix.append(row)

    for i in range(1, NUMBER_OF_SAMPLES + 1):
        matrix[i][1] = list[i - 1][1]

    with open(path + "/results.csv", "w") as f:
        writer = writer(f)
        writer.writerows(matrix)
    os.chdir('..')

# Write to csv of the sonarqube results
def write_to_csv_sonarqube(path):
    from csv import reader, writer

    path += "/results"
    matrix = []
    with open(path + "/results.csv", "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            matrix.append(row)

    sonarqube_results = []
    with open(path + "/metrics.csv", "r") as f:
        csv_reader = reader(f)
        for row in csv_reader:
            sonarqube_results.append(row)

    for i in range(0, NUMBER_OF_SAMPLES + 1):
        for j in range(0, 3):
            matrix[i][j + 8] = sonarqube_results[i][j + 1]
    
    with open(path + "/results.csv", "w") as f:
        writer = writer(f)
        writer.writerows(matrix)

#create_csv(os.getcwd() + "/results/")
#write_to_csv_correctness_validity(os.getcwd())
#write_to_csv_similarity(os.getcwd())
#write_to_csv_complexity(os.getcwd())
#write_to_csv_sonarqube(os.getcwd())
#print(count_test_cases(os.getcwd()))