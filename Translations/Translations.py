import pandas
import codecs

dictionary = {}


def get_text(key: str, language: str) -> str:
    """
    Gets the translated text for a given key in the provided language.
    :param key: The key to be translated. (str)
    :param language: The language to translate to. (str)
    :return: The translated key. (str)
    """
    if not dictionary.keys().__contains__(key):
        return f'[{language}] {key} 1'

    translations = dictionary[key]

    if not translations.keys().__contains__(language):
        return f'[{language}] {key} 2'

    return translations[language]


# Read csv
df = pandas.read_csv("Translations/Translations.csv")

# Remove artificial index
df = df.set_index('Key', drop=True)

# Process dataframe
for row in df.iterrows():
    tmp = row[1].to_dict()
    values = {}
    for culture in tmp.keys():
        values[culture] = codecs.decode(tmp[culture], 'unicode_escape')

    dictionary[row[0]] = values
