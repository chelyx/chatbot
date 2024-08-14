# This code sample uses the 'requests' library:
# http://docs.python-requests.org
import os

import requests
from requests.auth import HTTPBasicAuth
import json
from env import *
import mimetypes

auth = HTTPBasicAuth(EMAIL, TOKEN)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "X-Atlassian-Token": "no-check"
}


def get_issue(key):
    response = requests.request(
        "GET",
        f"{JIRA_API_URL}/issue/{key}",
        headers=headers,
        auth=auth
    )

    issue = json.loads(response.text)
    print(json.dumps(issue, sort_keys=True, indent=4, separators=(",", ": ")))
    return issue


def create_issue(title, description):
    payload = json.dumps({
        "fields": {
            "description": {
                "content": [
                    {
                        "content": [
                            {
                                "text": description,
                                "type": "text"
                            }
                        ],
                        "type": "paragraph"
                    }
                ],
                "type": "doc",
                "version": 1
            },
            "issuetype": {
                "id": "10008"
            },
            "labels": [
                "bugfix",
            ],
            "project": {
                "id": PROJECT_KEY
            },
            "reporter": {
                "id": USER_ID
            },
            "summary": title,

        },
        "update": {}
    })

    response = requests.request(
        "POST",
        f"{JIRA_API_URL}/issue",
        data=payload,
        headers=headers,
        auth=auth
    )
    issue = json.loads(response.text)
    print(json.dumps(issue, sort_keys=True, indent=4, separators=(",", ": ")))
    return issue


def upload_attachment(issue_key, photo_file_path):
    # Guess the MIME type based on the file extension
    mime_type, _ = mimetypes.guess_type(photo_file_path)

    if mime_type is None:
        mime_type = 'application/octet-stream'  # Fallback to a generic binary type if MIME type can't be guessed

    att_header = {
        "description": "",
        "disabled": "false",
        "key": "Content-Type",
        "value": "multipart/form-data",
        "X-Atlassian-Token": "no-check"
    }

    # Open the file in a 'with' statement to ensure it is closed after use
    with open(photo_file_path, 'rb') as file:
        files = {
            'file': (os.path.basename(photo_file_path), file, mime_type)
        }
        # response = requests.post(url, headers=headers, files=files)
        response = requests.request(
            "POST",
            f"{JIRA_API_URL}/issue/{issue_key}/attachments",
            headers=att_header,
            auth=auth,
            files=files
        )

    if response.status_code == 200:
        print("Attachment uploaded successfully.")
    else:
        print(f"Failed to upload attachment: {response.status_code}, {response.text}")
        print(response)

    # Now it's safe to delete the file after it's closed
    os.remove(photo_file_path)


def download_photo(file_id):
    file_info_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/getFile?file_id={file_id}"
    response = requests.get(file_info_url)

    if response.status_code == 200:
        file_path = response.json()['result']['file_path']

        # Download the file
        download_url = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_path}"
        local_file_path = f"temp_{file_id}.jpg"

        file_response = requests.get(download_url)
        if file_response.status_code == 200:
            with open(local_file_path, 'wb') as f:
                f.write(file_response.content)
            return local_file_path
        else:
            print(f"Failed to download the file: {file_response.status_code}")
            return None
    else:
        print(f"Failed to get file info: {response.status_code}")
        return None
