from g2p_en import G2p
import re
import eng_to_ipa as ipa

# this module holds text processing functions
# soon to be added:
# Dynamic Time Warping or Levensthien word distance
# segment phonemes / align if needed?

def text_to_ipaPhoneme(text):
    ipa_transcription = ipa.convert(text)
    return ipa_transcription

if __name__ == "__main__":
    text = "The red dog jumped over the white fence"    
    IPA_Output = text_to_ipaPhoneme(text)
    print("IPA:", IPA_Output)