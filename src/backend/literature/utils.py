import json
import os
import requests
import shutil
import tempfile
from flask import current_app
from lxml import etree
from zipfile import ZipFile
from ...db.services import DocumentService
from ..languages.utils import serializable_language

__all__ = [
    'serializable_document',
    'load_texts',
    'load_document_files'
]


def serializable_document(document):
    if document is None:
        return None
    s = {
        'id': document.id,
        'title': document.title,
        'author': document.author,
        'language': serializable_language(document.language),
        'file_url': document.file_url
    }
    return s


def load_document_files(file_url, filename=None):
    if file_url.startswith('http'):
        r = requests.get(file_url)
        if not r.status_code == 200:
            raise ValueError('Unable to load document contents')
        content = r.content

    else:
        content = current_app.static_path(f'data/{file_url}')

    with tempfile.TemporaryDirectory() as tempdir:
        with ZipFile(content, 'r') as z:
            z.extractall(tempdir)

        if filename:
            parser = etree.XMLParser(remove_blank_text=True)
            xml_content = etree.parse(os.path.join(tempdir, filename), parser)
            return etree.tostring(xml_content).decode('utf-8')

        with open(os.path.join(tempdir, 'index.json'), 'r', encoding='utf-8') as f:
            index = json.load(f)

    return index


def load_texts(app):
    text_folder = os.getenv('TEXTS_FOLDER')
    if not text_folder:
        return

    app.remove_static('data')
    data_dir = os.path.join(app.static_folder, 'data')
    os.makedirs(data_dir)

    folders = [
        x.replace('\\', '/')
        for x in os.listdir(text_folder)
        if os.path.isdir(os.path.join(text_folder, x))
    ]
    if not folders:
        return

    db_docs = DocumentService.get_all()

    for doc in db_docs:
        fname = doc.file_url.replace('\\', '/')
        fname = fname.split('data/')[-1]

        name = fname.rsplit('.', 1)[0]

        if name not in folders:
            continue

        print(f'Updating {fname} ...')

        with tempfile.TemporaryDirectory() as tempdir:
            zipfile = os.path.join(tempdir, name)
            dirname = os.path.dirname(zipfile)
            if not os.path.isdir(dirname):
                os.makedirs(dirname)

            shutil.make_archive(zipfile, 'zip', os.path.join(text_folder, name))
            zipfile += '.zip'
            shutil.copy2(zipfile, data_dir)
