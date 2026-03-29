# ai_service/app/models/nlp_model.py
# Dyslexia-aware text correction pipeline.
# Stage 1: SymSpell — fast dictionary-based spell correction
# Stage 2: T5 grammar correction (optional, heavier)

from symspellpy import SymSpell, Verbosity
import pkg_resources

# Initialize SymSpell with English frequency dictionary
sym_spell = SymSpell(max_dictionary_edit_distance=3, prefix_length=7)

# Load the dictionary bundled with symspellpy
dict_path = pkg_resources.resource_filename("symspellpy", "frequency_dictionary_en_82_765.txt")
sym_spell.load_dictionary(dict_path, term_index=0, count_index=1)

def correct_text(raw_text: str, language: str = "en") -> str:
    """
    Corrects spelling in text, accounting for dyslexic error patterns.
    Dyslexic patterns include:
    - Letter reversals: b/d, p/q (e.g. "doy" -> "boy")
    - Phonetic spelling: "woz" -> "was"
    - Omissions: "becaus" -> "because"
    """
    # For non-English, we return text as-is (extend with multilingual models)
    if language != "en":
        return raw_text

    # SymSpell compound correction — handles multi-word correction
    suggestions = sym_spell.lookup_compound(
        raw_text,
        max_edit_distance=2
    )

    # Return the best suggestion, or original if nothing found
    if suggestions:
        return suggestions[0].term
    return raw_text
