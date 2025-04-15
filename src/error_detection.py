import numpy as np
from panphon.distance import Distance
# threshold which phonemes are considered slightly mispronounced
COST_THRESHOLD = 0.09

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
    Calculates the Levenshtein distance between the target and user phonemes,
    identifies mispronounced indices and feature accuracy.
    
    Args:
    -----
        target_phonemes (list): List of target phonemes (e.g., ['ð', 'ə'])
        user_phonemes (list): List of user-produced phonemes (e.g., ['d', 'ə'])
        
    Returns:
    --------
        tuple: (list of tuples [(index, severity)], accuracy percentage)
               where severity is 'slight' or 'full'
    """
    dist = Distance()
    m, n = len(target_phonemes), len(user_phonemes)
    dp = np.zeros((m + 1, n + 1), dtype=float)
    
    # init DP table
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # fill table
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            # have to check for spaces as spaces mess thinsg up
            if target_phonemes[i-1] == ' ' and user_phonemes[j-1] == ' ':
                dp[i][j] = dp[i-1][j-1] # match 
            elif target_phonemes[i-1] == ' ' or user_phonemes[j-1] == ' ':
                dp[i][j] = min(dp[i-1][j] + 1, dp[i][j-1] + 1) # insertion or deletion
            else:
                feature_dist = dist.feature_edit_distance(target_phonemes[i-1], user_phonemes[j-1])
                dp[i][j] = min(
                    dp[i-1][j] + 1,  # deletion
                    dp[i][j-1] + 1,  # insertion
                    dp[i-1][j-1] + feature_dist  # substitution
                )
    
    # backtracking to find mispronounced phonemes
    mispronounced_indices = {}
    i, j = m, n
    while i > 0 or j > 0:
        if target_phonemes[i-1] == user_phonemes[j-1]:
            # match
            i -= 1
            j -= 1
        elif dp[i][j] == dp[i-1][j] + 1:
            # deletion (phoneme is missing)
            mispronounced_indices[i-1] = "incorrect"
            i -= 1
        elif dp[i][j] == dp[i][j-1] + 1:
            # insertion (extra phoneme)
            mispronounced_indices[i-1] = "incorrect"
            if i < m:
                mispronounced_indices[i] = "incorrect"
            j -= 1
        else:
            # substitution (phoneme mismatch)
            feature_dist = dist.feature_edit_distance(target_phonemes[i-1], user_phonemes[j-1])
            severity = 'partial' if feature_dist <= COST_THRESHOLD else 'incorrect'
            mispronounced_indices[i-1] = severity
            i -= 1
            j -= 1
    
    #  accuracy
    max_distance = max(m, n)
    similarity = 1 - (dp[m][n] / max_distance)
    accuracy = similarity * 100

    return mispronounced_indices, accuracy

def split_phonemes(phonemes):
    """
    Split a list of phonemes into words based on spaces.
    
    Args:
    -----
        phonemes (list): List of phonemes with spaces between words
                            e.g., ['ð', 'ə', ' ', 'k', 'æ', 't']
                        
    Returns:
    --------
        list: List of phoneme lists, where each sublist corresponds to a word
                e.g., [['ð', 'ə'], ['k', 'æ', 't']]
    """
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
    Get pronunciation score and error info for a target phrase and user phonemes,
    handling different word counts by comparing entire phoneme sequences.
    
    Args:
    -----
        target_phrase (str): Original text phrase (e.g., "the cat")
        target_phonemes (list): List of target IPA phonemes with spaces (e.g., ['ð', 'ə', ' ', 'k', 'æ', 't'])
        user_phonemes (list): List of user's spoken IPA phonemes with spaces (e.g., ['d', 'ə', ' ', 'k', 'æ', 't'])
        
    Returns:
    --------
        dict: Dictionary containing pronunciation feedback information 
    """

    # NOTE: you may be like wtf is going on
    #       you don't need to understand what or why im doing it
    #       [  JUST KNOW ] the data im returning

    error_info = {
        'accuracy': 0, # advanced accuracy metric!
        'incorrect_indices': [], # global character indices for highlighting
        'phoneme_indices': [], # global phoneme indices for highlighting
        'word_feedback': [] # phonemes and start/end positions for all words
    }

    # phoneme indices with severity mapping
    mispronounced_indices, error_info['accuracy'] = levenshtein_indices(target_phonemes, user_phonemes)
    
    # split target phrase into words and phonemes into word sublists
    target_word_phonemes = split_phonemes(target_phonemes)
    original_words = target_phrase.split()
    
    ######### POPULATE WORD_FEEDBACK ###########
    phoneme_index = 0
    for word_index, word in enumerate(original_words):
        # get words character positions
        # count the characters to get to word index
        word_start_pos = get_word_start_position(target_phrase, word_index)
        word_end_pos = word_start_pos + len(word) 
        
        word_phonemes = target_word_phonemes[word_index]
        word_data = {
            'word': word,
            'char_start_index': word_start_pos,
            'char_end_index': word_end_pos,
            'phonemes': []
        }
        # populate phoneme list with a mapping of 
        # phonemes and severity
        for phoneme in word_phonemes:
            severity = mispronounced_indices.get(phoneme_index, "correct")
            word_data['phonemes'].append({
                'phoneme': phoneme,
                'severity': severity
            })
            phoneme_index +=1
        phoneme_index+=1 # space
        error_info['word_feedback'].append(word_data)
    
    ####### GLOBAL CHARACTER INDICES ########

    # phoneme to word mapping
    phoneme_to_word_map = {}
    word_index = 0
    for i, phoneme in enumerate(target_phonemes):
        if phoneme == ' ':
            word_index += 1
        else:
            phoneme_to_word_map[i] = word_index
    
    # grab mispronounced phonemes
    for phoneme_index, severity in mispronounced_indices.items():

        phoneme = target_phonemes[phoneme_index]
        # word this phoneme belongs to
        word_index = phoneme_to_word_map.get(phoneme_index, 0)
        word_start_pos = error_info['word_feedback'][word_index]['char_start_index']
        
        # phoneme index within the word
        relative_phoneme_index = get_phoneme_index_in_word(target_phonemes, phoneme_index)

        # sum up the character offset before this character
        char_offset = 0
        for i in range(phoneme_index - relative_phoneme_index, phoneme_index):
            if i >= 0 and i < len(target_phonemes) and target_phonemes[i] != ' ':
                char_offset += IPA_MAPPINGS.get(target_phonemes[i], 1)
    
        phoneme_length = IPA_MAPPINGS.get(phoneme, 1)
        # add each character position to the error info
        for j in range(phoneme_length):
            global_char_pos = word_start_pos + char_offset + j
            error_info['incorrect_indices'].append((global_char_pos, severity))
    
    ###### GLOBAL PHONEME INDICES #######
    error_info['phoneme_indices'] = [(index, sev) for index, sev in mispronounced_indices.items()]
    
    return error_info

