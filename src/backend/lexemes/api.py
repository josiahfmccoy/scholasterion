from ...db.services import CollectionService, TokenService
from .. import api
from .utils import *


lexeme_api = api.Blueprint('lexeme_api', __name__)


@lexeme_api.route('/api/document/<int:document_id>/token/<string:token_id>', methods=['GET'])
def get_token_info(document_id, token_id):
    document = CollectionService.Documents.get(document_id)
    if not document:
        raise api.Exception('Document not found', 404)

    token = TokenService.get(identifier=token_id, document_id=document.id)
    if not token:
        lang = document.collection.language
        if lang.iso_code in ['grc', 'lat']:
            try:
                token = parse_loegion(document, token_id)
            except Exception:
                import traceback
                traceback.print_exc()
                raise

    return api.Result({'token': serializable_token(token)})
