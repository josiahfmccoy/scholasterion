import os
from flask import current_app
from lxml import etree
from ...db.services import DocumentService
from ..languages.utils import serializable_language
from ..utils import recursive_listdir

__all__ = [
    'serializable_document', 'serializable_collection',
    'load_texts'
]


def serializable_document(document, with_collection=True):
    if document is None:
        return None
    s = {
        'id': document.id,
        'long_title': document.long_title,
        'title': document.title,
        'author': document.author,
        'order': document.order,
        'file_url': document.file_url
    }
    if with_collection:
        s['collection'] = serializable_collection(document.collection)
    return s


def serializable_collection(collection, with_parent=True, with_sections=True):
    if collection is None:
        return None
    s = {
        'id': collection.id,
        'long_title': collection.long_title,
        'title': collection.title,
        'author': collection.author,
        'order': collection.order,
        'language': serializable_language(collection.language),
        'documents': [
            serializable_document(d, with_collection=False)
            for d in sorted(collection.documents, key=lambda x: x.order)
        ]
    }
    if with_sections:
        s['sections'] = [
            serializable_collection(c, with_parent=False)
            for c in sorted(collection.sections, key=lambda x: x.order)
        ]
    if with_parent:
        s['parent'] = serializable_collection(collection.parent, with_sections=False)
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

    db_docs = DocumentService.get_all()

    for doc in db_docs:
        fname = doc.file_url.replace('\\', '/')
        fname = fname.split('data/')[-1]

        if fname not in files:
            continue

        add_document(
            app=app, id=doc.id, filepath=os.path.join(text_folder, fname),
            file_url=fname
        )


def add_document(*args, app=None, filepath=None, file_url=None, **kwargs):
    doc = DocumentService.get_or_create(*args, **kwargs, no_commit=True)

    if app is None:
        app = current_app

    if filepath:
        fname = file_url or os.path.basename(filepath)
        app.logger.debug(f'Updating {fname} ...')

        parser = etree.XMLParser(remove_blank_text=True)
        txt = etree.parse(filepath, parser)

        with app.open_static(f'data/{fname}', 'wb') as f:
            f.write(etree.tostring(txt, encoding='utf-8', pretty_print=True))

        doc.file_url = fname

    DocumentService.commit()
