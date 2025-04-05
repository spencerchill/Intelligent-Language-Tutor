import numpy as np
from panphon.distance import Distance
# threshold which phonemes are considered slightly mispronounced
COST_THRESHOLD = 0.09
# phoneme to character mapping
# we can change these mappings to ipa and this code works fine. its up to you guys
PHONEME_MAPPINGS = {
    # consonants
    'DH': 2, 'TH': 2, 'CH': 2, 'SH': 2, 'NG': 2,
    'ZH': 2, 'JH': 2, 'Y': 1, 'R': 1, 'L': 1,
    'W': 1, 'M': 1, 'N': 1, 'K': 1, 'G': 1,
    'F': 1, 'V': 1, 'S': 1, 'Z': 1, 'P': 1,
    'B': 1, 'T': 1, 'D': 1,
    # possible i missed some but we default to one anyways
    # vowels
    'AA': 1, 'AE': 1, 'AH': 1, 'AO': 1, 'AW': 2,
    'AY': 2, 'EH': 1, 'ER': 2, 'EY': 2, 'IH': 1,
    'IY': 1, 'OW': 2, 'OY': 2, 'UH': 1, 'UW': 1
}

# IPA to character mapping
IPA_MAPPINGS = {
    # consonants
    'ð': 2, 'θ': 2, 'tʃ': 2, 'ʃ': 2, 'ŋ': 2,
    'ʒ': 2, 'dʒ': 2, 'j': 1, 'r': 1, 'l': 1,
    'w': 1, 'm': 1, 'n': 1, 'k': 1, 'g': 1,
    'f': 1, 'v': 1, 's': 1, 'z': 1, 'p': 1,
    'b': 1, 't': 1, 'd': 1,
    # vowels
    'ɑ': 1, 'æ': 1, 'ə': 1, 'ɔ': 1, 'aʊ': 2,
    'aɪ': 2, 'ɛ': 1, 'ɝ': 2, 'eɪ': 2, 'ɪ': 1,
    'i': 1, 'oʊ': 2, 'ɔɪ': 2, 'ʊ': 1, 'u': 1
}

def levenshtein_indices(target_phonemes, user_phonemes):
    """
    Levenshteinn distance algorithm.
    Returns mispronounced indices.
    """
   # TODO: better scoring metrics which are not being calculated now
    m, n = len(target_phonemes), len(user_phonemes)
    dp = np.zeros((m + 1, n + 1), dtype=int)
    
    for i in range(m + 1):
        dp[i][0] = i  # cost of deleting i phonemes
    for j in range(n + 1):
        dp[0][j] = j  # cost of inserting j phonemes

   # building edit distance matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if target_phonemes[i - 1] == user_phonemes[j - 1] else 1 
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # deletion
                dp[i][j - 1] + 1,  # insertion
                dp[i - 1][j - 1] + cost  # substitution
            )
   # backtracking dp
    i, j = m, n
    mispronounced_indices = {} 
    while i > 0 or j > 0:
        if target_phonemes[i - 1] == user_phonemes[j - 1]: 
            # match
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i - 1][j] + 1: 
            # Deletion (missing phoneme)
            mispronounced_indices[i - 1] = "full"
            i -= 1
        elif dp[i][j] == dp[i][j - 1] + 1: 
            # insertion (extra phoneme)
            # highlight phoneme before and after if they exist
            mispronounced_indices[i - 1] = "full"
            if i < m:
                mispronounced_indices[i] = "full"
            j -= 1
        else: 
            # substitution
            cost = Distance().feature_edit_distance(target_phonemes[i - 1], user_phonemes[j - 1])
            severity = 'slight' if cost <= COST_THRESHOLD else 'full'
            mispronounced_indices[i-1] = severity
            i -= 1
            j -= 1

    return mispronounced_indices

