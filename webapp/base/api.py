import os
from flask import current_app, request
from .. import api


base_api = api.Blueprint('base_api', __name__)


@base_api.route('/api/texts', methods=['GET'])
def load_texts():
    t = []

    for fname in os.listdir(current_app.static_path('data')):
        if not fname.endswith('.xml'):
            continue
        fname = fname.rsplit('.', 1)[0]
        t.append({
            'label': fname.replace('-', ' ').title(),
            'value': fname
        })

    return api.Result({'texts': sorted(t, key=lambda x: x['label'])})


@base_api.route('/api/text', methods=['GET'])
def load_text():
    name = request.args.get('name')

    filename = os.path.join(
        current_app.static_folder,
        'data',
        f'{name}.xml'
    )

    with open(filename, 'r', encoding='utf-8') as f:
        text = '\n'.join(f.readlines())

    mappings = {
        'text': 'div class="text"',
        'title': 'h3 class="section-title"',
        'content': 'div',
        'section': 'p class="section"',
        'line': 'div class="line"',
        'word': 'span',
        'form': 'span class="word-form"',
        'lemma': 'span class="lemma" style="display: none;"',
        'headword': 'span class="headword"',
        'gloss': 'span class="gloss"'
    }

    for k, v in mappings.items():
        text = text.replace(f'<{k}', f'<{v}')
        text = text.replace(f'</{k}', f'</{v}')

    return api.Result({'content': text})


@base_api.route('/api/text', methods=['POST'])
def save_text():
    document_name = request.form.get('document_name')
    text_title = request.form.get('text_title')
    if not text_title:
        raise api.Exception('Must have a title', 400)

    text_content = request.form.get('text_content')

    with current_app.open_static(f'data/{text_title}.txt', 'w', encoding='utf-8') as f:
        f.writelines([
            document_name.strip() or '...',
            '\n\n',
            text_title.strip(),
            '\n\n',
            *text_content.strip().split('\n'),
            '\n'
        ])

    return api.Result({'text_name': text_title, 'text_content': text_content})
