from db.services import TextService, TokenService
from .. import api
from .utils import *


lexeme_api = api.Blueprint('lexeme_api', __name__)


@lexeme_api.route('/api/volume/<int:volume_id>/token/<string:token_id>', methods=['GET'])
def get_token_info(volume_id, token_id):
    volume = TextService.Volumes.get(volume_id)
    if not volume:
        raise api.Exception('Text not found', 404)

    token = TokenService.get(identifier=token_id, volume_id=volume.id)
    if not token:
        lang = volume.text.language
        if lang.iso_code in ['grc', 'lat']:
            try:
                token = parse_loegion(volume, token_id)
            except Exception:
                import traceback
                traceback.print_exc()
                raise

    return api.Result({'token': serializable_token(token)})