def create_phoneme_to_char_mapping(word, phonemes):
    """
    Create a mapping from phoneme indices to character indices using PHONEME_MAPPINGS.  
    Returns a list of tuples (phoneme_index, char_index) for each phoneme.
    """
    mapping = []
    char_index = 0
    phoneme_index = 0

    while phoneme_index < len(phonemes) and char_index < len(word):
        phoneme = phonemes[phoneme_index]
        char_count = IPA_MAPPINGS.get(phoneme, 1)
  
        # add mappings for each character this phoneme represents
    
        for i in range(char_count):
            mapping.append((phoneme_index, char_index + i))
        #go next char and phone
        char_index += char_count
        phoneme_index += 1
    return mapping

def split_phonemes(phonemes):
    words = []
    current_word = []
    for phoneme in phonemes:
        if phoneme == ' ':
            words.append(current_word)
            current_word = []
        else:
            current_word.append(phoneme)
    words.append(current_word)
    return words

def get_pronunciation_score(target_phrase, target_phonemes, user_phonemes):
    """
    Get pronunciation score and error info for a target phrase and user phonemes.
    ISSUE: MISMATCH OF NUMBER OF WORDS
    USER MUST SPEAK SLOW CURRENTLY
    """   
    target_words = split_phonemes(target_phonemes)
    user_words = split_phonemes(user_phonemes)
    original_words = target_phrase.split()
    error_info = {
        'accuracy': 0,
        'incorrect_indices': [],
        'phoneme_indices': [],
        'word_feedback': [] # stores mispronounced words and their errors, VISUALLFEEDBACK
    }
    total_phonemes = 0
    correct_phonemes = 0
    for i in range(len(original_words)):
        # phonemes for curr word
        target_word = target_words[i]
        user_word = user_words[i]
        original_word = original_words[i]
        
        # check if words match exactly first
        if target_word == user_word:
            correct_phonemes += len(target_word)
            total_phonemes += len(target_word)
            continue
        # get indices of phonemes that are substitutions/deletions/insertions
        mispronounced_dict = levenshtein_indices(target_word, user_word)
        # create mapping from phoneme indices to character indices
        phoneme_to_char = create_phoneme_to_char_mapping(original_word, target_word)
    
        # Position of phoneme within larger context
        word_start = len(' '.join(original_words[:i])) + (i > 0)
        word_end = word_start + len(original_word)
        word_errors = []
        seen_phonemes = set() 

        for phoneme_idx, char_idx in phoneme_to_char:
            severity = mispronounced_dict.get(phoneme_idx)
            if severity:
                # severity is either partial or full
                phoneme = target_word[phoneme_idx]
                error_info['incorrect_indices'].append((word_start + char_idx, severity))
                word_errors.append({
                        'phoneme': phoneme,
                        'incorrect_indices': char_idx,
                        'severity': severity
                    })
                if phoneme not in seen_phonemes:  # prevent multiple phonemes in word_feedback
                    error_info['phoneme_indices'].append((i, phoneme_idx, severity))
                    seen_phonemes.add(phoneme)
        # jayden use this for future idea yk what it is KEEP
        if word_errors:
            error_info['word_feedback'].append({
            'word': original_word,
            'errors': word_errors,
            'start_index': word_start,
            'end_index': word_end
        })
        
        total_phonemes += len(target_word)
        correct_phonemes += len(target_word) - len(mispronounced_dict)

    if total_phonemes > 0:
        error_info['accuracy'] = (correct_phonemes / total_phonemes) * 100
    return error_info


def main():
    # Example usage
    import text_processing as tp
    target_phrase = "the"
    user_phrase = "duh"
    target_phonemes = tp.text_to_ipa_phoneme(target_phrase)
    user_phonemes = tp.text_to_ipa_phoneme(user_phrase)

    print(target_phonemes)
    feedback = get_pronunciation_score(target_phrase, target_phonemes, user_phonemes)
    print("Pronunciation Feedback:", feedback)

if __name__ == "__main__":
    main()