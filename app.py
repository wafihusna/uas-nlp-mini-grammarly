"""
Mini Grammarly - Improved NLP Pipeline
University NLP Project

Improvements over the original:
1. pyspellchecker for spell correction (replaces manual Levenshtein dictionary lookup)
2. NLTK word_tokenize() + pos_tag() for proper tokenization and POS tagging
3. language_tool_python for grammar checking (replaces hand-coded rules)
4. Levenshtein distance kept for EDUCATIONAL visualization only
5. Safe correction filtering (avoid correcting valid English words)
6. Fixed sidebar toggle (removed header:visibility:hidden)
7. Better error categorization: Spelling / Grammar / Punctuation
"""

import re
import string
import streamlit as st

# ── Required NLTK downloads (run once) ──────────────────────────────────────
import nltk
# Download quietly; already present = no-op
for pkg in ("punkt", "averaged_perceptron_tagger", "punkt_tab",
            "averaged_perceptron_tagger_eng"):
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

from nltk.tokenize import word_tokenize
import nltk.tag

from spellchecker import SpellChecker          # pip install pyspellchecker
import language_tool_python                    # pip install language-tool-python

# Levenshtein for educational display only
try:
    from Levenshtein import distance as lev_distance   # pip install python-Levenshtein
except ImportError:
    def lev_distance(a, b):                            # pure-python fallback
        if len(a) < len(b):
            return lev_distance(b, a)
        if not b:
            return len(a)
        prev = list(range(len(b) + 1))
        for i, c1 in enumerate(a):
            curr = [i + 1]
            for j, c2 in enumerate(b):
                curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(c1 != c2)))
            prev = curr
        return prev[-1]

# ─────────────────────────────────────────────
# HELPER – POS tag human-readable meanings
# ─────────────────────────────────────────────
def _pos_meaning(tag: str) -> str:
    """Map Penn Treebank POS tag to a human-readable description."""
    mapping = {
        "CC": "Coordinating conjunction",
        "CD": "Cardinal number",
        "DT": "Determiner",
        "EX": "Existential 'there'",
        "FW": "Foreign word",
        "IN": "Preposition / subordinating conj.",
        "JJ": "Adjective",
        "JJR": "Adjective, comparative",
        "JJS": "Adjective, superlative",
        "LS": "List item marker",
        "MD": "Modal",
        "NN": "Noun, singular",
        "NNS": "Noun, plural",
        "NNP": "Proper noun, singular",
        "NNPS": "Proper noun, plural",
        "PDT": "Predeterminer",
        "POS": "Possessive ending",
        "PRP": "Personal pronoun",
        "PRP$": "Possessive pronoun",
        "RB": "Adverb",
        "RBR": "Adverb, comparative",
        "RBS": "Adverb, superlative",
        "RP": "Particle",
        "SYM": "Symbol",
        "TO": "to",
        "UH": "Interjection",
        "VB": "Verb, base form",
        "VBD": "Verb, past tense",
        "VBG": "Verb, gerund / present participle",
        "VBN": "Verb, past participle",
        "VBP": "Verb, non-3rd-person present",
        "VBZ": "Verb, 3rd-person singular present",
        "WDT": "Wh-determiner",
        "WP": "Wh-pronoun",
        "WP$": "Possessive wh-pronoun",
        "WRB": "Wh-adverb",
        ",": "Comma",
        ".": "Sentence-final punctuation",
        ":": "Colon / semicolon",
        "``": "Opening quotation mark",
        "''": "Closing quotation mark",
        "(": "Left bracket",
        ")": "Right bracket",
    }
    return mapping.get(tag, tag)

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Mini Grammarly",
    page_icon="✏️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# GLOBAL CSS – Orange/Coral + Dark-Grey Theme
# NOTE: We no longer hide `header` so the sidebar toggle button remains visible.
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Sora:wght@700;800&display=swap');

/* ── Root variables ── */
:root {
    --orange:   #FF6B35;
    --orange-lt:#FFF0EB;
    --coral:    #FF8C61;
    --dark:     #1E1E2E;
    --grey:     #4A4A5A;
    --muted:    #9090A0;
    --bg:       #FAFAFA;
    --card:     #FFFFFF;
    --border:   #EBEBF0;
    --green:    #22C55E;
    --red:      #EF4444;
    --amber:    #F59E0B;
    --blue:     #3B82F6;
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--dark);
}

/* ── Hide only Streamlit footer/menu, NOT the header ──
   (Keeping the header restores the sidebar collapse button.) */
#MainMenu, footer {visibility: hidden;}
.block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 900px;}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--dark);
}
section[data-testid="stSidebar"] * {
    color: #E0E0EE !important;
}
section[data-testid="stSidebar"] .stRadio label {
    font-size: 0.95rem;
    padding: 6px 0;
}

/* ── Headings ── */
h1, h2, h3 { font-family: 'Sora', sans-serif; }

/* ── Buttons ── */
div.stButton > button {
    background: var(--orange);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.55rem 1.6rem;
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: background 0.2s, transform 0.1s;
}
div.stButton > button:hover {
    background: var(--coral);
    transform: translateY(-1px);
}

