#!/usr/bin/env python3
# smugdl v0.8

from pathlib import Path
from smugmug import SmugMug
import argparse, sys, os, hashlib, json, time, mimetypes, fnmatch, subprocess

#
# SmugMug modules
#

def get_child_nodes(self, parent_node_id):
    """
    Get a list of child nodes given the parents node_id
    """
    start = 1
    stepsize = 100
    nodes = []
    while(True):
        params = {'start': start, 'count': stepsize}
        response = self.request('GET', self.smugmug_api_base_url + "/node/" + parent_node_id + "!children", params=params, headers={'Accept': 'application/json'})
        for node in (response['Response']['Node'] if 'Node' in response['Response'] else []):
            #print(node)
            if node['Type'] == 'Album':
                album_key = get_album_key(smugmug, node["NodeID"])
                nodes.append({"Name": node["Name"], "NodeID": node["NodeID"], "HasChildren": node["HasChildren"], "Type": node["Type"], "Key": album_key})
            #print(nodes)
        if 'NextPage' in response['Response']['Pages']:
            start += stepsize
        else:
            break
    return nodes

def get_album_key(self, node_id):
    response = smugmug.request('GET', smugmug.smugmug_api_base_url + "/node/"+node_id, headers={'Accept': 'application/json'})
    albumkey = response['Response']['Node']['Uris']['Album']['Uri'].rsplit('/',1)[1]
    #print(albumkey)
    return albumkey

def download_album(self, album):
    download_path = Path(args.directory + '/' + album['Name'])
    download_path.mkdir(parents=True, exist_ok=True)
    album_images = self.get_album_images(album['Key'])
    #print(album)
    #print(len(album_images))
    for image in album_images:

        filepath = download_path/image['FileName']
        sys.stdout.write('Checking ' + str(filepath) + '... ')
        sys.stdout.flush()
        if filepath.is_file():
            try:
                image_data = open(filepath, 'rb').read()
                filehash = hashlib.md5(image_data).hexdigest()
                if filehash == image['ArchivedMD5']:
                    print('File is the same, skipping.')
                    sys.stdout.flush()
                else:
                    sys.stdout.write('File has changed, updating... ')
                    sys.stdout.flush()
                    smugmug.download_image(image_info = image, image_path = str(filepath))
                    print('Done')
            except IOError as e:
                print("I/O error({0}): {1}".format(e.errno, e.strerror))
                raise
            #print('File already exists, skipping.')
            sys.stdout.flush()
            #break
        else:
            smugmug.download_image(image_info = image, image_path = str(filepath))
    #print(album['NodeID'])


def validate_args(args):
    #global root_node_id
    global starting_node_id
    global parent_node_id
    global EXIV_CMD

    #confirm starting local directory exists
    if not os.path.isdir(args.directory):
        print("Destination directory ("+ args.directory + ") does not exist")
        sys.exit(1)

    #confirm starting SmugMug node is a folder (not a gallery)
    #print(args.url)
    smugmug = SmugMug(args.verbose)
    response = smugmug.request('GET', smugmug.smugmug_api_base_url + "!weburilookup",
        headers={'Accept': 'application/json'},
        params={'WebUri': args.url})
    #print(response)
    try:
        node_id = response['Response']['Folder']['NodeID']
    except:
        print("URL must be a path to a folder node in SmugMug.")
        sys.exit(1)
    starting_node_id = node_id

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Download albums from SmugMug for use in a digital photoframe.')
    parser.add_argument('url', type=str, help='Full url to SmugMug folder that contains the galleries to be downloaded')
    parser.add_argument('directory', type=str, help='Local directory to contain the downloaded galleries')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', default=False, help='verbose output')
    args = parser.parse_args()

    smugmug = SmugMug(args.verbose)

    #validate cli arguments and sets starting_node_id as the given starting point
    validate_args(args)
    #print(starting_node_id)
    albums = get_child_nodes(smugmug, starting_node_id)

    for album in albums:
        download_album(smugmug, album)
