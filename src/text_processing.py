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

ARPA_TO_IPA = {
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
            if phoneme_clean in ARPA_TO_IPA:
                ipa.append(ARPA_TO_IPA[phoneme_clean])
        ipa_words.append(ipa)  
    return [phoneme for word in ipa_words for phoneme in word + [' ']][:-1] 

if __name__ == "__main__":
    text = "nice to meet you"    
    phoneme_output = text_to_ipa_phoneme(text)
    print("IPA:", ''.join(phoneme_output))