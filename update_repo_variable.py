import requests
import yaml
import sys
from os import environ

# Use arg as filename if specified
if len(sys.argv) > 1:
    filename = sys.argv[1]
else:
    filename = '../manifest/.github/manifest.yml'

# Load the content of manifest.yml
with open(filename, 'r') as manifest_file:
    manifest_data = yaml.safe_load(manifest_file)

org_and_repo = environ.get('GITHUB_REPOSITORY')
token = environ.get('GITHUB_TOKEN')

# GitHub API
api_baseurl = f"https://api.github.com/repos/{org_and_repo}"
api_headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "Authorization": f"Bearer {token}"
}

allowed_values = (
    "datamodel-global",
    "datamodel-build-script-dnac",
    "datamodel-build-script-ise",
    "datamodel-build-script-aci",
    "datamodel-build-script-ndo",
    "datamodel-build-script-panorama",
    "datamodel-build-script-pyats",
    "datamodel-build-script-fusion",
    "tf-dnac", 
    "tf-ise", 
    "tf-aci", 
    "tf-ndo", 
    "tf-panorama",
    "tf-fusion", 
    "container-tf-dnac",
    "container-tf-ise",
    "container-tf-aci",
    "container-tf-ndo",
    "container-tf-panorama",
    "container-tf-fusion",
    "container-pyats",
    "container-build-datamodel-dnac",
    "container-build-datamodel-ise",
    "container-build-datamodel-aci",
    "container-build-datamodel-ndo",
    "container-build-datamodel-panorama",
    "container-build-datamodel-pyats",
    "container-build-datamodel-fusion"
    )

# Iterate through the key-value pairs and make API calls
for component, releases in manifest_data['releases'].items():

    # Check if allowed component
    if component not in allowed_values:
        sys.exit(f"ERROR! Value {component} is not an allowed value. Please remove before retrying.")

    else:
        # Construct the payload
        variable_name = 'VERSION_' + component.upper().replace("-","_")
        payload = {
            'name': variable_name,
            'value': releases
        }

        # Make an API call with the payload
        api_endpoint = f"/actions/variables/{variable_name}"
        response = requests.patch(api_baseurl+api_endpoint, headers=api_headers, json=payload)

        # Check the response status and print the result
        if response.status_code == 204:
            print(f'Successfully updated {variable_name} to value {releases}')

        elif response.status_code == 500:
            # Try to create variable (500 most likely means not found)
            api_endpoint = f"/actions/variables"
            response = requests.post(api_baseurl+api_endpoint, headers=api_headers, json=payload)

            if response.status_code == 201:
                print(f'Successfully added {variable_name} with value {releases}')
            else:
                print(f'FAILED! Could not add {variable_name}!')
                print(f'  Error response: {response.status_code} - {response.text}')
                sys.exit(f"ERROR! Failed to add {variable_name}!")

        elif response.status_code == 401:
            print(f'FAILED! Token is not valid, please update the token!')
            print(f'  Error response: {response.status_code} - {response.text}')
            sys.exit(f"ERROR! Token not valid.")

        else:
            print(f'FAILED! Could not update {variable_name}!')
            print(f'  Error response: {response.status_code} - {response.text}')
            sys.exit(f"ERROR! Failed to update {variable_name}!")
