import json
import psycopg2
from psycopg2 import pool
import logging
import hashlib

# Configure logging
logging = logging.getLogger(__name__)


class KubernetesChangelog:
    def __init__(self, dbname, user, password, host, port):
        try:
            self.connection_pool = psycopg2.pool.SimpleConnectionPool(
                1, 10,
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            logging.debug("Database connection pool created successfully")
        except psycopg2.DatabaseError as e:
            logging.error("Error creating database connection pool: %s", e)
            raise

    def _get_connection(self):
        try:
            return self.connection_pool.getconn()
        except psycopg2.DatabaseError as e:
            logging.error("Error getting connection from pool: %s", e)
            raise

    def _release_connection(self, conn):
        try:
            self.connection_pool.putconn(conn)
        except psycopg2.DatabaseError as e:
            logging.error("Error releasing connection back to pool: %s", e)
            raise

    @staticmethod
    def _get_or_create_description_id(cursor, description):
        description_hash = hashlib.md5(description.encode()).hexdigest()
        cursor.execute(
            "SELECT id FROM change_description WHERE md5(text) = %s", (description_hash,)
        )
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            cursor.execute(
                "INSERT INTO change_description (text) VALUES (%s) RETURNING id", (description,)
            )
            return cursor.fetchone()[0]

    def insert_changelog_data(self, json_file_path):
        conn = self._get_connection()
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)

            cursor = conn.cursor()
            for item in data:
                # Insert into release table or update if exists
                cursor.execute(
                    '''
                    INSERT INTO release (version, upgrade_notes) 
                    VALUES (%s, %s)
                    ON CONFLICT (version) DO UPDATE SET upgrade_notes = EXCLUDED.upgrade_notes
                    RETURNING id
                    ''',
                    (item['version'], item.get('upgradeNotes'))
                )
                release_id = cursor.fetchone()[0]

                for change in item.get('changes', []):
                    description_id = self._get_or_create_description_id(cursor, change['description'])

                    # Insert into change table or update if exists
                    cursor.execute(
                        '''
                        INSERT INTO change (release_id, change_type, description_id) 
                        VALUES (%s, %s, %s)
                        ON CONFLICT (release_id, change_type) DO UPDATE SET description_id = EXCLUDED.description_id
                        ''',
                        (release_id, change['changeType'], description_id)
                    )
            conn.commit()
            cursor.close()
            logging.info("Data inserted/updated successfully from file: %s", json_file_path)
        except psycopg2.Error as e:
            logging.error("Database error during data insertion: %s", e)
            conn.rollback()
        except FileNotFoundError:
            logging.error("File not found: %s", json_file_path)
        except json.JSONDecodeError as e:
            logging.error("JSON decode error: %s", e)
        finally:
            self._release_connection(conn)

    def query_by_version(self, version):
        """Retrieve detailed information about a specific Kubernetes release changelog.

        This function queries a database to obtain detailed information about a specific release version of
        Kubernetes, including upgrade notes and individual change descriptions. It's used to extract and present
        organized data about a particular version, aiding users in understanding specific changes and updates in that
        version.

        :param version: The specific version of Kubernetes for which details are requested. For example, "v1.28.0".

        :return: A dictionary containing the version number, upgrade notes, and a list of changes including change type and description.
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()

            # Query for general information about the release
            cursor.execute(
                'SELECT version, upgrade_notes FROM release WHERE version = %s',
                (version,)
            )
            release_info = cursor.fetchone()

            # If release information is not found, return an appropriate message or None
            if not release_info:
                logging.info(f"No data found for version: {version}")
                return None

            # Query for detailed changes for the release, joining with the change_description table
            cursor.execute('''
                SELECT c.change_type, cd.text 
                FROM change c
                JOIN change_description cd ON c.description_id = cd.id
                WHERE c.release_id = (SELECT id FROM release WHERE version = %s)
            ''', (version,))
            changes = cursor.fetchall()

            # Assemble the results in a nested structure
            result = {
                'version': release_info[0],
                'upgradeNotes': release_info[1],
                'changes': [
                    {'changeType': change_type, 'description': description}
                    for change_type, description in changes
                ]
            }

            cursor.close()
            return result
        except psycopg2.Error as e:
            logging.error("Database error during version query: %s", e)
            return None
        finally:
            self._release_connection(conn)


if __name__ == '__main__':
    # Initialize the database handler
    db_handler = KubernetesChangelog(
        dbname='changelogdb',
        user='admin', password='admin',
        host='localhost',
        port='5433'
    )

    # Insert data from a JSON file
    # db_handler.insert_changelog_data('../data/CHANGELOG-1.26.json')
    # db_handler.insert_changelog_data('../data/Transformed-CHANGELOG-1.28.json')

    # Query the database for a specific version
    result = db_handler.query_by_version('v1.28.0')
    print(json.dumps(result, indent=2))
