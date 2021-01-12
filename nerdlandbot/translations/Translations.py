import pandas
import codecs

from os import path

translations = {}


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

    return translations_for_key[language]


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
