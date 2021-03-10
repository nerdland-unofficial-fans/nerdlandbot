import pandas
import codecs
from os import path
from datetime import datetime

from discord.ext import commands

from nerdlandbot.helpers.TranslationHelper import get_culture_from_context
from nerdlandbot.helpers.constants import SATURDAY, SUNDAY, FOEMP

translations = {}

def is_weekend() -> bool:
    return datetime.now().weekday() in {SATURDAY, SUNDAY}

def translate_adjective(language: str) -> str:
    return (
        get_text("darling", language)
        if is_weekend()
        else get_text("dummy", language)
    )


def get_text(translation_key: str, language: str) -> str:
    """
    Gets the translated text for a given key in the provided language.
    :param translation_key: The key to be translated. (str)
    :param language: The language to translate to. (str)
    :return: The translated key. (str)
    """
    if not translations.keys().__contains__(translation_key):
        return f'[{language}] {translation_key} 1'

    translations_for_key = translations[translation_key]

    if not translations_for_key.keys().__contains__(language):
        return f'[{language}] {translation_key} 2'

    language_translation = translations_for_key[language]
    if FOEMP in language_translation:
        language_translation = language_translation.replace(
            FOEMP, translate_adjective(language),
        )

    return language_translation


# Read csv
translations_dataframe = pandas.read_csv(path.join(path.dirname(__file__), "Translations.csv"))

# Remove artificial index
translations_dataframe = translations_dataframe.set_index('Key', drop=True)

# Process dataframe data
for key, data in translations_dataframe.iterrows():
    dict_for_key = {}
    for culture in data.keys():
        dict_for_key[culture] = codecs.decode(data[culture], 'unicode_escape')

    translations[key] = dict_for_key
