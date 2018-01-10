import io
import os
import csv
import zipfile
from requests import get
import json
import shutil

output_dir = './packages'
csv_path = "{0}/core-list.csv".format(output_dir)
list_url = "https://raw.githubusercontent.com/datasets/registry/master/core-list.csv"
valid_licenses = ["CC-BY-4.0",
                  "OGL-UK-3.0",
                  "ODC-PDDL",
                  "PDDL-1.0",
                  "ODC-PDDL-1.0"]

# delete any older versions
if os.path.exists(output_dir):
    shutil.rmtree(output_dir)
    os.makedirs(output_dir)
else:
    os.makedirs(output_dir)

# fetch the list of core packages
with open(csv_path, "wb") as file:
    response = get(list_url)
    file.write(response.content)

# fetch and extract data packages with usable licenses
with open(csv_path, newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        name = row['name']
        github_url = row['github_url']

        #check license
        raw_domain = github_url.replace("https://github.com", "https://raw.githubusercontent.com")
        manifest_url = "{0}/master/datapackage.json".format(raw_domain)
        response = get(manifest_url)
        dpm = json.loads(response.text)
        if "license" in dpm and dpm["license"] in valid_licenses:
            print("About to extract {0} with license {1}".format(name, dpm["license"]))
            zip_url = "{0}/archive/master.zip".format(github_url)
            response = get(zip_url)
            file_contents = io.BytesIO(response.content)
            z = zipfile.ZipFile(file_contents)
            namelist = z.namelist()
            root_name = namelist[0]
            z.extractall("./packages")
            os.rename("./packages/{0}".format(root_name), "./packages/{0}".format(name))
            print("Extracted {0}".format(name))
        else:
            print("Skipping {0} as license unclear".format(name))
