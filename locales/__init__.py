from locales import tr, en, de, fr, ar, ru

LOCALES = {
    "tr": tr.T,
    "en": en.T,
    "de": de.T,
    "fr": fr.T,
    "ar": ar.T,
    "ru": ru.T,
}

DEFAULT_LANG = "tr"


def get_text(lang: str, key: str, **kwargs) -> str:
    locale = LOCALES.get(lang, LOCALES[DEFAULT_LANG])
    text = locale.get(key, LOCALES[DEFAULT_LANG].get(key, key))
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text


def t(lang: str, key: str, **kwargs) -> str:
    return get_text(lang, key, **kwargs)
