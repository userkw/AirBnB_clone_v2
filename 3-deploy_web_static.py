#!/usr/bin/python3
"""
Fabric script that creates and distributes an archive to the web servers.

execute: fab -f 3-deploy_web_static.py deploy -i ~/.ssh/id_rsa -u ubuntu
"""

from fabric.api import env, local, put, run
from datetime import datetime
from os.path import exists, isdir
import os

# Define the hosts for deployment
env.hosts = ['54.83.172.21', '100.25.135.230']

def do_pack():
    """Generates a tgz archive."""
    try:
        # Get the current date and time for the archive name
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        # Ensure the versions directory exists
        if not isdir("versions"):
            local("mkdir versions")
        # Ensure my_index.html exists
        if not os.path.exists('web_static/my_index.html'):
            with open('web_static/my_index.html', 'w') as f:
                f.write('<html><body><h1>Test</h1></body></html>')
        # Create the archive
        file_name = "versions/web_static_{}.tgz".format(date)
        local("tar -cvzf {} web_static".format(file_name))
        return file_name
    except Exception as e:
        print(f"Error: {e}")
        return None

def do_deploy(archive_path):
    """Distributes an archive to the web servers."""
    if not exists(archive_path):
        return False
    try:
        # Extract the archive name and directory name
        file_n = archive_path.split("/")[-1]
        no_ext = file_n.split(".")[0]
        path = "/data/web_static/releases/"
        
        # Upload the archive to /tmp/ directory on the server
        put(archive_path, '/tmp/')
        # Create the target directory
        run(f'mkdir -p {path}{no_ext}/')
        # Extract the archive to the target directory
        run(f'tar -xzf /tmp/{file_n} -C {path}{no_ext}/')
        # Remove the archive from /tmp/
        run(f'rm /tmp/{file_n}')
        # Move the extracted files to the target directory
        run(f'mv {path}{no_ext}/web_static/* {path}{no_ext}/')
        # Remove the now empty web_static directory
        run(f'rm -rf {path}{no_ext}/web_static')
        # Remove the current symlink
        run('rm -rf /data/web_static/current')
        # Create a new symlink to the new release
        run(f'ln -s {path}{no_ext}/ /data/web_static/current')
        
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def deploy():
    """Creates and distributes an archive to the web servers."""
    # Create the archive
    archive_path = do_pack()
    if archive_path is None:
        return False
    # Deploy the archive
    return do_deploy(archive_path)
