from db.services import TextService
from .. import api
from .utils import *


literature_api = api.Blueprint('literature_api', __name__)


@literature_api.route('/api/text', methods=['GET'])
def load_texts():
    texts = sorted(TextService.get_all(), key=lambda x: x.name + '|' + x.language.iso_code)
    return api.Result({'texts': [serializable_text(t) for t in texts]})


@literature_api.route('/api/text/<int:text_id>', methods=['GET'])
def load_text(text_id):
    text = TextService.get(text_id)
    if not text:
        raise api.Exception('Text not found', 404)

    return api.Result({'text': serializable_text(text)})


@literature_api.route('/api/volume/<int:volume_id>', methods=['GET'])
def load_volume(volume_id):
    volume = TextService.Volumes.get(volume_id)
    if not volume:
        raise api.Exception('Volume not found', 404)

    return api.Result({'volume': serializable_volume(volume)})
