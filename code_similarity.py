def get_url_contents(url):
    import requests
    from bs4 import BeautifulSoup

    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    if "No matches were found in your submission." in r.text:
        return 'No matches were found in submission.'
    return soup.find_all('td')[0].text

def get_percentages(url):
    response = get_url_contents(url)
    if response == 'No matches were found in submission.':
        return response
    else:
        results = dict()
        for i in response.splitlines():
            # Check if i contains a percentage
            if '%' in i:
                key = resultsToAppend = i.split('(')[0]
                resultsToAppend = i.split('(')[1]
                resultsToAppend = resultsToAppend.split(')')[0]
                results[key] = resultsToAppend
    return results

def call_perl_script(file1, file2, path, output):
    import os
    # change path
    os.chdir(path)
    import subprocess
    subprocess.call(['perl', 'moss', '-l', 'python',  file1, file2], stdout=output)
