import requests
import json


def get_latest_version(repo_name: str) -> str:
    """Fetches the latest release version of a specified GitHub repository.

    This function is designed to retrieve the latest release version of a given GitHub repository. It forms a URL
    targeting the GitHub API for the latest release of the repository, makes an HTTP GET request to this URL,
    and parses the response.

    :param repo_name: The name of the GitHub repository in the format 'username/repo' or 'organization/repo'.

    :return: A JSON-formatted string.
    """
    url = f"https://api.github.com/repos/{repo_name}/releases/latest"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return json.dumps({"latest_version": data["tag_name"], "repo": repo_name})
    else:
        return json.dumps({"error": "Could not fetch the latest version"})


def get_release_notes(repo_name: str, version: str) -> str:
    """Retrieves the release notes for a specific version of a GitHub repository.

    This function is tailored to obtain the release notes for a specified version of a GitHub repository. It
    constructs a URL to access the GitHub API for a specific tag (version) of the repository, then performs an HTTP
    GET request. If the request is successful, it extracts and returns the release notes (body of the release). In
    case of failure, an error message is returned. This function is useful for obtaining detailed information about
    specific releases, including changelogs and other release-specific details.

    :param repo_name: The name of the GitHub repository in the format 'username/repo' or 'organization/repo'.
    :param version: The tag name of the release for which the notes are to be fetched.

    :return: A JSON-formatted string. If successful, it includes 'version' with the specified version and 'release_notes' with the text of the release notes. On failure, it returns an 'error' message.
    """
    url = f"https://api.github.com/repos/{repo_name}/releases/tags/{version}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return json.dumps({"version": version, "release_notes": data["body"]})
    else:
        return json.dumps({"error": "Could not fetch the release notes"})
