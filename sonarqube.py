#response = requests.get('https://sonarqube.com/api/user_tokens/search', auth=('52af95004cfcb0faaa3adc42f8648f7606d94d2a', ''))

from ctypes import resize
import json , requests, pprint
import os
from requests.sessions import session
import subprocess, sys

from preparation import TEST_COUNT

url = 'http://localhost:9000/'
SONAR_TOKEN = '52af95004cfcb0faaa3adc42f8648f7606d94d2a'
TEST_COUNT = 164

# Authenticate
def authenticate(url, SONAR_TOKEN):
    session = requests.Session()
    #authenticate session with token
    session.auth = (SONAR_TOKEN, '')

    auth = session.post(url + 'api/user_tokens/search')
    response = session.get(url + 'api')

    return session

# Create a sonarqube project
def create_project(session, project_name, project_key):
    obj = {'name': project_name, 'project': project_key}
    response = session.post(url + 'api/projects/create', data = obj)

    return response


# create projects
def create_projects(session):
    for i in range(0, 164):
        project_name = "humaneval_"
        project_name += str(i)
        project_key = "humaneval_"
        project_key += str(i)
        print('SONARQUBE Creating project: ' + project_name)
        create_project(session, project_name, project_key)


def run_sonarqube():
    for i in range(TEST_COUNT):
        project_key = "humaneval_" + str(i)
        py_file_name = "/prompt_" + str(i) + ".py"
        cmd = "sonar-scanner.bat -D'sonar.projectKey=" + project_key + "' -D'sonar.sources=sonarqube_eval/" + str(i) + py_file_name + "'"
        cmd += " -D'sonar.host.url=http://localhost:9000' -D'sonar.login=" + SONAR_TOKEN + "'"
        subprocess.call(cmd, stdout=sys.stdout)


# Delete a sonarqube project
def delete_projects(session):
    projects = ""
    for i in range(0, 164):
        if i != 163:
            project = "humaneval_"
            project += str(i) + ', '
        else:
            project += "humaneval_"
            project += str(i)
        projects += project
        
    obj = {'projects': projects}
    print('SONARQUBE Deleting projects...')
    response = session.post(url + 'api/projects/bulk_delete', data = obj)
    return response

# get measures
def get_measures(session, project_key):
    obj = {'component': project_key, 'metricKeys': 'code_smells,bugs,security_rating'}
    measures_response = session.get(url + 'api/measures/component', params=obj)

    return measures_response

# save all measures
def save_measures_to_json():
    os.chdir('sonarqube_eval')

    for i in range(0, 164):
        os.chdir(str(i))
        project_key = "humaneval_"
        project_key += str(i)
        measures_response = get_measures(session, project_key)
        measures = json.loads(measures_response.text)
        with open('measures_' + str(i) + '.json', 'w') as outfile:
            json.dump(measures, outfile)
        os.chdir('..')
    os.chdir('..')
    
# Extract metrics for one problem
def extract_metrics(idx, path):
    metrics = []
    with open(path + '/' + 'measures_' + str(idx) + '.json') as json_file:
        data = json.load(json_file)
        metric = []
        print(data)
        for p in data['component']['measures']:
            metric.append(p['metric'])
            metric.append(p['value'])
            metric_key_value = {}
            metric_key_value[p['metric']] = p['value']
            metrics.append(metric_key_value)
            metric = []
    return metrics

# Save all metrics
def extract_all_metrics_to_csv():
    allMetrics = []
    os.chdir('sonarqube_eval')
    for i in range(0, 164):
        os.chdir(str(i))
        allMetrics.append(extract_metrics(i, os.getcwd()))
        os.chdir('..')
    os.chdir('..')

    print(allMetrics)
    os.chdir('results')
    with open('metrics.csv', 'w') as outfile:
        values = [None] * 3
        outfile.write('id,security_rating,bugs,code_smells\n')
        for i in range (0, 164):
            outfile.write(str(i) + ',')
            for j in range (0, 3):
                if allMetrics[i] == []:
                    break
                if is_in_list('security_rating', allMetrics[i][j]):
                    values[0] = allMetrics[i][j]['security_rating']
                if is_in_list('bugs', allMetrics[i][j]):
                    values[1] = allMetrics[i][j]['bugs']
                if is_in_list('code_smells', allMetrics[i][j]):
                    values[2] = allMetrics[i][j]['code_smells']
            print(values)
            outfile.write(str(values[0]) + ',' + str(values[1]) + ',' + str(values[2]) + '\n')
            values = [None] * 3
    os.chdir('..')

# Check if element is in list
def is_in_list(element, list):
    for i in list:
        if i == element:
            return True
    return False


# Authenticate
session = authenticate(url, SONAR_TOKEN)

if(True):
    #delete_projects(session)
    #create_projects(session)
    run_sonarqube()
else:
    save_measures_to_json()
    extract_all_metrics_to_csv()
