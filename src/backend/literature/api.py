from flask import request
from ...db.services import DocumentService
from .. import api
from .utils import *


literature_api = api.Blueprint('literature_api', __name__)


@literature_api.route('/api/document', methods=['GET'])
def load_documents():
    def sort_title(x):
        n = x.title.strip()
        for pref in ['A ', 'The ']:
            if n.lower().startswith(pref.lower()):
                n = n[len(pref):]
                break
        # n = f'{n}|{x.language.iso_code}'
        return n

    documents = sorted(
        DocumentService.get_all(), key=lambda x: sort_title(x)
    )
    return api.Result({
        'documents': [serializable_document(t) for t in documents]
    })


@literature_api.route('/api/document/<int:document_id>', methods=['GET'])
def load_document(document_id):
    document = DocumentService.get(document_id)
    if not document:
        raise api.Exception('Document not found', 404)

    return api.Result({'document': serializable_document(document)})


@literature_api.route(
    '/api/document/<int:document_id>/content', methods=['GET']
)
def load_content(document_id):
    document = DocumentService.get(document_id)
    if not document:
        raise api.Exception('Document not found', 404)

    try:
        return api.Result({
            'content': load_document_files(
                document.file_url,
                filename=request.args.get('filename')
            ),
        })
    except Exception:
        import traceback
        traceback.print_exc()
        raise
