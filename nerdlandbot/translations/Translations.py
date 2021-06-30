import csv

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
        get_text("friendship", language)
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
    if translation_key not in translations:
        return f'[{language}] {translation_key} 1'

    translations_for_key = translations[translation_key]

    if language not in translations_for_key:
        return f'[{language}] {translation_key} 2'

    language_translation = translations_for_key[language]
    if FOEMP in language_translation:
        language_translation = language_translation.replace(
            FOEMP, translate_adjective(language),
        )

    return language_translation


def load_translations() -> None:
    with open(path.join(path.dirname(__file__), "Translations.csv"), newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = row['Key']
            del row['Key']
            translations[key] = {k: v.encode().decode('unicode-escape') for k, v in row.items()}
