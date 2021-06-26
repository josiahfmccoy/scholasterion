from db.services import CollectionService
from .. import api
from .utils import *


literature_api = api.Blueprint('literature_api', __name__)


@literature_api.route('/api/collection', methods=['GET'])
def load_collections():
    def sort_title(x):
        n = x.title.strip()
        if n.startswith('A '):
            n = n[2:]
        elif n.startswith('The '):
            n = n[4:]
        # n = f'{n}|{x.language.iso_code}'
        return n

    collections = sorted(
        CollectionService.get_all(parent_id=None),
        key=lambda x: sort_title(x)
    )
    return api.Result({
        'collections': [serializable_collection(t) for t in collections]
    })


@literature_api.route('/api/collection/<int:collection_id>', methods=['GET'])
def load_collection(collection_id):
    collection = CollectionService.get(collection_id)
    if not collection:
        raise api.Exception('Collection not found', 404)

    return api.Result({'collection': serializable_collection(collection)})


@literature_api.route('/api/document/<int:document_id>', methods=['GET'])
def load_document(document_id):
    document = CollectionService.Documents.get(document_id)
    if not document:
        raise api.Exception('Document not found', 404)

    return api.Result({'document': serializable_document(document)})
