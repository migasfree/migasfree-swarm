#!/usr/bin/python3

import os
import sys
import shutil
import fnmatch
import requests
import json

from django.conf import settings
from requests_toolbelt.multipart.encoder import MultipartEncoder

from migasfree.utils import get_secret, get_setting, read_file, write_file
from migasfree.core.pms import get_pms
from migasfree.core.validators import build_magic
from migasfree.secure import wrap, unwrap

SERVER_URL = f'http://{get_setting("MIGASFREE_FQDN")}'
API_URL = f'{SERVER_URL}/api/v1/token'
UPLOAD_PKG_URL = f'{SERVER_URL}/api/v1/safe/packages/'

PRIVATE_KEY = os.path.join(get_setting('MIGASFREE_KEYS_DIR'), 'migasfree-packager.pri')
PUBLIC_KEY = os.path.join(get_setting('MIGASFREE_KEYS_DIR'), 'migasfree-server.pub')
TMP_PATH = '/tmp'
OLD_STORE_TRAILING = 'STORES'


def get_auth_token():
    return f'Token {get_secret("token_pms")}'


def headers():
    return {'Authorization': get_auth_token()}


def get_locations():
    locations = []

    for root, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
        for filename in fnmatch.filter(dirnames, get_setting('MIGASFREE_STORE_TRAILING_PATH')):
            locations.append(os.path.join(root, filename))

    return locations


def migrate_structure(projects):
    for prj in projects:
        source = os.path.join(
            settings.MEDIA_ROOT,
            prj['name'],
            OLD_STORE_TRAILING
        )
        if os.path.exists(source):
            target = os.path.join(
                settings.MEDIA_ROOT,
                prj['slug'],
                get_setting('MIGASFREE_STORE_TRAILING_PATH')
            )
            shutil.move(source, target)
            print(f'{source} migrated to {target} path')
            shutil.rmtree(os.path.join(settings.MEDIA_ROOT, prj['name']))


def upload_package(data, upload_files):
    data = json.dumps({
        'msg': wrap(
            data,
            sign_key=PRIVATE_KEY,
            encrypt_key=PUBLIC_KEY
        ),
        'project': data['project']
    })

    my_magic = build_magic()

    files = []
    for _file in upload_files:
        content = read_file(_file)

        tmp_file = os.path.join(TMP_PATH, os.path.basename(_file))
        write_file(tmp_file, content[0:1023])  # only header
        mime = my_magic.file(tmp_file)
        os.remove(tmp_file)

        files.append(
            ('file', (_file, content, mime))
        )

    data = json.loads(data)

    fields = data
    fields.update(dict(files))
    data = MultipartEncoder(fields=fields)
    headers = {'content-type': data.content_type}

    req = requests.post(UPLOAD_PKG_URL, data=data, headers=headers)

    if 'msg' in req.json():
        response = unwrap(
            req.json()['msg'],
            decrypt_key=PRIVATE_KEY,
            verify_key=PUBLIC_KEY
        )

        return response

    return req.json()


def migrate_packages():
    locations = get_locations()
    packages = []

    for location in locations:
        len_location = len(location.replace(settings.MEDIA_ROOT, '').split('/'))
        for root, _, filenames in os.walk(location):
            for _file in filenames:
                len_candidate = len(
                    os.path.join(root, _file).replace(settings.MEDIA_ROOT, '').split('/')
                )
                if len_location == (len_candidate - 2):
                    parts = root.replace(settings.MEDIA_ROOT, '').split('/')
                    packages.append({
                        'location': os.path.join(root, _file),
                        'fullname': _file,
                        'project': parts[1],
                        'store': parts[-1],
                    })

    if len(packages) > 0:
        for item in packages:
            req = requests.get(
                f'{API_URL}/packages/',
                {
                    'fullname__icontains': item['fullname'],
                    'project__name__icontains': item['project'],
                    'store__name__icontains': item['store']
                },
                headers=headers()
            )

            response = req.json()
            if response['count'] == 1:
                package = response['results'][0]
                print(f'Migrating {package["fullname"]}...')
                ret = upload_package(
                    data={
                        'project': package['project']['name'],
                        'store': package['store']['name'],
                        'is_package': True
                    },
                    upload_files=[item['location']]
                )
                print(ret)  # DEBUG


