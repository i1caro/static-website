#!/usr/bin/env python

"""
SYNOPSIS

  python mirror-site [-d, -dont-download]

DESCRIPTION

  Mirror our website to www.elastichosts.com

  -d, -dont-download : just trims the files doesn't download from the web


"""
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
  parser.add_argument('site', metavar='Url', type=str, nargs='?', help='Site url or path')
  parser.add_argument('-d', '--dont-mirror', action='store_true', help='dont mirror the website')
  args = parser.parse_args()

  site = args.site or 'www.elastichosts.com'

  if not args.dont_mirror:
    print 'Mirroring {}'.format(site)
    mirror(site)
    print 'Merging files'
  merge_files(site)