def get_phoneme_index_in_word(phonemes, global_index):
    """
    Get the relative index of a phoneme within its word.
    
    Args:
    -----
        phonemes (list): Complete phoneme list
        global_index (int): Global index in the list
        
    Returns:
    --------
        int: Relative index within the word
    """
    word_start = global_index
    while word_start > 0 and phonemes[word_start-1] != ' ':
        word_start -= 1
    return global_index - word_start

def get_word_start_position(phrase, word_index):
    """
    Get the character position where a word starts in the phrase.
    
    Args:
    -----
        phrase (str): Original phrase
        word_idx (int): Index of the word
        
    Returns:
    --------
        int: Character position where the word starts
    """
    words = phrase.split()
    position = 0
    
    for i in range(word_index):
        if i < len(words):
            position += len(words[i]) + 1  # +1 for space
    
    return position

def main():
    """
    Example usage
    """
    import text_processing as tp
    target_phrase = "bam bop badabopop pow"
    user_phrase = "bat bot jayden cool"
    target_phonemes = tp.text_to_ipa_phoneme(target_phrase)
    user_phonemes = tp.text_to_ipa_phoneme(user_phrase)

    print(target_phonemes)
    print(user_phonemes)
    info = get_pronunciation_score(target_phrase, target_phonemes, user_phonemes)
    print("feedback", info)


if __name__ == "__main__":
    main()