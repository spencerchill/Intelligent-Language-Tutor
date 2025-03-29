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

def get_lcs_indices(target_phonemes, user_phonemes):
    """
    Get indices of phonemes that are not part of the LCS between two phoneme sequences.
    Returns a set of indices from target_phonemes that are not in the LCS.
    """
    m, n = len(target_phonemes), len(user_phonemes)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    # build LCS table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if target_phonemes[i-1] == user_phonemes[j-1]:
                dp[i][j] = dp[i-1][j-1] + 1
            else:
                dp[i][j] = max(dp[i-1][j], dp[i][j-1])
    # traverse table
    i, j = m, n

    lcs_indices = set()
    while i > 0 and j > 0:
        if target_phonemes[i-1] == user_phonemes[j-1]:
            # match... add curr index to set
            lcs_indices.add(i-1)
            i -= 1
            j -= 1
        elif dp[i-1][j] > dp[i][j-1]:
            i -= 1
        else:
            j -= 1
   
    # return indices that are NOTTT in the LCS
    return set(range(len(target_phonemes))) - lcs_indices

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
        char_count = PHONEME_MAPPINGS.get(phoneme, 1)
       
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
    ISSUE: MISMATCH OF NUMBER OF WORDS BREAKS IT LMAO
    USER MUST SPEAK SLOW CURRENTLY
    """    
    target_words = split_phonemes(target_phonemes)
    user_words = split_phonemes(user_phonemes)
    original_words = target_phrase.split()
   
    error_info = {
        'accuracy': 0, # lazy attempt at accuracy, change later with LEVENSTEHINENGS
        'incorrect_indices': {},
        'word_feedback': [] # stores word and any of its errors. honestly remove this later i think (DEBUGGING)
    } 
    total_phonemes = 0
    correct_phonemes = 0
    for i in range(len(original_words)):
        # phonemes for curr word
        target_word = target_words[i]
        user_word = user_words[i]
        original_word = original_words[i]
        # get indices of phonemes that are not in LCS
        mispronounced_indices = get_lcs_indices(target_word, user_word)
        # create mapping from phoneme indices to character indices
        phoneme_to_char = create_phoneme_to_char_mapping(original_word, target_word)

        word_start = len(' '.join(original_words[:i])) + (i > 0)
        word_mistakes = []
        for phoneme_idx, char_idx in phoneme_to_char:
            if phoneme_idx in mispronounced_indices:
                # with levensthien we could have partial mispronounciations
                # we could highlight those yellow but this is future
                error_info['incorrect_indices'][word_start + char_idx] = "red"
                word_mistakes.append(target_word[phoneme_idx])
       # may delete word feedback
        error_info['word_feedback'].append({
            'word': original_word,
            'errors': word_mistakes
        })    
        total_phonemes += len(target_word)
        correct_phonemes += len(target_word) - len(mispronounced_indices)

    if total_phonemes > 0:
        error_info['accuracy'] = (correct_phonemes / total_phonemes) * 100
   
    return error_info

def main():
    # Example usage !!MUST HAVE SAME NUMBER OF WORDS!!
    target_phrase = "the air"
    target_phonemes = ['DH', 'AH', ' ', 'EH', 'R']
    user_phonemes = ['D', 'AH', ' ', 'EH', 'ee']
   
    feedback = get_pronunciation_score(target_phrase, target_phonemes, user_phonemes)
    print("Pronunciation Feedback:", feedback)

if __name__ == "__main__":
    main()