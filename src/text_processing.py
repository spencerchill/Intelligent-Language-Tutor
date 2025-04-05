from g2p_en import G2p
import re

# this module holds text processing functions
# IMPORTANT: removed eng_to_ipa because it does not correctly map.
#            to simplify building application for users i use g2p then map arpabet to ipa

# dont delete this pls
def text_to_phoneme(text):
    g2p = G2p()
    phonemes = g2p(text)
    #remove stress markers of phonetic representation
    return [re.sub(r'\d+', '', phoneme) for phoneme in phonemes]

arpabet_to_ipa = {
    "AA": "ɑ", "AE": "æ", "AH": "ʌ", "AO": "ɔ", "AW": "aʊ", "AY": "aɪ",
    "B": "b", "CH": "tʃ", "D": "d", "DH": "ð", "EH": "ɛ", "ER": "ɝ",
    "EY": "eɪ", "F": "f", "G": "ɡ", "HH": "h", "IH": "ɪ", "IY": "i",
    "JH": "dʒ", "K": "k", "L": "l", "M": "m", "N": "n", "NG": "ŋ",
    "OW": "oʊ", "OY": "ɔɪ", "P": "p", "R": "ɹ", "S": "s", "SH": "ʃ",
    "T": "t", "TH": "θ", "UH": "ʊ", "UW": "u", "V": "v", "W": "w",
    "Y": "j", "Z": "z", "ZH": "ʒ"
}
def text_to_ipa_phoneme(text):
    g2p = G2p()
    words = text.strip().split()
    ipa_words = []
    for word in words:
        arpabet = g2p(word)
        ipa = []
        for phoneme in arpabet:
            phoneme_clean = re.sub(r'\d', '', phoneme)
            if phoneme_clean in arpabet_to_ipa:
                ipa.append(arpabet_to_ipa[phoneme_clean])
        ipa_words.append(''.join(ipa))
    return f"/{' '.join(ipa_words)}/"

if __name__ == "__main__":
    text = "he doesn't know"    
    phoneme_output = text_to_ipa_phoneme(text)
    print("IPA:", phoneme_output)