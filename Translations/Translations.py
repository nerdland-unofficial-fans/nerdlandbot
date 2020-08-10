import pandas

dictionary = {}
initialized = False

df = pandas.read_csv("Translations/Translations.csv")
df = df.set_index('Key', drop=True)

for row in df.iterrows():
    dictionary[row[0]] = row[1].to_dict()

def get_text(key, culture):
    if not dictionary.keys().__contains__(key):
        return f'[{culture}] {key} 1'

    values = dictionary[key]

    if not values.keys().__contains__(culture):
        return f'[{culture}] {key} 2'

    return values[culture]
