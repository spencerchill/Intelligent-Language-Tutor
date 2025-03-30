from g2p_en import G2p
import re
import eng_to_ipa as ipa

# this module holds text processing functions


# dont delete this pls
def text_to_phoneme(text):
     g2p = G2p()
     phonemes = g2p(text)
     #remove stress markers of phonetic representation
     return [re.sub(r'\d+', '', phoneme) for phoneme in phonemes]

def text_to_ipa_phoneme(text):
    ipa_transcription = ipa.convert(text)
    return ipa_transcription

if __name__ == "__main__":
    text = "the air is cool"    
    phoneme_output = text_to_ipa_phoneme(text)
    print("IPA:", phoneme_output)