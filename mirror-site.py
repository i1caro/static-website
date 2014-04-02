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


def to_relative(directorypath, match):
  split_url = match.split('/')
  split_path = directorypath.split('/')[1:]
  number_of_similar = 0
  for path_dir, path_url in zip(split_path, split_url):
    if path_dir != path_url:
      break
    number_of_similar += 1

  result = '/'.join(split_url[number_of_similar:])
  different_paths = len(split_path) - number_of_similar
  if different_paths > 0:
    return '/'.join(['..' for o in range(different_paths)]) + '/' + result
  return result


def turn_full_path_links_into_relative(site):
  regex_url = re.compile('[\'\"](https?\:\/\/{}\/)(.+?)[\'\"]'.format(site))
  for directorypath, directoryname, files in os.walk(site):
    for filename in files:
      current_file = os.path.join(directorypath, filename)
      with open(current_file, 'r') as opened_file:
        content = opened_file.read()

      with open(current_file, 'w') as opened_file:
        matches = regex_url.findall(content)
        if not matches:
          continue
        matches = set(matches)
        print directorypath + '/' + filename
        for match_site, match in matches:
          relative_url = to_relative(directorypath, match)
          absolute_url = match_site + match
          print ' .... %s' % absolute_url
          print ' .... %s' % relative_url
          content = content.replace(absolute_url, relative_url)
        opened_file.write(content)


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Mirrors website and merges the GET parameters into a single file needs wget to be installed.')
  parser.add_argument('site', metavar='Url', type=str, nargs='?', help='Site url or path')
  parser.add_argument('-d', '--dont-mirror', action='store_true', help='dont mirror the website')
  args = parser.parse_args()

  sites = [
    'www.elastichosts.com',
    'www.elastichosts.co.uk',
    'www.elastichosts.com.hk',
    'www.elastichosts.nl',
    'www.elastichosts.com.au'
  ]
  if args.site:
    sites = list(args.site)

  for site in sites:
    if not args.dont_mirror:
      print 'Mirroring {}'.format(site)
      mirror(site)
      print 'Merging files'
    merge_files(site)
    turn_full_path_links_into_relative(site)


