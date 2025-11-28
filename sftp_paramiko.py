import os
from urllib.parse import urlparse

import paramiko


def sftp_connect(hostname: str, port: int, username: str, password: str) -> None:
    # Create an SSH client
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Connect to the SFTP server
    ssh_client.connect(hostname=str(hostname), port=int(port), username=str(username), password=str(password))

    # Create an SFTP session
    sftp = ssh_client.open_sftp()

    # Now you can perform SFTP operations
    # Upload files to SFTP location from local
    html_files = ["Tabelle_U10.html", "Tabelle_U12.html", "Tabelle_H3.html"]
    for html_file in html_files:
        sftp.put(html_file, "/" + html_file)

    # Upload files to SFTP location from local
    for html_file in html_files:
        sftp.get("/" + html_file, html_file + "_download")

    sftp.close()

    ssh_client.close()

    delete_downloads = input("You want to keep the downloads? (y/n): ")
    if delete_downloads == "n":
        for html_file in html_files:
            os.remove(".\\" + html_file + "_download")


if __name__ == '__main__':

    sftp_url = os.environ.get("SFTPTOGO_URL")

    if not sftp_url:
        print("First, please set environment variable SFTPTOGO_URL and try again.")
        exit(0)

    parsed_url = urlparse(sftp_url)

    sftp_connect(hostname=parsed_url.hostname, port=22, username=parsed_url.username, password=parsed_url.password)
