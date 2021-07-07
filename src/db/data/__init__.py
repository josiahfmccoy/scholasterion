from ...workbench.parsing.loegion import norm_word
from ..services import LexemeService, LanguageService
from .ancient_greek import CORE_VOCAB as grc_vocab

__all__ = ['load_defaults']


def add_vocab(vocab, lang):
    for lem, defs in vocab.items():
        lex = LexemeService.get_or_create(
            lemma=norm_word(lem),
            language_id=lang.id
        )
        if 'gloss' in defs:
            lex.gloss = defs['gloss']

        forms = defs.get('forms', [])
        if lem not in forms and lex.lemma not in forms:
            forms.append(lem)
        for word in forms:
            if isinstance(word, str):
                word = {'form': word}

            w = LexemeService.Words.get_or_create(
                form=norm_word(word['form']),
                lexeme_id=lex.id,
                no_commit=True
            )
            if 'gloss' in word:
                w.gloss = word['gloss']

    LexemeService.commit()


def load_defaults():
    add_vocab(grc_vocab, LanguageService.get(iso_code='grc'))
