EXPLANATION_TEMPLATES = {
    # Missing
    "M:DET": "A determiner (e.g., 'the', 'a') was added: '{correction}'. Articles help clarify noun phrases.",
    "M:NOUN": "A noun was added: '{correction}'. Nouns help complete or clarify the meaning of phrases.",
    "M:PREP": "A preposition was added: '{correction}'. Prepositions show relationships between ideas.",
    "M:VERB": "A verb was added: '{correction}'. Every clause typically needs a verb to express an action or state.",
    "M:PUNCT": "Punctuation was added: '{correction}', improving sentence clarity or structure.",
    "M:SUBJ": "A subject is missing in this clause. A subject '{correction}' was added to complete the sentence.",
    "M:PRON": "A pronoun was added: '{correction}'. Pronouns help avoid repetition or clarify who is involved.",
    "M:ADJ": "An adjective was added: '{correction}'. Adjectives help describe or modify nouns.",
    "M:ADV": "An adverb was added: '{correction}'. Adverbs modify verbs, adjectives, or other adverbs.",
    "M:CONJ": "A conjunction was added: '{correction}'. Conjunctions connect words, phrases, or clauses.",
    "M:PART": "A particle was added: '{correction}'. Particles help form phrasal verbs or add nuance.",
    "M:AUX": "An auxiliary verb was added: '{correction}'. These help form questions, tenses, or passive voice.",
    "M:VERB:FORM": "A verb form was added: '{correction}'. This corrects the verb structure in the sentence.",
    "M:VERB:TENSE": "A verb tense marker was added: '{correction}'. This establishes the time frame of the action.",
    "M:VERB:SVA": "A subject-verb agreement marker was added: '{correction}'. This ensures the verb matches its subject.",
    "M:VERB:INFL": "A verb inflection marker was added: '{correction}'. This corrects how the verb is formed.",
    "M:NOUN:NUM": "A noun number marker was added: '{correction}'. This specifies whether the noun is singular or plural.",
    "M:NOUN:POSS": "A possessive marker was added: '{correction}'. This shows ownership or relationship.",
    "M:DET:ART": "An article was added: '{correction}'. Articles help specify if a noun is definite or indefinite.",
    "M:VERB:MODAL": "A modal verb was added: '{correction}'. Modal verbs express necessity, possibility, permission, or ability.",
    "M:NOUN:INFLEC": "A noun inflection was added: '{correction}'. This corrects the noun form or declension.",
    "M:OTHER": "A missing word was added: '{correction}'. This completes the grammatical structure.",

    # Unnecessary
    "U:ADV": "The adverb '{word}' is unnecessary. It may create redundancy or confusion (e.g., double negatives).",
    "U:DET": "The determiner '{word}' is unnecessary in this context. Its removal makes the sentence more concise.",
    "U:NOUN": "The noun '{word}' is redundant or not needed in this sentence.",
    "U:PREP": "The preposition '{word}' is unnecessary here. Extra prepositions can make the sentence awkward or incorrect.",
    "U:VERB": "The verb '{word}' is not needed in this sentence and may result in a grammatical error like a double verb.",
    "U:PUNCT": "The punctuation '{word}' is not needed and may disrupt sentence structure or meaning.",
    "U:ADJ": "The adjective '{word}' is unnecessary and makes the sentence wordy or redundant.",
    "U:PRON": "The pronoun '{word}' is redundant or creates confusion about the subject.",
    "U:CONJ": "The conjunction '{word}' is not needed here. Extra conjunctions can make a sentence grammatically incorrect.",
    "U:AUX": "The auxiliary verb '{word}' is unnecessary and creates an ungrammatical structure.",
    "U:PART": "The particle '{word}' is not needed and may confuse the meaning of the phrasal verb.",
    "U:OTHER": "The word '{word}' is unnecessary and should be removed for clarity or grammatical correctness.",

    # Replacement
    "R:VERB": "The verb '{word}' was replaced with '{correction}' to better match tense, subject-verb agreement, or meaning.",
    "R:NOUN": "The noun '{word}' was replaced with '{correction}' for better context, clarity, or agreement.",
    "R:DET": "The determiner '{word}' was replaced with '{correction}' to better fit the noun it modifies.",
    "R:PREP": "The preposition '{word}' was replaced with '{correction}' because the original one didn't fit the phrase correctly.",
    "R:ADJ": "The adjective '{word}' was replaced with '{correction}' for better grammatical or semantic accuracy.",
    "R:PRON": "The pronoun '{word}' was replaced with '{correction}' to match number, gender, or case properly.",
    "R:ADV": "The adverb '{word}' was replaced with '{correction}' for clearer or more accurate meaning.",
    "R:PUNCT": "The punctuation mark '{word}' was replaced with '{correction}' to improve sentence flow or correctness.",
    "R:OTHER": "The phrase '{word}' was changed to '{correction}' to improve grammar, such as correcting verb form, adding necessary prepositions, or clarifying sentence structure.",
    "R:CONJ": "The conjunction '{word}' was replaced with '{correction}' to better join clauses or match sentence logic.",
    "R:PART": "The particle '{word}' was replaced with '{correction}' to correct a phrasal verb or improve natural usage.",
    "R:AUX": "The auxiliary verb '{word}' was replaced with '{correction}' to form the correct tense or structure.",
    
    # Specific verb error types
    "R:VERB:FORM": "The verb form '{word}' was replaced with '{correction}'. This corrects issues like using gerunds vs. infinitives.",
    "R:VERB:TENSE": "The verb tense '{word}' was replaced with '{correction}'. This ensures the action is placed in the correct time frame.",
    "R:VERB:SVA": "The verb '{word}' was replaced with '{correction}' to match its subject in number (singular/plural).",
    "R:VERB:INFL": "The irregular verb '{word}' was replaced with '{correction}'. This corrects the inflection of an irregular verb form.",
    "R:VERB:MOOD": "The verb mood '{word}' was replaced with '{correction}'. This corrects the indicative, subjunctive, or imperative mood.",
    "R:VERB:VOICE": "The verb '{word}' was replaced with '{correction}' to correct active/passive voice usage.",
    "R:VERB:MODAL": "The modal verb '{word}' was replaced with '{correction}' to express the right degree of necessity, possibility, or permission.",
    "R:VERB:ASPECT": "The verb aspect '{word}' was replaced with '{correction}' to correctly indicate whether the action is ongoing, completed, or habitual.",
    
    # Specific noun error types
    "R:NOUN:NUM": "The noun form '{word}' was replaced with '{correction}' to correct singular/plural usage.",
    "R:NOUN:POSS": "The possessive form '{word}' was replaced with '{correction}' to show ownership correctly.",
    "R:NOUN:INFL": "The noun inflection '{word}' was replaced with '{correction}' to match the grammatical requirements.",
    "R:NOUN:INFLEC": "The noun inflection '{word}' was replaced with '{correction}' to correct the declension or case form.",
    "R:NOUN:CASE": "The noun case '{word}' was replaced with '{correction}' to match its grammatical role in the sentence.",
    "R:NOUN:GENDER": "The noun gender form '{word}' was replaced with '{correction}' to match the grammatical gender requirements.",
    
    # Specific morphology errors
    "R:MORPH": "The word form '{word}' was replaced with '{correction}' to fix morphological issues (word formation).",
    
    # Specific orthography errors
    "R:ORTH": "The capitalization or formatting of '{word}' was adjusted to '{correction}' to match standard conventions.",
    "R:SPELL": "The misspelled word '{word}' was corrected to '{correction}'.",
    "R:CONTR": "The word '{word}' was replaced with '{correction}' to use or remove a contraction appropriately.",
    
    # Word Order
    "W:ADJ": "The adjective '{word}' was moved for better word order. Adjectives usually go before the noun they describe.",
    "W:ADV": "The adverb '{word}' was moved for better placement. Adverbs should typically appear near the verb or adjective they modify.",
    "W:PREP": "The preposition '{word}' was moved for more natural or correct sentence structure.",
    "W:NOUN": "The noun '{word}' was moved to improve sentence structure or clarity.",
    "W:VERB": "The verb '{word}' was moved to the correct position in the sentence.",
    "W:PRON": "The pronoun '{word}' was moved to clarify its reference or improve sentence structure.",
    "W:PUNCT": "The punctuation '{word}' was moved to the correct position in the sentence.",
    "W:DET": "The determiner '{word}' was moved closer to the noun it modifies.",
    "W:OTHER": "The word '{word}' was moved to improve overall sentence structure or readability.",
    
    # Split/Merge
    "S:SPELL": "Words were incorrectly split and have been joined to form '{correction}'.",
    "S:OTHER": "Words or phrases were incorrectly split and have been reorganized for clarity.",
    "M:SPELL": "The word '{word}' was incorrectly joined and has been split into '{correction}'.",
    "M:OTHER": "Words or phrases were incorrectly joined and have been separated for clarity.",
    
    # Articles, Determiners and Quantifiers
    "R:DET:ART": "The article '{word}' was replaced with '{correction}' to match the noun's definiteness or countability.",
    "R:DET:DEMO": "The demonstrative '{word}' was replaced with '{correction}' to correctly indicate proximity or reference.",
    "R:DET:POSS": "The possessive determiner '{word}' was replaced with '{correction}' to match the owner in gender or number.",
    "R:DET:QUANT": "The quantifier '{word}' was replaced with '{correction}' to better express the quantity or amount.",
    
    # Pronoun-specific categories  
    "R:PRON:PERS": "The personal pronoun '{word}' was replaced with '{correction}' to match gender, number, or case.",
    "R:PRON:POSS": "The possessive pronoun '{word}' was replaced with '{correction}' to agree with the owner or reference.",
    "R:PRON:REF": "The reflexive pronoun '{word}' was replaced with '{correction}' to properly reflect the subject.",
    "R:PRON:REL": "The relative pronoun '{word}' was replaced with '{correction}' to correctly introduce the relative clause.",
    
    # Punctuation-specific categories
    "R:PUNCT:TERM": "The terminal punctuation '{word}' was replaced with '{correction}' to properly end the sentence.",
    "R:PUNCT:CLAUSE": "The clause punctuation '{word}' was replaced with '{correction}' to better separate clauses.",
    "R:PUNCT:QUOT": "The quotation punctuation '{word}' was replaced with '{correction}' to properly mark quoted text.",
    
    # Agreement errors
    "R:AGREEMENT": "The word '{word}' was replaced with '{correction}' to maintain proper agreement in the sentence.",
    "R:AGREEMENT:SUBJ-VERB": "The verb '{word}' was replaced with '{correction}' to match its subject in person and number.",
    "R:AGREEMENT:NOUN-NUM": "The noun '{word}' was replaced with '{correction}' to maintain proper number agreement.",
    "R:AGREEMENT:DET-NOUN": "The determiner '{word}' was replaced with '{correction}' to agree with the noun it modifies.",
    "R:AGREEMENT:ADJ-NOUN": "The adjective '{word}' was replaced with '{correction}' to agree with the noun it modifies.",
    
    # Idioms and collocations
    "R:COLLOC": "The word '{word}' was replaced with '{correction}' to form a natural collocation or commonly used phrase.",
    "R:IDIOM": "The phrase containing '{word}' was corrected to '{correction}' to match the standard idiomatic expression.",
    
    # Formality errors
    "R:REGISTER": "The word '{word}' was replaced with '{correction}' to match the appropriate level of formality.",
    "R:STYLE": "The phrasing '{word}' was replaced with '{correction}' to maintain consistent style and tone.",
    
    # Complex clause structures
    "R:CLAUSE": "The clause structure using '{word}' was reformulated with '{correction}' to improve grammatical correctness.",
    "R:CLAUSE:REL": "The relative clause marker '{word}' was replaced with '{correction}' to properly introduce the relative clause.",
    "R:CLAUSE:NOUN": "The noun clause construction with '{word}' was replaced with '{correction}' for better grammatical structure.",
    "R:CLAUSE:ADV": "The adverbial clause using '{word}' was replaced with '{correction}' to connect ideas properly.",
    
    # Semantics and logical errors
    "R:SEM": "The word '{word}' was replaced with '{correction}' to correct a semantic (meaning) error.",
    "R:LOGICAL": "The logical connector '{word}' was replaced with '{correction}' to establish the correct relationship between ideas.",
    
    # Conditional structures
    "R:COND": "The conditional structure using '{word}' was replaced with '{correction}' to express the condition properly.",
    
    # Negation forms
    "R:NEG": "The negation form '{word}' was replaced with '{correction}' to express negation correctly.",
    
    # Catch-all fallback
    "UNK": "This word '{word}' was corrected to '{correction}' for grammar or clarity, but the specific reason wasn't identified.",
}