from g2p_en import G2p
import re

# this module holds text processing functions
# soon to be added:
# Dynamic Time Warping or Levensthien word distance
# segment phonemes / align if needed?

def text_to_phoneme(text):
    g2p = G2p()
    phonemes = g2p(text)
    #remove stress markers of phonetic representation
    return [re.sub(r'\d+', '', phoneme) for phoneme in phonemes]