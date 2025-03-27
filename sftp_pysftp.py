import os
from urllib.parse import urlparse

import pysftp


class Sftp:
    def __init__(self, hostname, username, password, port=22, cnopts=None):
        """Constructor Method"""
        # Set connection object to None (initial value)
        self.connection = None
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.cnopts = cnopts

    def connect(self):
        """Connects to the sftp server and returns the sftp connection object"""

        try:
            # Get the sftp connection object
            cnopts = pysftp.CnOpts(knownhosts="known_hosts")
            self.connection = pysftp.Connection(
                host=self.hostname,
                username=self.username,
                password=self.password,
                port=self.port,
                cnopts=cnopts
            )
        except Exception as err:
            raise Exception(err)
        finally:
            print(f"Connected to {self.hostname} as {self.username}.")

    def disconnect(self):
        """Closes the sftp connection"""
        self.connection.close()
        print(f"Disconnected from host {self.hostname}")

    def listdir(self, remote_path):
        """lists all the files and directories in the specified path and returns them"""
        for obj in self.connection.listdir(remote_path):
            yield obj

    def listdir_attr(self, remote_path):
        """lists all the files and directories (with their attributes) in the specified path and returns them"""
        for attr in self.connection.listdir_attr(remote_path):
            yield attr

    def download(self, remote_path, target_local_path):
        """
        Downloads the file from remote sftp server to local.
        Also, by default extracts the file to the specified target_local_path
        """

        try:
            print(
                f"downloading from {self.hostname} as {self.username} [(remote path : {remote_path});(local path: {target_local_path})]"
            )

            # Create the target directory if it does not exist
            path, _ = os.path.split(target_local_path)
            if not os.path.isdir(path):
                try:
                    os.makedirs(path)
                except Exception as err:
                    raise Exception(err)

            # Download from remote sftp server to local
            self.connection.get(remote_path, target_local_path)
            print("download completed")

        except Exception as err:
            raise Exception(err)

    def upload(self, source_local_path, remote_path):
        """
        Uploads the source files from local to the sftp server.
        """

        try:
            print(
                f"uploading to {self.hostname} as {self.username} [(remote path: {remote_path});(source local path: {source_local_path})]"
            )

            # Download file from SFTP
            self.connection.put(source_local_path, remote_path)
            print("upload completed")

        except Exception as err:
            raise Exception(err)


if __name__ == "__main__":

    sftp_url = os.environ.get("SFTPTOGO_URL")

    if not sftp_url:
        print("First, please set environment variable SFTPTOGO_URL and try again.")
        exit(0)

    parsed_url = urlparse(sftp_url)

    sftp = Sftp(
        hostname=parsed_url.hostname,
        username=parsed_url.username,
        password=parsed_url.password
    )

    # Connect to SFTP
    sftp.connect()

    # Lists files with attributes of SFTP
    my_path = "/"
    print(f"List of files with attributes at location {my_path}:")
    print("mode", "size", "a    time", "make_time", "filename", sep="\t\t\t")
    for file in sftp.listdir_attr(my_path):
        print(file.st_mode, file.st_size, file.st_atime, file.st_mtime, file.filename, sep="\t\t\t")

    # Upload files to SFTP location from local
    html_file = "Tabelle_U10.html"
    sftp.upload(".\\" + html_file, "/" + html_file)

    html_file = "Tabelle_U12.html"
    sftp.upload(".\\" + html_file, "/" + html_file)

    html_file = "Tabelle_H3.html"
    sftp.upload(".\\" + html_file, "/" + html_file)

    # Lists files of SFTP location after upload
    print(f"List of files at location {my_path}:")
    print([f for f in sftp.listdir(my_path)])

    # Download files from SFTP
    sftp.download("/" + html_file, ".\\" + html_file + "_download")

    # Disconnect from SFTP
    sftp.disconnect()
