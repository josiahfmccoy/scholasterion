import os
from lxml import etree
from db.services import VolumeService, WordService, LexemeService
from src.utils import norm_word
from ..languages.utils import serializable_language

__all__ = [
    'serializable_text', 'serializable_volume',
    'load_texts'
]


def serializable_text(text):
    s = {
        'id': text.id,
        'name': text.name,
        'language': serializable_language(text.language),
        'volumes': [serializable_volume(v) for v in text.volumes]
    }
    return s


def serializable_volume(volume):
    s = {
        'id': volume.id,
        'name': volume.name,
        'file_url': volume.file_url,
    }
    return s


def load_texts(app):
    app.remove_static('data')

    text_folder = os.getenv('TEXTS_FOLDER')

    files = [x for x in os.listdir(text_folder) if x.endswith('.xml')]
    if not files:
        return

    db_vols = VolumeService.get_all()

    parser = etree.XMLParser(remove_blank_text=True)
    for vol in db_vols:
        fname = os.path.basename(vol.file_url)
        if fname not in files:
            continue
        print(f'Updating {fname} ...')

        txt = etree.parse(os.path.join(text_folder, fname), parser)

        # lang = vol.text.language_id

        # for word in txt.xpath('//span[@class="word"]'):
        #     form = word.xpath('.//span[@class="word-form"]')[0]
        #     norm = norm_word(form.text)
        #     if not norm:
        #         continue

        #     for lem in word.xpath('.//span[@class="lemma"]'):
        #         lex = LexemeService.get_or_create(
        #             lemma=lem.text,
        #             language_id=lang
        #         )
        #         WordService.get_or_create(
        #             form=norm,
        #             lexeme=lex,
        #             no_commit=True
        #         )
        # WordService.commit()

        with app.open_static(f'data/{fname}', 'wb') as f:
            f.write(etree.tostring(txt, encoding='utf-8', pretty_print=True))
