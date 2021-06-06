import os
from flask import current_app
from lxml import etree
from db.services import VolumeService
from ..languages.utils import serializable_language
from ..utils import recursive_listdir

__all__ = [
    'serializable_text', 'serializable_volume',
    'load_texts'
]


def serializable_text(text):
    s = {
        'id': text.id,
        'name': text.name,
        'language': serializable_language(text.language),
        'volumes': [
            serializable_volume(v) for v in sorted(text.volumes, key=lambda x: x.order)
        ]
    }
    return s


def serializable_volume(volume):
    s = {
        'id': volume.id,
        'order': volume.order,
        'name': volume.name,
        'file_url': volume.file_url,
    }
    return s


def load_texts(app):
    text_folder = os.getenv('TEXTS_FOLDER')
    if not text_folder:
        return

    app.remove_static('data')

    files = [
        os.path.relpath(x, start=text_folder).replace('\\', '/')
        for x in recursive_listdir(text_folder)
        if x.endswith('.xml')
    ]
    if not files:
        return

    db_vols = VolumeService.get_all()

    for vol in db_vols:
        fname = vol.file_url.replace('\\', '/')
        fname = fname.split('data/')[-1]

        if fname not in files:
            continue

        add_volume(
            app=app, id=vol.id, filepath=os.path.join(text_folder, fname),
            file_url=fname
        )


def add_volume(*args, app=None, filepath=None, file_url=None, **kwargs):
    vol = VolumeService.get_or_create(*args, **kwargs, no_commit=True)

    if app is None:
        app = current_app

    if filepath:
        fname = file_url or os.path.basename(filepath)
        app.logger.debug(f'Updating {fname} ...')

        parser = etree.XMLParser(remove_blank_text=True)
        txt = etree.parse(filepath, parser)

        with app.open_static(f'data/{fname}', 'wb') as f:
            f.write(etree.tostring(txt, encoding='utf-8', pretty_print=True))

        vol.file_url = fname

    VolumeService.commit()
