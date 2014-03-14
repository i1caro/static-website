from fabric.api import run
from fabric.contrib.files import append, exists
from fabric.context_managers import settings, cd


"""
server_name www.elastichosts.com; is not permanent needs to be tested
"""


def setup():
    """
    Mirror and server our website in a server

    Assumes that we're touching a Ubuntu server apt-get
    Fabric will prompt for host info; this should be toor@<IP> with the VNC password provided on prompt
    """
    install_software()
    setup_directories()
    download_site()
    setup_nginx()


def no_donwload_setup():
    install_software()
    setup_directories()
    setup_nginx()


def install_software():
    run('apt-get install nginx')


def setup_directories():
    run('mkdir -p /var/www')
    if not exists('/var/www/nginx.conf'):
        append('/var/www/nginx.conf', NGINX_CONFIG)
    if not exists('/var/www/mirror-site.py'):
        append('/var/www/mirror-site.py', PYTHON_SCRIPT)
    with settings(warn_only=True):
        run('ln -s /var/www/nginx.conf /etc/nginx/sites-enabled/')
        run('rm /etc/nginx/sites-enabled/default')
    run('chmod 755 /var/www/mirror-site.py')
    with settings(warn_only=True):
        run('ln -s /var/www/mirror-site.py /etc/cron.daily/ -v')


def download_site():
    with cd('/var/www'):
        run('./mirror-site.py')


def setup_nginx():
    run('chown -R www-data:www-data /var/www')
    run('service nginx restart')

PYTHON_SCRIPT = """\
#!/usr/bin/env python

from subprocess import call
import argparse
import os
import re

GETREQUEST = re.compile('(.*)\?.*$')


def mirror(site):
  call(['wget', '--mirror', '--page-requisites', site])
  # Also add special files that wget ignores
  call(['wget', '--mirror', '--page-requisites', 'http://{}/wp-includes/js/comment-reply.js'.format(site)])
  call(['wget', '--mirror', '--page-requisites', 'http://{}/wp-includes/js/jquery/jquery.js'.format(site)])


def merge_files(site):
  for directorypath, directoryname, files in os.walk(site):
    file_list = set(files)
    for filename in files:
      match = GETREQUEST.match(filename)
      if match:
        clean_name = match.groups()[0]
        old_path = os.path.join(directorypath, filename)
        if clean_name in file_list:
          os.remove(old_path)
        else:
          file_list.add(clean_name)
          new_path = os.path.join(directorypath, clean_name)
          os.rename(old_path, new_path)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Mirrors website and merges the GET parameters into a single file needs wget to be installed.')
  parser.add_argument('-d', '--dont-mirror', action='store_true', help='dont mirror the website')
  args = parser.parse_args()

  site = 'www.elastichosts.com'
  if not args.dont_mirror:
    print 'Mirroring {}'.format(site)
    mirror(site)
    print 'Merging files'
  merge_files(site)
"""

NGINX_CONFIG = """\
# You may add here your
# server {
#   ...
# }
# statements for each of your virtual hosts to this file

##
# You should look at the following URL's in order to grasp a solid understanding
# of Nginx configuration files in order to fully unleash the power of Nginx.
# http://wiki.nginx.org/Pitfalls
# http://wiki.nginx.org/QuickStart
# http://wiki.nginx.org/Configuration
#
# Generally, you will want to move this file somewhere, and start with a clean
# file but keep this around for reference. Or just disable in sites-enabled.
#
# Please see /usr/share/doc/nginx-doc/examples/ for more detailed examples.
##

server {
    listen 80 default_server;
    listen [::]:80 default_server ipv6only=on;

    root /var/www/www.elastichosts.com;
    index index.html index.htm;

    # Make site accessible from http://localhost/
    server_name www.elastichosts.com;
    #access_log  /var/www/elastic.access.log  main;

    location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to displaying a 404.
        try_files $uri $uri/ =404;
        # Uncomment to enable naxsi on this location
        # include /etc/nginx/naxsi.rules
        include /etc/nginx/mime.types;
    }
     # serve static files
        location ~ ^/(images|javascript|js|css|flash|media|static)/  {
          root    /var/www/www.elastichosts.com;
    }
}


# another virtual host using mix of IP-, name-, and port-based configuration
#
#server {
#   listen 8000;
#   listen somename:8080;
#   server_name somename alias another.alias;
#   root html;
#   index index.html index.htm;
#
#   location / {
#       try_files $uri $uri/ =404;
#   }
#}


# HTTPS server
#
#server {
#   listen 443;
#   server_name localhost;
#
#   root html;
#   index index.html index.htm;
#
#   ssl on;
#   ssl_certificate cert.pem;
#   ssl_certificate_key cert.key;
#
#   ssl_session_timeout 5m;
#
#   ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
#   ssl_ciphers "HIGH:!aNULL:!MD5 or HIGH:!aNULL:!MD5:!3DES";
#   ssl_prefer_server_ciphers on;
#
#   location / {
#       try_files $uri $uri/ =404;
#   }
#}
"""
