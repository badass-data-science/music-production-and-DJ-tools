#
# Load useful libraries
#
import pandas as pd
import numpy as np
from music_production_and_DJ_tools.theory.western.enharmonics import df_enharmonic

#
# Class to define a DJ's "Camelot wheel" to facilitate
# harmonic mixing
#
class CamelotWheel():

    #
    # constructor
    #
    def __init__(
        self,
        list_chromatic_scales : list,
    ):

        self.list_chromatic_scales = list_chromatic_scales
        list_df = [CamelotWheel.create_harmonic_mixing_camelot_keys_and_transitions(x) for x in self.list_chromatic_scales]
        self.df_initial_wheel = pd.concat(list_df).drop_duplicates().reset_index(drop = True)
        self.df_initial_wheel_stacked = CamelotWheel.stack_Major_and_minor_keys(self.df_initial_wheel)
        self.df_key_nodes = self.df_initial_wheel_stacked[['key', 'camelot_key']].copy()
        self.define_key_transition_relationships()
        self.deal_with_enharmonic_equivalency()

    #
    # create initial camelot wheel
    #
    # This is static so that we can use it elsewhere
    #
    @staticmethod
    def create_harmonic_mixing_camelot_keys_and_transitions(
        pitch_class_chromatic_scale : list,
    ) -> pd.DataFrame:

        # initialize
        chromatic_distance_P5 = 7  # Perfect fifth expressed as chromatic distance
        list_circle_of_fifths = []

        # initialize the index so that during the first run
        # through the loop the index begins on the first 
        # value of the given chromatic pitch class scale
        # (usually "C" by convention):
        #
        key_index = -1 * chromatic_distance_P5

        # iterate through the circle of fifths with respect to chromatic distances
        for i in range(0, 12):

            # update the key index
            key_index = (key_index + chromatic_distance_P5) % 12

            # compute the Camelot wheel numbers for the given pitch class key
            number_minor = ((i + 4) % 12) + 1
            number_Major = ((i + 7) % 12) + 1

            # compile iteration result and append to list
            dict_key = {
                'index' : i,
                'chromatic_pitch_index' : key_index,
                'pitch_class_camelot_wheel' : pitch_class_chromatic_scale[key_index],
                'camelot_minor' : str(number_minor) + 'A',
                'camelot_Major' : str(number_Major) + 'B',
            }
            list_circle_of_fifths.append(dict_key)

        # create a DataFrame from the list of iteration results
        df = pd.DataFrame(list_circle_of_fifths)

        # ensure we are sorted properly before the following shift operators
        df = df.sort_values(by = 'index').copy()

        # define the possible directional shifts for the minor mode
        df['minor_down'] = np.roll(df['camelot_minor'], shift = 1)
        df['minor_up'] = np.roll(df['camelot_minor'], shift = -1)
        df['minor_mode_shift'] = [x.replace('A', 'B') for x in df['camelot_minor']]

        # define the possible directional shifts for the Major mode
        df['Major_down'] = np.roll(df['camelot_Major'], shift = 1)
        df['Major_up'] = np.roll(df['camelot_Major'], shift = -1)
        df['Major_mode_shift'] = [x.replace('B', 'A') for x in df['camelot_Major']]

        # keep a subset of the columns
        df = df[[
            'pitch_class_camelot_wheel',
            'camelot_minor', 'minor_down', 'minor_up', 'minor_mode_shift',
            'camelot_Major', 'Major_down', 'Major_up', 'Major_mode_shift',
        ]].copy()

        # rename columns for final return
        df.rename(columns = {'pitch_class_camelot_wheel' : 'pitch_class'}, inplace = True)
    
        return df

    #
    # define a function to reshape the output of 
    # "create_harmonic_mixing_camelot_keys_and_transitions"
    # into a stacked data set with mode (Major or minor)
    # indicated
    #
    # This is static so that we can use it elsewhere
    #
    @staticmethod
    def stack_Major_and_minor_keys(df : pd.DataFrame) -> pd.DataFrame:

        # define a helper function to remove indicators such as "Major" or "minor"
        def adjust(df, indicator):
            df_adjusted = df[[
                'pitch_class',
                'camelot_' + indicator,
                indicator + '_down',
                indicator + '_up',
                indicator + '_mode_shift',
            ]].copy()
            df_adjusted.columns = [x.replace('_' + indicator, '').replace(indicator + '_', '') for x in df_adjusted.columns]
            return df_adjusted

        # remove minor indicator and at "m" string to key name
        df_minor = adjust(df, 'minor')
        df_minor['pitch_class'] = [x + 'm' for x in df_minor['pitch_class']]

        # remove Major indicator
        df_Major = adjust(df, 'Major')

        # stack the Major and minor DataFrames and rename columns appropriately
        df_result = (
            pd.concat([df_minor, df_Major])
            .reset_index(drop = True)
            .rename(
                columns = {
                    'pitch_class' : 'key',
                    'camelot' : 'camelot_key',
                }
            )
        )
    
        return df_result

    #
    # define a method to finalize the key transition relationships
    #
    def define_key_transition_relationships(self):
        df_down = pd.merge(
            self.df_initial_wheel_stacked,
            self.df_key_nodes.rename(columns = {'camelot_key' : 'down', 'key' : 'down_key'}),
            on = 'down',
            how = 'left',
        )

        df_up = pd.merge(
            df_down,
            self.df_key_nodes.rename(columns = {'camelot_key' : 'up', 'key' : 'up_key'}),
            on = 'up',
            how = 'left',
        )

        df_mode_shift = pd.merge(
            df_up,
            self.df_key_nodes.rename(columns = {'camelot_key' : 'mode_shift', 'key' : 'mode_shift_key'}),
            on = 'mode_shift',
            how = 'left',
        )

        self.df_relationships = df_mode_shift[['key', 'down_key', 'up_key', 'mode_shift_key']].copy()
        self.df_relationships['same_shift_key'] = self.df_relationships['key']

    #
    # Address enharmonic equivalency
    #
    def deal_with_enharmonic_equivalency(self):

        self.df_relationships['key_to_map_to_enharmonic'] = [
            x.replace('m', '') for x in self.df_relationships['key']
        ]

        self.df_relationships = pd.merge(
            self.df_relationships,
            df_enharmonic.rename(columns = {'key' : 'key_to_map_to_enharmonic'}),
            on = 'key_to_map_to_enharmonic',
            how = 'left',
        )

        self.df_relationships['same_shift_key'] = [
            i + 'm' if j.find('m') >= 0 else i for i, j in zip(
                self.df_relationships['enharmonic_equivalent'],
                self.df_relationships['key']
            )
        ]

        self.df_relationships.drop(columns = ['key_to_map_to_enharmonic', 'enharmonic_equivalent'], inplace = True)
        self.df_relationships = self.df_relationships.drop_duplicates()