def migrate_package_sets():
    locations = get_locations()
    package_sets = []

    for location in locations:
        len_location = len(location.replace(settings.MEDIA_ROOT, '').split('/'))
        for root, dirnames, filenames in os.walk(location):
            for dirname in dirnames:
                for _root, _dir, _filenames in os.walk(os.path.join(location, dirname)):
                    len_candidate_set = len(_root.replace(settings.MEDIA_ROOT, '').split('/'))
                    if _filenames and not _dir and len_candidate_set - len_location > 1:
                        parts = _root.replace(settings.MEDIA_ROOT, '').split('/')
                        package_sets.append({
                            'location': _root,
                            'name': parts[-1],
                            'project': parts[1],
                            'store': parts[-2],
                            'packages': _filenames
                        })

    if len(package_sets) > 0:
        for item in package_sets:
            req = requests.get(
                f'{API_URL}/package-sets/',
                {
                    'name': item['name'],
                    'project__name__icontains': item['project'],
                    'store__name__icontains': item['store']
                },
                headers=headers()
            )

            response = req.json()
            if response['count'] == 1:
                package_set = response['results'][0]
                print(f'Migrating {package_set["name"]}...')

                files = []
                for package in item['packages']:
                    files.append(
                        (
                            'files',
                            (
                                package,
                                open(os.path.join(item['location'], package), 'rb').read(),
                                get_pms(package_set['project']['pms']).mimetype[0]
                            )
                        )
                    )

                mp_encoder = MultipartEncoder(fields=files)
                response = requests.patch(
                    f'{API_URL}/package-sets/{package_set["id"]}/',
                    data=mp_encoder,
                    headers={
                        'Authorization': get_auth_token(),
                        'Content-Type': mp_encoder.content_type
                    }
                )
                print(response.text)

                if response.status_code == requests.codes.ok:
                    print(f'Package set {package_set["name"]} migrated successfully!!!')
                else:
                    print(f'Package set {package_set["name"]} NOT migrated!')

                print()


def get_projects():
    req = requests.get(
        f'{API_URL}/projects/',
        headers=headers()
    )
    if req.status_code != requests.codes.ok:
        print('Invalid credentials. Review token.')
        sys.exit(1)

    response = req.json()
    if 'detail' in response:
        print(response['detail'])
        sys.exit(1)

    req = requests.get(
        f'{API_URL}/projects/',
        {
            'page_size': response['count']
        },
        headers=headers()
    )
    response = req.json()

    return response['results']


def update_projects(projects):
    for prj in projects:
        if prj['pms'].startswith('apt'):
            prj['pms'] = 'apt'

        prj['platform'] = prj['platform']['id']
        req = requests.patch(f'{API_URL}/projects/{prj["id"]}/', prj, headers=headers())
        if req.status_code == requests.codes.ok:
            print(f'Project {prj["name"]} updated')
        else:
            print(f'Project {prj["name"]} update failed!!! ({req.status_code})')


def regenerate_metadata():
    req = requests.get(
        f'{API_URL}/deployments/internal-sources/',
        headers=headers()
    )
    response = req.json()

    req = requests.get(
        f'{API_URL}/deployments/internal-sources/',
        {
            'page_size': response['count']
        },
        headers=headers()
    )
    response = req.json()
    for deploy in response['results']:
        req = requests.get(
            f'{API_URL}/deployments/internal-sources/{deploy["id"]}/metadata/',
            headers=headers()
        )
        if req.status_code == requests.codes.ok:
            print(f'Deployment {deploy["name"]} regenerated')
        else:
            print(f'Deployment {deploy["name"]} regenerating failed!!!')


if __name__ == '__main__':
    projects = get_projects()
    update_projects(projects)
    migrate_structure(projects)
    migrate_packages()
    migrate_package_sets()
    regenerate_metadata()
