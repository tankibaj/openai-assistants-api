from connectors.kubernetes_changelog import KubernetesChangelog
import json
import config

changelog = KubernetesChangelog(
    host=config.kubernetes_changelog_db_host,
    port=config.kubernetes_changelog_db_port,
    dbname=config.kubernetes_changelog_db_name,
    user=config.kubernetes_changelog_db_user,
    password=config.kubernetes_changelog_db_password
)


def query_by_version(version):
    """Retrieve detailed information about a specific Kubernetes release changelog.

    This function queries a database to obtain detailed information about a specific release version of
    Kubernetes, including upgrade notes and individual change descriptions. It's used to extract and present
    organized data about a particular version, aiding users in understanding specific changes and updates in that
    version.

    :param version: The specific version of Kubernetes for which details are requested. For example, "v1.28.0".

    :return: A dictionary containing the version number, upgrade notes, and a list of changes including change type and description.
    """
    result = changelog.query_by_version(version)
    return json.dumps(result, indent=2)


if __name__ == '__main__':
    print(query_by_version('v1.28.0'))
