#
# load useful libraries
#
import pandas as pd

#
# define enharmonic map
#
dict_enharmonic_map = {
    'Db' : ['C#', 'Db'],
    'Eb' : ['D#', 'Eb'],
    'Gb' : ['F#', 'Gb'],
    'Ab' : ['G#', 'Ab'],
    'Bb' : ['A#', 'Bb'],
    'C#' : ['Db', 'C#'],
    'D#' : ['Eb', 'D#'],
    'F#' : ['Gb', 'F#'],
    'G#' : ['Ab', 'G#'],
    'A#' : ['Bb', 'A#'],
    'C' : ['C'],
    'D' : ['D'],
    'E' : ['E'],
    'F' : ['F'],
    'G' : ['G'],
    'A' : ['A'],
    'B' : ['B'],
}

#
# create DataFrame
#
list_enharmonic = []
for key in dict_enharmonic_map.keys():
    list_enharmonic.append(
        {
            'key' : key,
            'enharmonic_equivalents' : dict_enharmonic_map[key],
        }
    )

df_enharmonic = (
    pd.DataFrame(list_enharmonic)
    .explode('enharmonic_equivalents')
    .rename(columns = {'enharmonic_equivalents' : 'enharmonic_equivalent'})
)

if __name__ == '__main__':
    print(df_enharmonic)