/* ── Text area ── */
textarea {
    border-radius: 10px !important;
    border: 1.5px solid var(--border) !important;
    font-size: 1rem !important;
    padding: 12px !important;
}
textarea:focus {
    border-color: var(--orange) !important;
    box-shadow: 0 0 0 3px rgba(255,107,53,0.15) !important;
}

/* ── Custom cards ── */
.mg-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.mg-hero {
    background: linear-gradient(135deg, #FFF0EB 0%, #FAFAFA 100%);
    border-left: 5px solid var(--orange);
    border-radius: 14px;
    padding: 2rem 2.4rem;
    margin-bottom: 1.5rem;
}
.mg-badge {
    display: inline-block;
    background: var(--orange-lt);
    color: var(--orange);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    margin-bottom: 0.8rem;
}
.result-box {
    background: #F0FDF4;
    border: 1.5px solid #86EFAC;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    font-size: 1.05rem;
    font-weight: 500;
    color: #166534;
    margin-top: 0.6rem;
}
.table-tech th {
    background: var(--dark);
    color: white;
    padding: 8px 14px;
    text-align: left;
    font-size: 0.88rem;
}
.table-tech td {
    padding: 8px 14px;
    border-bottom: 1px solid var(--border);
    font-size: 0.88rem;
}
.table-tech tr:nth-child(even) td { background: #FAF9FF; }
.about-label {
    font-size: 0.75rem;
    font-weight: 700;
    color: var(--orange);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.3rem;
}
.member-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    display: flex;
    align-items: center;
    gap: 0.9rem;
    margin-bottom: 0.6rem;
}
.member-avatar {
    width: 38px;
    height: 38px;
    border-radius: 50%;
    background: var(--orange-lt);
    color: var(--orange);
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 1rem;
}
.preview-box {
    background: #fff8f5;
    border: 1.5px solid #FFD5C2;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    margin-top: 0.6rem;
    font-size: 0.95rem;
    line-height: 1.8;
}
.arrow-down {
    text-align: center;
    color: var(--orange);
    font-size: 1.4rem;
    margin: 0.2rem 0;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NLP BACKEND – Improved Pipeline
# ─────────────────────────────────────────────

# ── 1. Spell Checker (pyspellchecker) ────────────────────────────────────────
# pyspellchecker uses a frequency-based English word corpus.
# It is much more accurate than a manual dictionary + Levenshtein lookup because:
# - It knows hundreds of thousands of real English words (including "sister", "want", etc.)
# - It considers word frequency, not just edit distance
# - It won't falsely flag common English words
_spell = SpellChecker()

# Words to NEVER auto-correct (whitelist) – proper nouns, abbreviations, etc.
WHITELIST = {
    "i", "a", "ok", "mr", "mrs", "dr", "jr", "sr",
    "id", "url", "nlp", "ui", "ux", "api",
}

def check_spelling_improved(tokens: list[str]) -> dict[str, str]:
    """
    Use pyspellchecker to find misspelled tokens.
    Returns {original_token: suggested_correction}.

    Safety filters applied:
    - Skip punctuation, numbers, single characters, whitelisted words
    - Skip words that start with capital letters (likely proper nouns)
    - Only suggest correction when spell checker is confident
    """
    errors = {}
    # Find misspelled words (returns a set of unknown words)
    word_list = [t for t in tokens if t.isalpha() and len(t) > 1]
    misspelled = _spell.unknown(word_list)

    for token in misspelled:
        lower = token.lower()
        # Skip whitelisted, single-char, or capitalized (proper noun) tokens
        if lower in WHITELIST:
            continue
        if token[0].isupper() and token.lower() != token:
            continue  # likely a proper noun

        # Get the most likely correction
        correction = _spell.correction(lower)
        if correction and correction != lower:
            errors[token] = correction

    return errors


# ── 2. POS Tagger (NLTK) ─────────────────────────────────────────────────────
# NLTK's averaged_perceptron_tagger is a statistical model trained on the
# Penn Treebank. It is far more accurate than a hand-crafted rule tagger.

def pos_tag_improved(tokens: list[str]) -> list[tuple[str, str]]:
    """
    Tag each token with its Part-of-Speech using NLTK's statistical tagger.
    Returns list of (token, POS_tag) tuples.
    """
    return nltk.pos_tag(tokens)


# ── 3. Grammar Checker (LanguageTool) ────────────────────────────────────────
# LanguageTool is a mature, rule-based grammar engine with thousands of rules.
# It handles subject-verb agreement, tense consistency, articles, punctuation, etc.

@st.cache_resource(show_spinner="Loading grammar engine…")
def load_language_tool():
    """Load LanguageTool once and cache it across reruns (heavy startup cost)."""
    return language_tool_python.LanguageTool("en-US")

_lt = load_language_tool()


def check_grammar_improved(text: str):
    """
    Run LanguageTool on the full text.
    Returns a list of LanguageTool Match objects.

    Each match has:
      .offset        – character position in text
      .error_length  – length of the error span
      .message       – human-readable explanation
      .replacements  – list of suggested corrections
      .rule_id       – rule identifier (e.g. "HE_VERB_AGR")
      .category      – error category (e.g. "GRAMMAR", "TYPOS")
    """
    return _lt.check(text)


# ── 4. Main Analysis Pipeline ─────────────────────────────────────────────────

def analyze(text: str) -> dict:
    """
    Full NLP pipeline:
      Step 1 → Tokenize with NLTK word_tokenize
      Step 2 → POS tag with NLTK averaged_perceptron_tagger
      Step 3 → Spell check with pyspellchecker
      Step 4 → Grammar check with LanguageTool
      Step 5 → Build correction map + corrected text
      Step 6 → Compute Levenshtein distances for educational display
    """

    # ── Step 1: Tokenize ──────────────────────────────────────────────────────
    # word_tokenize handles contractions (don't → do, n't) and punctuation well
    tokens = word_tokenize(text)

    # ── Step 2: POS Tag ───────────────────────────────────────────────────────
    pos_tags = pos_tag_improved(tokens)

    # ── Step 3: Spell Check ───────────────────────────────────────────────────
    spell_errors = check_spelling_improved(tokens)
    # spell_errors = {wrong_token: correct_word}

    # ── Step 4: Grammar Check ────────────────────────────────────────────────
    grammar_matches = check_grammar_improved(text)

    # ── Step 5: Build correction map ─────────────────────────────────────────
    # We build TWO independent views:
    # (a) token-level spell corrections (applied token-by-token)
    # (b) character-level grammar corrections (applied to whole text via LanguageTool)

    # Apply LanguageTool corrections to get corrected text
    # language_tool_python.utils.correct() applies all suggestions
    corrected_text = language_tool_python.utils.correct(text, grammar_matches)

    # Now also apply remaining spell corrections that LanguageTool may have missed
    # We re-check spelling on the LT-corrected text
    corrected_tokens = word_tokenize(corrected_text)
    residual_spell = check_spelling_improved(corrected_tokens)
    for wrong, right in residual_spell.items():
        corrected_text = re.sub(
            r'\b' + re.escape(wrong) + r'\b', right, corrected_text
        )

    # Fix spacing before punctuation
    corrected_text = re.sub(r" ([.,!?;:])", r"\1", corrected_text)

    # ── Step 6: Levenshtein (for educational display only) ───────────────────
    lev_details = {}
    for wrong, right in spell_errors.items():
        lev_details[wrong] = {
            "suggestion": right,
            "distance": lev_distance(wrong.lower(), right.lower()),
        }

    # ── Build grammar error map by character offset ───────────────────────────
    # Each entry: { 'span': (start, end), 'original': str, 'suggestion': str,
    #               'message': str, 'category': str }
    grammar_error_list = []
    for m in grammar_matches:
        suggestion = m.replacements[0] if m.replacements else None
        if suggestion is None:
            continue
        grammar_error_list.append({
            "span":       (m.offset, m.offset + m.error_length),
            "original":   text[m.offset: m.offset + m.error_length],
            "suggestion": suggestion,
            "message":    m.message,
            "category":   m.category,
            "rule_id":    m.rule_id,
        })

    return {
        "original":          text,
        "tokens":            tokens,
        "pos_tags":          pos_tags,
        "spell_errors":      spell_errors,       # {wrong: right}
        "grammar_errors":    grammar_error_list, # list of dicts
        "lev_details":       lev_details,
        "corrected_text":    corrected_text,
    }


# ─────────────────────────────────────────────
# SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding: 1rem 0 0.5rem 0;'>
        <div style='font-size:1.6rem; font-weight:800; color:#FF6B35; font-family:Sora,sans-serif;'>✏️ Mini</div>
        <div style='font-size:1.6rem; font-weight:800; color:#FFFFFF; font-family:Sora,sans-serif; margin-top:-6px;'>Grammarly</div>
        <div style='font-size:0.75rem; color:#9090B8; margin-top:4px;'>NLP University Project</div>
    </div>
    <hr style='border-color:#333350; margin: 0.8rem 0;'/>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["🏠 Home", "🔍 Grammar Checker", "⚙️ How It Works", "📊 Technology", "🧑‍💻 About Project"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <hr style='border-color:#333350; margin: 1.5rem 0 0.6rem 0;'/>
    <div style='font-size:0.72rem; color:#6060A0; line-height:1.6;'>
        Built with Streamlit · NLTK · pyspellchecker<br>
        LanguageTool · Levenshtein
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 1 – HOME
# ─────────────────────────────────────────────
if page == "🏠 Home":
    st.markdown("""
    <div class='mg-hero'>
        <div class='mg-badge'>NLP Academic Project</div>
        <h1 style='font-size:2.6rem; margin:0.2rem 0 0.6rem 0; color:#1E1E2E;'>
            Mini <span style='color:#FF6B35;'>Grammarly</span>
        </h1>
        <p style='font-size:1.1rem; color:#4A4A5A; max-width:560px; line-height:1.7; margin:0;'>
            Detect spelling and grammar errors automatically using NLP — powered by
            NLTK tokenization & POS tagging, pyspellchecker, LanguageTool grammar engine,
            and Levenshtein distance for educational visualization.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='mg-card' style='text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>🔡</div>
            <div style='font-weight:700; margin-bottom:0.3rem;'>Spell Checking</div>
            <div style='color:#9090A0; font-size:0.88rem;'>
                pyspellchecker uses a frequency-based English corpus to accurately identify
                and fix misspelled words — without false positives on real words like "sister"
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='mg-card' style='text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>🏷️</div>
            <div style='font-weight:700; margin-bottom:0.3rem;'>POS Tagging</div>
            <div style='color:#9090A0; font-size:0.88rem;'>
                NLTK's statistical averaged_perceptron_tagger assigns grammatical categories
                with high accuracy, trained on the Penn Treebank corpus
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='mg-card' style='text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>📐</div>
            <div style='font-weight:700; margin-bottom:0.3rem;'>Grammar Rules</div>
            <div style='color:#9090A0; font-size:0.88rem;'>
                LanguageTool's rule engine covers thousands of English grammar patterns
                including tense consistency, subject-verb agreement, article usage, and more
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class='mg-card'>
        <div style='font-weight:700; font-size:1rem; margin-bottom:0.8rem;'>
            📋 Example Output Preview
        </div>
        <div style='color:#9090A0; font-size:0.85rem; margin-bottom:0.5rem;'>Input sentence:</div>
        <div class='preview-box'>
            Yesterday, my sister
            <span style='color:#EF4444;font-weight:700;text-decoration:underline wavy #EF4444;'>go</span>
            to the
            <span style='color:#EF4444;font-weight:700;text-decoration:underline wavy #EF4444;'>scool</span>
            library because she
            <span style='color:#EF4444;font-weight:700;text-decoration:underline wavy #EF4444;'>want</span>
            to borrow some
            <span style='color:#EF4444;font-weight:700;text-decoration:underline wavy #EF4444;'>boks</span>.
        </div>
        <div style='color:#9090A0; font-size:0.85rem; margin: 0.8rem 0 0.4rem 0;'>Corrected output:</div>
        <div class='result-box'>
            ✅ Yesterday, my sister <strong>went</strong> to the <strong>school</strong>
            library because she <strong>wanted</strong> to borrow some <strong>books</strong>.
        </div>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 2 – GRAMMAR CHECKER
# ─────────────────────────────────────────────
elif page == "🔍 Grammar Checker":
    st.markdown("""
    <div style='margin-bottom:1.4rem;'>
        <div class='mg-badge'>Core System</div>
        <h2 style='margin:0.2rem 0 0.4rem 0;'>Grammar & Spelling Checker</h2>
        <p style='color:#9090A0; font-size:0.95rem; margin:0;'>
            Type or paste any English sentence and click <strong>Analyze Text</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    default_text = (
        "Yesterday, my sister go to the scool library "
        "because she want to borrow some boks."
    )
    user_text = st.text_area(
        "Input Text",
        value=default_text,
        height=120,
        placeholder='e.g. "She go to scool everyday"',
        label_visibility="collapsed",
    )

    analyze_btn = st.button("🔍 Analyze Text", type="primary")

    if analyze_btn and user_text.strip():
        with st.spinner("Running NLP pipeline…"):
            result = analyze(user_text.strip())

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

        # ── Pipeline step indicators ──────────────────────────────────────────
        step_cols = st.columns(6)
        steps = ["Tokenize", "POS Tag", "Spell Check", "Levenshtein", "Grammar", "Output"]
        icons  = ["⚙️", "🏷️", "🔤", "📐", "📏", "✅"]
        for i, (col, label, icon) in enumerate(zip(step_cols, steps, icons)):
            with col:
                st.markdown(f"""
                <div style='text-align:center; padding:0.5rem;
                     background:{"#FFF0EB" if i < 5 else "#F0FDF4"};
                     border-radius:8px;
                     border:1px solid {"#FFD5C2" if i < 5 else "#86EFAC"};'>
                    <div style='font-size:1.1rem;'>{icon}</div>
                    <div style='font-size:0.72rem; font-weight:600;
                         color:{"#FF6B35" if i < 5 else "#166534"};'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Build error span sets for highlighting ────────────────────────────
        # Spell errors: token-level
        spell_error_tokens = {t.lower() for t in result["spell_errors"]}

        # Grammar errors: character spans in the ORIGINAL text
        grammar_spans = [
            (ge["span"][0], ge["span"][1]) for ge in result["grammar_errors"]
        ]

        # ── Highlighted error text (character-level) ──────────────────────────
        st.markdown("**📌 Detected Errors (highlighted)**")

        original = result["original"]
        # Build a set of character positions covered by grammar errors
        grammar_pos = set()
        for start, end in grammar_spans:
            grammar_pos.update(range(start, end))

        # Reconstruct highlighted HTML token by token, using NLTK tokens
        tokens = result["tokens"]
        # Map each token back to its character offset in original text
        token_spans = []
        search_start = 0
        for tok in tokens:
            idx = original.find(tok, search_start)
            if idx == -1:
                token_spans.append((-1, -1))
            else:
                token_spans.append((idx, idx + len(tok)))
                search_start = idx + len(tok)

        highlighted_parts = []
        for tok, (start, end) in zip(tokens, token_spans):
            tl = tok.lower()
            is_spell_err = tl in spell_error_tokens and tok.isalpha()
            is_gram_err  = start != -1 and start in grammar_pos

            if is_spell_err:
                suggestion = result["spell_errors"].get(tok) or result["spell_errors"].get(tl, "?")
                highlighted_parts.append(
                    f'<span style="color:#EF4444;font-weight:700;'
                    f'text-decoration:underline wavy #EF4444;"'
                    f' title="Spelling → {suggestion}">'
                    f'{tok} <sup style="font-size:0.6em;background:#EF4444;'
                    f'color:white;padding:1px 4px;border-radius:3px;">SP</sup></span>'
                )
            elif is_gram_err:
                ge = next(
                    (g for g in result["grammar_errors"] if g["span"][0] <= start < g["span"][1]),
                    None
                )
                hint = ge["message"][:60] + "…" if ge and len(ge["message"]) > 60 else (ge["message"] if ge else "")
                highlighted_parts.append(
                    f'<span style="color:#F59E0B;font-weight:700;'
                    f'text-decoration:underline wavy #F59E0B;"'
                    f' title="Grammar: {hint}">'
                    f'{tok} <sup style="font-size:0.6em;background:#F59E0B;'
                    f'color:white;padding:1px 4px;border-radius:3px;">GR</sup></span>'
                )
            elif tok in string.punctuation:
                highlighted_parts.append(tok)
            else:
                highlighted_parts.append(f'<span style="color:#1E1E2E;">{tok}</span>')

        highlighted_html = " ".join(highlighted_parts)
        # Fix spacing before punctuation
        highlighted_html = re.sub(r" ([.,!?;:])", r"\1", highlighted_html)

        st.markdown(f"""
        <div class='mg-card' style='font-size:1.05rem; line-height:2;'>
            {highlighted_html}
            <div style='margin-top:0.8rem; font-size:0.78rem; color:#9090A0;'>
                <span style='color:#EF4444;'>■</span> Spelling Error &nbsp;&nbsp;
                <span style='color:#F59E0B;'>■</span> Grammar Error
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Error Breakdown ───────────────────────────────────────────────────
        total_errors = len(result["spell_errors"]) + len(result["grammar_errors"])

        if total_errors > 0:
            st.markdown("**📋 Error Breakdown**")

            # Spelling errors
            for wrong, right in result["spell_errors"].items():
                st.markdown(f"""
                <div class='mg-card' style='padding:0.9rem 1.2rem;'>
                    <div style='display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap;'>
                        <div style='font-size:1.3rem;font-weight:800;color:#EF4444;'>{wrong}</div>
                        <div style='color:#9090A0;font-size:1.1rem;'>→</div>
                        <div style='font-size:1.3rem;font-weight:800;color:#22C55E;'>{right}</div>
                        <div style='flex:1;text-align:right;'>
                            <span style='background:#FEF2F2;color:#EF4444;font-size:0.75rem;
                                  font-weight:700;padding:3px 9px;border-radius:20px;'>Spelling</span>
                        </div>
                    </div>
                    <div style='color:#6060A0;font-size:0.83rem;margin-top:6px;'>
                        💡 Word not found in English corpus. Nearest match by frequency analysis.
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Grammar errors
            for ge in result["grammar_errors"]:
                st.markdown(f"""
                <div class='mg-card' style='padding:0.9rem 1.2rem;'>
                    <div style='display:flex;align-items:center;gap:1.2rem;flex-wrap:wrap;'>
                        <div style='font-size:1.3rem;font-weight:800;color:#F59E0B;'>{ge["original"]}</div>
                        <div style='color:#9090A0;font-size:1.1rem;'>→</div>
                        <div style='font-size:1.3rem;font-weight:800;color:#22C55E;'>{ge["suggestion"]}</div>
                        <div style='flex:1;text-align:right;'>
                            <span style='background:#FFFBEB;color:#F59E0B;font-size:0.75rem;
                                  font-weight:700;padding:3px 9px;border-radius:20px;'>
                                Grammar · {ge["category"]}
                            </span>
                        </div>
                    </div>
                    <div style='color:#6060A0;font-size:0.83rem;margin-top:6px;'>
                        💡 {ge["message"]}
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No errors detected in the input text!")

        # ── POS Tag Table ─────────────────────────────────────────────────────
        with st.expander("🏷️ View POS Tagging Results (NLTK)"):
            import pandas as pd
            pos_data = {
                "Token":     [tok for tok, _ in result["pos_tags"]],
                "POS Tag":   [tag for _, tag in result["pos_tags"]],
                "Tag Meaning": [_pos_meaning(tag) for _, tag in result["pos_tags"]],
                "Status":    [
                    "❌ Spell Error" if tok.lower() in spell_error_tokens
                    else "⚠️ Grammar Error" if any(
                        g["original"].lower() == tok.lower()
                        for g in result["grammar_errors"]
                    )
                    else "✅ OK"
                    for tok, _ in result["pos_tags"]
                ],
            }
            st.dataframe(pd.DataFrame(pos_data), use_container_width=True, hide_index=True)

        # ── Levenshtein Educational Table ────────────────────────────────────
        if result["lev_details"]:
            with st.expander("📐 Levenshtein Distance (Educational View)"):
                st.markdown("""
                <div style='font-size:0.85rem;color:#6060A0;margin-bottom:0.6rem;'>
                    ℹ️ Levenshtein distance is shown here for <strong>educational purposes</strong>.
                    The primary spell correction is performed by <code>pyspellchecker</code>,
                    which uses word frequency data for more accurate results.
                </div>
                """, unsafe_allow_html=True)
                import pandas as pd
                lev_rows = [
                    {
                        "Misspelled": wrong,
                        "Best Suggestion": info["suggestion"],
                        "Edit Distance": info["distance"],
                        "Meaning": f"{info['distance']} character edit(s) needed",
                    }
                    for wrong, info in result["lev_details"].items()
                ]
                st.dataframe(pd.DataFrame(lev_rows), use_container_width=True, hide_index=True)

        # ── Final Result ──────────────────────────────────────────────────────
        st.markdown("<br>**✅ Final Corrected Text**", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='result-box' style='font-size:1.2rem;letter-spacing:0.01em;'>
            {result["corrected_text"]}
        </div>
        """, unsafe_allow_html=True)

    elif analyze_btn:
        st.warning("⚠️ Please enter some text before analyzing.")


# ─────────────────────────────────────────────
# PAGE 3 – HOW IT WORKS
# ─────────────────────────────────────────────
elif page == "⚙️ How It Works":
    st.markdown("""
    <div style='margin-bottom:1.4rem;'>
        <div class='mg-badge'>Educational Pipeline</div>
        <h2 style='margin:0.2rem 0 0.4rem 0;'>How the NLP System Works</h2>
        <p style='color:#9090A0; font-size:0.95rem; margin:0;'>
            A sequential pipeline that transforms raw text into error-corrected output.
        </p>
    </div>
    """, unsafe_allow_html=True)

    PIPELINE = [
        {
            "title": "Input Text",
            "icon": "📝",
            "example": '"Yesterday, my sister go to the scool library because she want to borrow some boks."',
            "detail": "Raw user-provided sentence is received by the system. No preprocessing is done at this stage.",
        },
        {
            "title": "Tokenization — NLTK word_tokenize()",
            "icon": "⚙️",
            "example": '["Yesterday", ",", "my", "sister", "go", "to", "the", "scool", ...]',
            "detail": (
                "NLTK's word_tokenize() uses the Penn Treebank tokenizer. "
                "It correctly handles contractions (don't → do, n't), "
                "splits punctuation from words, and preserves sentence structure. "
                "This is far more robust than a simple regex split."
            ),
        },
        {
            "title": "POS Tagging — NLTK averaged_perceptron_tagger",
            "icon": "🏷️",
            "example": "[('Yesterday','RB'), ('sister','NN'), ('go','VBP'), ('scool','NN'), ...]",
            "detail": (
                "NLTK's statistical POS tagger, trained on the Penn Treebank corpus, "
                "assigns tags like VBP (verb, non-3rd-person present), NN (noun), RB (adverb). "
                "This replaces the original hand-coded rule tagger for much higher accuracy."
            ),
        },
        {
            "title": "Spell Checking — pyspellchecker",
            "icon": "🔤",
            "example": '"scool" → not in corpus → correction: "school"\n"sister" → in corpus → no correction (safe!)',
            "detail": (
                "pyspellchecker queries a frequency-based English word corpus. "
                "It identifies unknown words and returns the most likely correction based "
                "on word frequency AND edit distance, weighted together. "
                "A whitelist and proper-noun filter prevent false positives on real words."
            ),
        },
        {
            "title": "Levenshtein Distance — Educational Display",
            "icon": "📐",
            "example": 'lev("scool", "school") = 1\nlev("boks", "books") = 1\nlev("want", "went") = 1',
            "detail": (
                "Levenshtein distance is now used ONLY for educational visualization, "
                "not as the primary correction engine. It counts the minimum number of "
                "single-character edits (insertions, deletions, substitutions) between two strings. "
                "pyspellchecker internally uses a combination of frequency + edit distance."
            ),
        },
        {
            "title": "Grammar Checking — LanguageTool",
            "icon": "📏",
            "example": '"go" (after "sister") → Rule VERB_TENSE → suggest "went"\n"want" → Rule VERB_TENSE → suggest "wanted"',
            "detail": (
                "LanguageTool applies thousands of English grammar rules covering "
                "tense consistency, subject-verb agreement, article usage, punctuation, and more. "
                "It operates on the full sentence string (not just token pairs), so it understands "
                "context across multiple words — far beyond the original (subject, verb) lookup table."
            ),
        },
        {
            "title": "Merge & Apply Corrections",
            "icon": "🔗",
            "example": 'LanguageTool corrects grammar → pyspellchecker fixes residual spelling → final text assembled',
            "detail": (
                "LanguageTool's correct() utility applies all grammar corrections first. "
                "Spell corrections are then applied to any remaining unknown words. "
                "This two-pass approach avoids double-correcting words that were already fixed."
            ),
        },
        {
            "title": "Output — Corrected Text",
            "icon": "✅",
            "example": '"Yesterday, my sister went to the school library because she wanted to borrow some books."',
            "detail": (
                "The fully corrected sentence is returned with all errors fixed. "
                "Highlighted error breakdown and POS table give students full visibility "
                "into every step of the NLP pipeline."
            ),
        },
    ]

    for i, step in enumerate(PIPELINE):
        arrow = '<div class="arrow-down">↓</div>' if i < len(PIPELINE)-1 else ""
        with st.expander(f'{step["icon"]} Step {i+1}: {step["title"]}', expanded=(i==0)):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown(f"""
                <div style='font-size:0.9rem;color:#4A4A5A;line-height:1.7;margin-bottom:0.8rem;'>
                    {step["detail"]}
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div style='background:#FFF8F5;border:1.5px solid #FFD5C2;border-radius:8px;
                     padding:0.8rem 1rem;font-size:0.85rem;font-family:monospace;color:#CC4400;
                     white-space:pre-wrap;'>
                    <div style='font-size:0.72rem;color:#9090A0;margin-bottom:4px;
                         font-family:Inter,sans-serif;font-weight:600;'>EXAMPLE</div>
                    {step["example"]}
                </div>
                """, unsafe_allow_html=True)
        st.markdown(arrow, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 4 – TECHNOLOGY
# ─────────────────────────────────────────────
elif page == "📊 Technology":
    st.markdown("""
    <div style='margin-bottom:1.4rem;'>
        <div class='mg-badge'>Tech Stack</div>
        <h2 style='margin:0.2rem 0 0.4rem 0;'>Technology & Libraries</h2>
        <p style='color:#9090A0; font-size:0.95rem; margin:0;'>
            Libraries and NLP techniques powering Mini Grammarly.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='mg-card'>
    <table class='table-tech' style='width:100%; border-collapse:collapse;'>
    <thead><tr>
        <th>Library / Tool</th>
        <th>Role in This System</th>
        <th>Category</th>
    </tr></thead>
    <tbody>
    <tr><td><strong>NLTK</strong></td>
        <td>word_tokenize() for tokenization; averaged_perceptron_tagger for POS tagging</td>
        <td>🔡 NLP Core</td></tr>
    <tr><td><strong>pyspellchecker</strong></td>
        <td>Frequency-based English corpus spell checking; replaces manual dictionary lookup</td>
        <td>🔤 Spell Check</td></tr>
    <tr><td><strong>language-tool-python</strong></td>
        <td>Java-backed grammar rule engine with 1000+ English rules</td>
        <td>📏 Grammar</td></tr>
    <tr><td><strong>python-Levenshtein</strong></td>
        <td>Edit distance computation for educational visualization in the UI</td>
        <td>📐 Distance</td></tr>
    <tr><td><strong>Streamlit</strong></td>
        <td>Web framework & interactive UI</td>
        <td>🌐 Frontend</td></tr>
    <tr><td><strong>Pandas</strong></td>
        <td>Tabular display of POS results and Levenshtein table</td>
        <td>📊 Data</td></tr>
    <tr><td><strong>Regex (re)</strong></td>
        <td>Punctuation spacing cleanup and token character-offset mapping</td>
        <td>⚙️ Utility</td></tr>
    </tbody>
    </table>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='mg-badge'>NLP Techniques</div>
    <h3 style='margin:0.4rem 0 1rem 0;'>Underlying NLP Methods</h3>
    """, unsafe_allow_html=True)

    techniques = [
        ("🔡", "Tokenization (NLTK word_tokenize)",
         "Splits text into tokens using the Penn Treebank tokenizer. Handles contractions "
         "(don't → [do, n't]), separates punctuation from words, and preserves sentence structure. "
         "More robust than simple whitespace splitting for real-world English text."),
        ("🏷️", "Part-of-Speech Tagging (NLTK averaged_perceptron_tagger)",
         "A statistical tagger trained on the Penn Treebank corpus. Uses the averaged perceptron "
         "algorithm to assign Penn Treebank tags (NN, VBP, RB, etc.) based on learned patterns "
         "from millions of annotated sentences — not hand-coded rules."),
        ("🔤", "Spell Checking (pyspellchecker)",
         "Uses a pre-built frequency dictionary of English words. Unknown words are identified "
         "and the correction is chosen by maximizing P(correction | misspelling), combining "
         "word frequency with edit distance. Avoids the false-positive problem of pure "
         "dictionary lookup (e.g., 'sister', 'want' are correctly kept unchanged)."),
        ("📐", "Levenshtein Distance (Educational)",
         "Shown in the UI for educational purposes to help students understand how string "
         "similarity is computed. Counts minimum single-character edits (insert/delete/substitute) "
         "between two strings. Used internally by pyspellchecker as one factor in ranking corrections."),
        ("📏", "Rule-Based Grammar (LanguageTool)",
         "LanguageTool contains thousands of manually authored grammar and style rules for English. "
         "It operates on full sentences and handles tense consistency, subject-verb agreement, "
         "article usage, punctuation, and common learner errors — covering far more cases than "
         "a small hand-coded (subject, verb) lookup table."),
    ]

    for icon, title, desc in techniques:
        st.markdown(f"""
        <div class='mg-card' style='display:flex;gap:1rem;align-items:flex-start;'>
            <div style='font-size:2rem;margin-top:2px;'>{icon}</div>
            <div>
                <div style='font-weight:700;font-size:0.98rem;margin-bottom:0.3rem;'>{title}</div>
                <div style='color:#4A4A5A;font-size:0.88rem;line-height:1.7;'>{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 5 – ABOUT PROJECT
# ─────────────────────────────────────────────
elif page == "🧑‍💻 About Project":
    st.markdown("""
    <div style='margin-bottom:1.4rem;'>
        <div class='mg-badge'>Academic Context</div>
        <h2 style='margin:0.2rem 0 0.4rem 0;'>About This Project</h2>
        <p style='color:#9090A0; font-size:0.95rem; margin:0;'>
            Background, objectives, and academic references.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='mg-card'>
        <div class='about-label'>Project Objective</div>
        <p style='color:#4A4A5A; font-size:0.92rem; line-height:1.8; margin:0;'>
            To design and implement a lightweight, web-based prototype of a
            <strong>Grammatical Error Correction & Spelling Checker</strong> system using
            fundamental Natural Language Processing (NLP) techniques. The system demonstrates
            a complete text analysis pipeline — from raw input to corrected output — that can
            serve as an educational tool and practical aid for English writing.
        </p>
    </div>
    <div class='mg-card'>
        <div class='about-label'>Background Context</div>
        <p style='color:#4A4A5A; font-size:0.92rem; line-height:1.8; margin:0;'>
            Grammatical errors and spelling mistakes are among the most common challenges
            faced by non-native English speakers and students. Commercial tools like Grammarly
            employ large-scale neural language models; however, their internal workings remain
            opaque. This project implements a <strong>transparent, hybrid NLP pipeline</strong>
            combining statistical models (NLTK POS tagger) and rule-based engines (LanguageTool)
            that is interpretable and academically grounded.<br><br>
            The system addresses two core problems:<br>
            <strong>(1)</strong> <em>Spelling errors</em> — detected via pyspellchecker's
            frequency corpus and corrected using combined frequency + edit-distance ranking.<br>
            <strong>(2)</strong> <em>Grammatical errors</em> — detected by LanguageTool's
            1000+ English grammar rules including tense consistency, subject-verb agreement,
            and article usage.
        </p>
    </div>
    <div class='mg-card'>
        <div class='about-label'>Journal & Reference Sources</div>
        <ol style='color:#4A4A5A;font-size:0.9rem;line-height:2;padding-left:1.2rem;margin:0;'>
            <li>Levenshtein, V. I. (1966). <em>Binary codes capable of correcting deletions,
                insertions, and reversals.</em> Soviet Physics Doklady, 10(8), 707–710.</li>
            <li>Bird, S., Klein, E., & Loper, E. (2009). <em>Natural Language Processing with Python.</em>
                O'Reilly Media. (NLTK reference)</li>
            <li>Norvig, P. (2009). <em>How to Write a Spelling Corrector.</em>
                norvig.com/spell-correct.html (basis for pyspellchecker)</li>
            <li>Naber, D. (2003). <em>A Rule-Based Style and Grammar Checker.</em>
                Diploma Thesis, University of Bielefeld. (LanguageTool basis)</li>
            <li>Jurafsky, D. & Martin, J. H. (2023). <em>Speech and Language Processing (3rd ed. draft).</em>
                Stanford University. Chapter 2: Regular Expressions, Text Normalization, Edit Distance.</li>
            <li>Ng, H. T., et al. (2014). <em>The CoNLL-2014 Shared Task on Grammatical Error Correction.</em>
                Proceedings of CoNLL Shared Task.</li>
        </ol>
    </div>
    <div class='mg-card'>
        <div class='about-label'>Group Members / Contributors</div>
    """, unsafe_allow_html=True)

    members = [
        ("A", "Member 1", "NIM: [Student ID]", "Lead Developer & NLP Pipeline"),
        ("B", "Member 2", "NIM: [Student ID]", "UI/UX Design & Frontend"),
        ("C", "Member 3", "NIM: [Student ID]", "Grammar Rule Engine & Testing"),
        ("D", "Member 4", "NIM: [Student ID]", "Documentation & Research"),
    ]
    for initial, name, nim, role in members:
        st.markdown(f"""
        <div class='member-card'>
            <div class='member-avatar'>{initial}</div>
            <div>
                <div style='font-weight:600;font-size:0.92rem;'>{name}</div>
                <div style='color:#9090A0;font-size:0.8rem;'>{nim} · {role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("""
    <div class='mg-card' style='background:linear-gradient(135deg,#FFF0EB,#FAFAFA);border-left:4px solid #FF6B35;'>
        <div class='about-label'>Course Information</div>
        <div style='display:grid;grid-template-columns:1fr 1fr;gap:0.6rem;font-size:0.88rem;color:#4A4A5A;'>
            <div><strong>Course:</strong> Natural Language Processing</div>
            <div><strong>Semester:</strong> Semester 6 / 2026 Year</div>
            <div><strong>Institution:</strong> Airlangga University</div>
            <!-- Bagian Supervisor dengan 2 nama turun ke bawah -->
            <div><strong>Supervisors:</strong><br>
                1. Endah Purwanti, S.Si., M.Kom.<br>
                2. Indah Werdiningsih, S.Si., M.Kom.
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)