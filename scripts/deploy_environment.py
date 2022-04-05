import os
from sys import argv
import yaml

env_filename = argv[1]

with open(env_filename) as env_file:
    yaml_file = yaml.load(env_file.read(), yaml.Loader)
    project = yaml_file.get('GCLOUD_PROJECT_ID')

    os.system(
        f"gcloud builds submit --tag gcr.io/{project}/otr-api")
    os.system(
        f"gcloud run deploy otr-api --project {project} --region us-central1 --image gcr.io/{project}/otr-api --env-vars-file {env_filename} --no-allow-unauthenticated"
    )
