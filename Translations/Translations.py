import pandas
import codecs

dictionary = {}


def get_text(key, culture):
    if not dictionary.keys().__contains__(key):
        return f'[{culture}] {key} 1'

    values = dictionary[key]

    if not values.keys().__contains__(culture):
        return f'[{culture}] {key} 2'

    return values[culture]


df = pandas.read_csv("Translations/Translations.csv")
df = df.set_index('Key', drop=True)

for row in df.iterrows():
    tmp = row[1].to_dict()
    values = {}
    for culture in tmp.keys():
        values[culture] = codecs.decode(tmp[culture], 'unicode_escape')

    dictionary[row[0]] = values

