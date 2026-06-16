import streamlit as st
import re
import string
from collections import defaultdict

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
}

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg);
    color: var(--dark);
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {visibility: hidden;}
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
.error-token {
    color: var(--red);
    font-weight: 700;
    text-decoration: underline wavy var(--red);
}
.correct-token {
    color: var(--green);
    font-weight: 700;
}
.pipeline-step {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 0.9rem;
}
.step-num {
    min-width: 32px;
    height: 32px;
    background: var(--orange);
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.85rem;
    flex-shrink: 0;
}
.step-body { flex: 1; }
.step-title { font-weight: 600; font-size: 0.95rem; margin-bottom: 2px; }
.step-desc  { color: var(--grey); font-size: 0.88rem; }
.arrow-down {
    text-align: center;
    color: var(--orange);
    font-size: 1.4rem;
    margin: 0.2rem 0;
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
.about-section { margin-bottom: 1.6rem; }
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
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# NLP BACKEND (Pure Python – no heavy deps)
# ─────────────────────────────────────────────

# Minimal English word dictionary (common words + corpus)
DICTIONARY = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll","m",
    "o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn",
    "weren","won","wouldn",
    # Common verbs
    "go","goes","went","gone","going","run","runs","ran","running",
    "eat","eats","ate","eaten","eating","write","writes","wrote","written",
    "read","reads","reading","play","plays","played","playing","work","works",
    "worked","working","study","studies","studied","studying","come","comes",
    "came","coming","see","sees","saw","seen","seeing","get","gets","got",
    "getting","make","makes","made","making","know","knows","knew","knowing",
    "think","thinks","thought","thinking","say","says","said","saying",
    "take","takes","took","taken","taking","give","give","gave","given",
    "look","looks","looked","looking","use","uses","used","using","find",
    "finds","found","finding","tell","tells","told","telling","ask","asks",
    "asked","asking","seem","seems","seemed","seeming","feel","feels","felt",
    "feeling","try","tries","tried","trying","call","calls","called","calling",
    "keep","keeps","kept","keeping","let","lets","letting","begin","begins",
    "began","begun","beginning","show","shows","showed","shown","showing",
    "hear","hears","heard","hearing","play","plays","played","playing",
    "put","puts","putting","bring","brings","brought","bringing",
    # Common nouns
    "time","year","people","way","day","man","woman","child","children",
    "world","life","hand","part","place","case","week","company","system",
    "program","question","government","number","night","point","home","water",
    "room","mother","area","money","story","fact","month","lot","right","study",
    "book","eye","job","word","business","issue","side","kind","head","house",
    "service","friend","father","power","hour","game","line","end","plan",
    "form","face","street","car","city","community","name","team","minute",
    "field","air","teacher","force","education","school","family","student",
    "group","country","problem","hand","class","turn","state","public",
    "phone","door","food","table","computer","phone","app","data","test",
    "result","report","paper","class","office","health","reason","part",
    "sentence","text","word","language","error","grammar","spelling","check",
    # Adjectives / adverbs
    "good","new","first","last","long","great","little","own","right","big",
    "high","small","large","next","early","old","young","important","few",
    "public","bad","same","able","every","everyday","always","never",
    "often","sometimes","usually","today","yesterday","tomorrow",
    "please","thank","sorry","hello","bye","yes","sir","madam",
}

# Common misspelling → correct mapping (supplement Levenshtein)
SPELL_CORRECTIONS = {
    "scool": "school",
    "schol": "school",
    "shcool": "school",
    "recieve": "receive",
    "beleive": "believe",
    "freind": "friend",
    "wierd": "weird",
    "occured": "occurred",
    "seperate": "separate",
    "definately": "definitely",
    "goverment": "government",
    "studing": "studying",
    "teh": "the",
    "adn": "and",
    "hav": "have",
    "wont": "won't",
    "dont": "don't",
    "cant": "can't",
    "im": "I'm",
    "everday": "everyday",
    "evryday": "everyday",
    "languege": "language",
    "languaje": "language",
    "grammer": "grammar",
    "gramer": "grammar",
    "speling": "spelling",
    "cheking": "checking",
    "errror": "error",
    "sentance": "sentence",
}

# Simple POS tagger using pattern rules
PRONOUNS_3S = {"she", "he", "it"}  # 3rd person singular → verb needs -s
PRONOUNS_ALL = {"i","you","we","they","she","he","it","they"}

POS_MAP = {
    "she": "PRP", "he": "PRP", "it": "PRP", "they": "PRP",
    "i": "PRP", "we": "PRP", "you": "PRP", "me": "PRP",
    "him": "PRP", "her": "PRP", "us": "PRP", "them": "PRP",
    "the": "DT", "a": "DT", "an": "DT",
    "is": "VBZ", "are": "VBP", "was": "VBD", "were": "VBD",
    "has": "VBZ", "have": "VBP", "had": "VBD",
    "does": "VBZ", "do": "VBP", "did": "VBD",
    "goes": "VBZ", "go": "VB",
    "to": "TO", "not": "RB", "never": "RB", "always": "RB",
    "everyday": "RB", "today": "RB", "yesterday": "RB",
    "and": "CC", "but": "CC", "or": "CC",
    "in": "IN", "on": "IN", "at": "IN", "for": "IN",
    "with": "IN", "by": "IN", "of": "IN", "from": "IN",
}

# Grammar rules: (subject_pronoun, base_verb) → corrected_verb
GRAMMAR_RULES = {
    ("she", "go"):   "goes",
    ("he",  "go"):   "goes",
    ("it",  "go"):   "goes",
    ("she", "have"): "has",
    ("he",  "have"): "has",
    ("it",  "have"): "has",
    ("she", "do"):   "does",
    ("he",  "do"):   "does",
    ("it",  "do"):   "does",
    ("she", "run"):  "runs",
    ("he",  "run"):  "runs",
    ("it",  "run"):  "runs",
    ("she", "play"): "plays",
    ("he",  "play"): "plays",
    ("it",  "play"): "plays",
    ("she", "work"): "works",
    ("he",  "work"): "works",
    ("it",  "work"): "works",
    ("she", "eat"):  "eats",
    ("he",  "eat"):  "eats",
    ("it",  "eat"):  "eats",
    ("she", "write"):"writes",
    ("he",  "write"):"writes",
    ("she", "study"):"studies",
    ("he",  "study"):"studies",
    ("she", "come"): "comes",
    ("he",  "come"): "comes",
    ("i",   "goes"): "go",
    ("they","goes"): "go",
    ("we",  "goes"): "go",
    ("you", "goes"): "go",
    ("i",   "is"):   "am",
    ("they","is"):   "are",
    ("we",  "is"):   "are",
    ("you", "is"):   "are",
}


def levenshtein(s1: str, s2: str) -> int:
    """Compute Levenshtein edit distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    if not s2:
        return len(s1)
    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr = [i + 1]
        for j, c2 in enumerate(s2):
            curr.append(min(prev[j+1]+1, curr[j]+1, prev[j]+(c1 != c2)))
        prev = curr
    return prev[-1]


def best_spell_suggestion(token: str, vocab: set, max_dist: int = 2) -> str | None:
    """Find closest word in vocab by Levenshtein distance."""
    token_lower = token.lower()
    # Check hardcoded map first
    if token_lower in SPELL_CORRECTIONS:
        return SPELL_CORRECTIONS[token_lower]
    best_word, best_dist = None, max_dist + 1
    for word in vocab:
        d = levenshtein(token_lower, word)
        if d < best_dist:
            best_dist, best_word = d, word
    return best_word if best_dist <= max_dist else None


def tokenize(text: str) -> list[str]:
    """Simple whitespace + punctuation-aware tokenizer."""
    tokens = re.findall(r"[\w']+|[.,!?;:]", text)
    return tokens


def pos_tag(tokens: list[str]) -> list[tuple[str, str]]:
    """Rule-based POS tagger."""
    tagged = []
    for tok in tokens:
        tl = tok.lower()
        if tl in POS_MAP:
            tag = POS_MAP[tl]
        elif tok in string.punctuation:
            tag = "PUNCT"
        elif tl.endswith("ing"):
            tag = "VBG"
        elif tl.endswith("ed"):
            tag = "VBD"
        elif tl.endswith("ly"):
            tag = "RB"
        elif tl.endswith("s") and tl not in DICTIONARY:
            tag = "NNS"
        elif tl not in DICTIONARY:
            tag = "UNK"
        else:
            tag = "NN"
        tagged.append((tok, tag))
    return tagged


def check_spelling(tokens: list[str]) -> dict[str, str]:
    """Return {misspelled_token: suggestion}."""
    errors = {}
    for tok in tokens:
        tl = tok.lower()
        if tl in string.punctuation or tok.isnumeric():
            continue
        if tl not in DICTIONARY and tl not in PRONOUNS_ALL:
            suggestion = best_spell_suggestion(tl, DICTIONARY)
            if suggestion:
                errors[tok] = suggestion
    return errors


def check_grammar(tokens: list[str]) -> dict[int, tuple[str, str]]:
    """Return {index: (wrong_token, suggestion)} for grammar errors."""
    errors = {}
    tl = [t.lower() for t in tokens]
    for i, tok in enumerate(tl):
        if tok in PRONOUNS_ALL and i + 1 < len(tl):
            next_tok = tl[i+1]
            key = (tok, next_tok)
            if key in GRAMMAR_RULES:
                errors[i+1] = (tokens[i+1], GRAMMAR_RULES[key])
    return errors


def analyze(text: str):
    """Full NLP pipeline. Returns structured result dict."""
    # Step 1: Preprocessing
    lowered = text.lower()
    tokens = tokenize(text)
    tokens_lower = [t.lower() for t in tokens]

    # Step 2: POS Tagging
    pos_tags = pos_tag(tokens)

    # Step 3 & 4: Spell check + Levenshtein
    spell_errors = check_spelling(tokens)

    # Step 5: Grammar check
    grammar_errors = check_grammar(tokens)

    # Step 6: Merge errors and build corrected text
    corrections = {}

    # Add spell corrections
    for wrong, right in spell_errors.items():
        corrections[wrong.lower()] = {
            "original": wrong,
            "corrected": right,
            "type": "Spelling",
            "reason": f"Levenshtein distance = {levenshtein(wrong.lower(), right)} (closest match in dictionary)",
        }

    # Add grammar corrections (by index to avoid overwriting spell fixes)
    grammar_by_token = {}
    for idx, (wrong, right) in grammar_errors.items():
        # Don't double-count if already a spell error
        if wrong.lower() not in corrections:
            grammar_by_token[wrong.lower()] = {
                "original": wrong,
                "corrected": right,
                "type": "Grammar",
                "reason": f"Subject-verb agreement: subject requires '{right}' form",
            }
    corrections.update(grammar_by_token)

    # Build corrected tokens
    corrected_tokens = []
    for tok in tokens:
        tl = tok.lower()
        if tl in corrections:
            corrected_tokens.append(corrections[tl]["corrected"])
        else:
            corrected_tokens.append(tok)
    corrected_text = " ".join(corrected_tokens)
    # Fix spacing before punctuation
    corrected_text = re.sub(r" ([.,!?;:])", r"\1", corrected_text)

    return {
        "original": text,
        "lowered": lowered,
        "tokens": tokens,
        "pos_tags": pos_tags,
        "spell_errors": spell_errors,
        "grammar_errors": grammar_errors,
        "corrections": corrections,
        "corrected_text": corrected_text,
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
        Built with Streamlit · NLTK · TextBlob<br>
        LanguageTool · Levenshtein
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PAGE 1 – HOME / LANDING
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
            tokenization, POS tagging, Levenshtein distance, and rule-based grammar checking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='mg-card' style='text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>🔡</div>
            <div style='font-weight:700; margin-bottom:0.3rem;'>Spell Checking</div>
            <div style='color:#9090A0; font-size:0.88rem;'>Identify misspelled words using dictionary lookup & Levenshtein distance</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='mg-card' style='text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>🏷️</div>
            <div style='font-weight:700; margin-bottom:0.3rem;'>POS Tagging</div>
            <div style='color:#9090A0; font-size:0.88rem;'>Assign grammatical categories to each word using rule-based NLP tagging</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='mg-card' style='text-align:center;'>
            <div style='font-size:2rem; margin-bottom:0.5rem;'>📐</div>
            <div style='font-weight:700; margin-bottom:0.3rem;'>Grammar Rules</div>
            <div style='color:#9090A0; font-size:0.88rem;'>Apply subject-verb agreement and other grammatical rule-based corrections</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Preview example
    st.markdown("""
    <div class='mg-card'>
        <div style='font-weight:700; font-size:1rem; margin-bottom:0.8rem;'>
            📋 Example Output Preview
        </div>
        <div style='color:#9090A0; font-size:0.85rem; margin-bottom:0.5rem;'>Input sentence:</div>
        <div class='preview-box'>
            She <span class='error-token'>[go]</span> to <span class='error-token'>[scool]</span> everyday.
        </div>
        <div style='color:#9090A0; font-size:0.85rem; margin: 0.8rem 0 0.4rem 0;'>Corrected output:</div>
        <div class='result-box'>
            ✅ She <strong>goes</strong> to <strong>school</strong> everyday.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🚀 Try the Grammar Checker Now"):
        st.session_state["nav_to_checker"] = True
        st.rerun()

    if st.session_state.get("nav_to_checker"):
        st.session_state["nav_to_checker"] = False
        # User must click the sidebar manually; give a friendly hint
        st.info("👈 Click **🔍 Grammar Checker** in the sidebar to get started!")


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

    user_text = st.text_area(
        "Input Text",
        value="She go to scool everyday",
        height=120,
        placeholder='e.g. "She go to scool everyday"',
        label_visibility="collapsed",
    )

    analyze_btn = st.button("🔍 Analyze Text", type="primary")

    if analyze_btn and user_text.strip():
        result = analyze(user_text.strip())

        st.markdown("<hr style='margin:1.5rem 0;'>", unsafe_allow_html=True)

        # ── Step indicators ──
        step_cols = st.columns(6)
        steps = ["Preprocess", "POS Tag", "Spell Check", "Levenshtein", "Grammar", "Output"]
        icons  = ["⚙️","🏷️","🔤","📐","📏","✅"]
        for i, (col, label, icon) in enumerate(zip(step_cols, steps, icons)):
            with col:
                st.markdown(f"""
                <div style='text-align:center; padding:0.5rem;
                     background:{"#FFF0EB" if i < 5 else "#F0FDF4"};
                     border-radius:8px; border:1px solid {"#FFD5C2" if i < 5 else "#86EFAC"};'>
                    <div style='font-size:1.1rem;'>{icon}</div>
                    <div style='font-size:0.72rem; font-weight:600; color:{"#FF6B35" if i < 5 else "#166534"};'>{label}</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Highlighted error text ──
        st.markdown("**📌 Detected Errors (highlighted)**")
        tokens = result["tokens"]
        corrections = result["corrections"]

        highlighted_parts = []
        for tok in tokens:
            tl = tok.lower()
            if tl in corrections:
                c = corrections[tl]
                badge_color = "#EF4444" if c["type"] == "Spelling" else "#F59E0B"
                label = "SP" if c["type"] == "Spelling" else "GR"
                highlighted_parts.append(
                    f'<span style="color:{badge_color}; font-weight:700; '
                    f'text-decoration:underline wavy {badge_color};" '
                    f'title="{c["type"]} error: suggest → {c["corrected"]}">'
                    f'{tok} <sup style="font-size:0.6em;background:{badge_color};'
                    f'color:white;padding:1px 4px;border-radius:3px;">{label}</sup></span>'
                )
            elif tok in string.punctuation:
                highlighted_parts.append(tok)
            else:
                highlighted_parts.append(f'<span style="color:#1E1E2E;">{tok}</span>')

        highlighted_html = " ".join(highlighted_parts)
        st.markdown(f"""
        <div class='mg-card' style='font-size:1.05rem; line-height:2;'>
            {highlighted_html}
            <div style='margin-top:0.8rem; font-size:0.78rem; color:#9090A0;'>
                <span style='color:#EF4444;'>■</span> Spelling Error &nbsp;&nbsp;
                <span style='color:#F59E0B;'>■</span> Grammar Error
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Corrections breakdown ──
        if corrections:
            st.markdown("**📋 Error Breakdown**")
            for _, c in corrections.items():
                type_color = "#EF4444" if c["type"] == "Spelling" else "#F59E0B"
                type_bg    = "#FEF2F2" if c["type"] == "Spelling" else "#FFFBEB"
                st.markdown(f"""
                <div class='mg-card' style='padding:0.9rem 1.2rem; display:flex; align-items:center; gap:1.2rem; flex-wrap:wrap;'>
                    <div style='font-size:1.3rem; font-weight:800; color:#EF4444;'>{c["original"]}</div>
                    <div style='color:#9090A0; font-size:1.1rem;'>→</div>
                    <div style='font-size:1.3rem; font-weight:800; color:#22C55E;'>{c["corrected"]}</div>
                    <div style='flex:1; text-align:right;'>
                        <span style='background:{type_bg}; color:{type_color}; font-size:0.75rem;
                              font-weight:700; padding:3px 9px; border-radius:20px;'>{c["type"]}</span>
                    </div>
                    <div style='width:100%; color:#6060A0; font-size:0.83rem;'>💡 {c["reason"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No errors detected in the input text!")

        # ── POS Tag table ──
        with st.expander("🏷️ View POS Tagging Results"):
            pos_data = {"Token": [], "Lowercase": [], "POS Tag": [], "Status": []}
            for tok, tag in result["pos_tags"]:
                tl = tok.lower()
                status = "❌ Error" if tl in corrections else "✅ OK"
                pos_data["Token"].append(tok)
                pos_data["Lowercase"].append(tl)
                pos_data["POS Tag"].append(tag)
                pos_data["Status"].append(status)
            import pandas as pd
            st.dataframe(pd.DataFrame(pos_data), use_container_width=True, hide_index=True)

        # ── Levenshtein table for spell errors ──
        if result["spell_errors"]:
            with st.expander("📐 Levenshtein Distance Details"):
                lev_rows = []
                for wrong, right in result["spell_errors"].items():
                    dist = levenshtein(wrong.lower(), right)
                    lev_rows.append({"Misspelled": wrong, "Suggestion": right, "Edit Distance": dist})
                import pandas as pd
                st.dataframe(pd.DataFrame(lev_rows), use_container_width=True, hide_index=True)

        # ── Final result ──
        st.markdown("<br>**✅ Final Corrected Text**", unsafe_allow_html=True)
        st.markdown(f"""
        <div class='result-box' style='font-size:1.2rem; letter-spacing:0.01em;'>
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
            "desc": "Raw user-provided sentence is received by the system.",
            "example": '"She go to scool everyday"',
            "detail": "The system accepts any English sentence. No preprocessing is done at this stage — the raw string is passed directly to the next step.",
        },
        {
            "title": "Text Preprocessing — Case Folding & Tokenization",
            "icon": "⚙️",
            "desc": "Convert to lowercase and split into individual tokens (words/punctuation).",
            "example": '["she", "go", "to", "scool", "everyday"]',
            "detail": "Case folding normalizes all characters to lowercase so that 'She' and 'she' are treated identically. Tokenization splits the string into a list of meaningful units using regex pattern matching on word boundaries.",
        },
        {
            "title": "POS Tagging — Part-of-Speech Assignment",
            "icon": "🏷️",
            "desc": "Each token receives a grammatical category tag.",
            "example": "[('she','PRP'), ('go','VB'), ('to','TO'), ('scool','UNK'), ('everyday','RB')]",
            "detail": "A rule-based tagger assigns tags like PRP (pronoun), VB (verb base), TO (preposition 'to'), NN (noun), RB (adverb), UNK (unknown). The UNK tag signals a potential out-of-vocabulary word, flagging it for spell checking.",
        },
        {
            "title": "Spell Checking — Dictionary Corpus Lookup",
            "icon": "🔤",
            "desc": "Each token is checked against a known English word corpus.",
            "example": '"scool" → NOT in dictionary → flagged as misspelled',
            "detail": "Every token is looked up in an English word dictionary. Tokens absent from the dictionary (and not special characters or numbers) are marked as spelling errors. Common pronouns and grammar words are whitelisted.",
        },
        {
            "title": "Levenshtein Distance — Spelling Correction",
            "icon": "📐",
            "desc": "The closest correct word is found by computing edit distance.",
            "example": 'levenshtein("scool", "school") = 1 → suggest "school"',
            "detail": "Levenshtein distance counts the minimum number of single-character edits (insertions, deletions, substitutions) needed to transform one word into another. The dictionary word with the smallest distance (≤ 2) becomes the correction suggestion.",
        },
        {
            "title": "Grammar Rule Checking — Subject-Verb Agreement",
            "icon": "📏",
            "desc": "Apply linguistic rules to detect grammatical errors.",
            "example": '"she" + "go" → Rule: 3rd-person singular needs -s → suggest "goes"',
            "detail": "The rule engine checks subject-verb pairs. If a 3rd-person singular pronoun (she/he/it) is followed by a base-form verb, it flags a subject-verb disagreement. A lookup table maps (subject, verb) pairs to their corrections.",
        },
        {
            "title": "Error Detection & Correction — Merge Results",
            "icon": "🔗",
            "desc": "Spelling and grammar corrections are unified into a single correction map.",
            "example": '{"go": "goes", "scool": "school"}',
            "detail": "Both spell-check and grammar-check results are merged. When the same token is flagged by both systems, the correction is unified. The corrected token list is assembled to produce the final output.",
        },
        {
            "title": "Output — Corrected Text",
            "icon": "✅",
            "desc": "The fully corrected sentence is returned to the user.",
            "example": '"She goes to school everyday"',
            "detail": "Corrected tokens are joined back into a sentence with proper spacing and punctuation. The result is displayed with highlighted changes and a detailed breakdown table.",
        },
    ]

    for i, step in enumerate(PIPELINE):
        arrow = '<div class="arrow-down">↓</div>' if i < len(PIPELINE)-1 else ""
        with st.expander(f'{step["icon"]} Step {i+1}: {step["title"]}', expanded=(i == 0)):
            col_a, col_b = st.columns([1, 1])
            with col_a:
                st.markdown(f"""
                <div style='font-size:0.9rem; color:#4A4A5A; line-height:1.7; margin-bottom:0.8rem;'>
                    {step["detail"]}
                </div>
                """, unsafe_allow_html=True)
            with col_b:
                st.markdown(f"""
                <div style='background:#FFF8F5; border:1.5px solid #FFD5C2; border-radius:8px; 
                     padding:0.8rem 1rem; font-size:0.85rem; font-family:monospace; color:#CC4400;'>
                    <div style='font-size:0.72rem; color:#9090A0; margin-bottom:4px; 
                         font-family:Inter,sans-serif; font-weight:600;'>EXAMPLE</div>
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
    <tr><td><strong>NLTK</strong></td><td>Tokenization & POS Tagging foundation</td><td>🔡 NLP Core</td></tr>
    <tr><td><strong>TextBlob</strong></td><td>Spell checking and basic grammar checking</td><td>🔤 Spell Check</td></tr>
    <tr><td><strong>LanguageTool</strong></td><td>Advanced rule-based grammar checking</td><td>📏 Grammar</td></tr>
    <tr><td><strong>Levenshtein (python-Levenshtein)</strong></td><td>Edit distance for spelling suggestion ranking</td><td>📐 Distance</td></tr>
    <tr><td><strong>Streamlit</strong></td><td>Web framework & interactive UI</td><td>🌐 Frontend</td></tr>
    <tr><td><strong>Pandas</strong></td><td>Tabular display of results & POS tags</td><td>📊 Data</td></tr>
    <tr><td><strong>Regex (re)</strong></td><td>Custom tokenization patterns</td><td>⚙️ Utility</td></tr>
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
        ("🔡", "Tokenization",
         "The process of splitting a string of text into individual units called tokens. "
         "In Mini Grammarly, regex-based tokenization handles words and punctuation separately, "
         "preserving contractions while correctly isolating sentence-ending punctuation."),
        ("🏷️", "Part-of-Speech (POS) Tagging",
         "Assigns a grammatical category (noun, verb, pronoun, adverb, etc.) to each token. "
         "This system uses a rule-based tagger with suffix heuristics (e.g., -ing → VBG, -ed → VBD) "
         "and a hardcoded lexicon for common function words."),
        ("📐", "Levenshtein Distance",
         "A string metric measuring the minimum number of single-character edits "
         "(insertions, deletions, substitutions) to transform one word into another. "
         "Used here to rank dictionary candidates when suggesting spelling corrections — "
         "the word with the smallest edit distance (≤ 2) is chosen as the best suggestion."),
        ("📏", "Rule-Based Grammar Checking",
         "Applies a set of handcrafted linguistic rules derived from English grammar principles. "
         "The primary rule enforced is subject-verb agreement: 3rd-person singular subjects "
         "(she/he/it) must be followed by the -s/-es form of a present-tense verb. "
         "The rule set is implemented as a lookup table of (subject, verb) → correction mappings."),
    ]

    for icon, title, desc in techniques:
        st.markdown(f"""
        <div class='mg-card' style='display:flex; gap:1rem; align-items:flex-start;'>
            <div style='font-size:2rem; margin-top:2px;'>{icon}</div>
            <div>
                <div style='font-weight:700; font-size:0.98rem; margin-bottom:0.3rem;'>{title}</div>
                <div style='color:#4A4A5A; font-size:0.88rem; line-height:1.7;'>{desc}</div>
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

    # Objective
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
    """, unsafe_allow_html=True)

    # Background
    st.markdown("""
    <div class='mg-card'>
        <div class='about-label'>Background Context</div>
        <p style='color:#4A4A5A; font-size:0.92rem; line-height:1.8; margin:0;'>
            Grammatical errors and spelling mistakes are among the most common challenges 
            faced by non-native English speakers and students. Commercial tools like Grammarly 
            employ large-scale neural language models; however, their internal workings remain 
            opaque. This project implements a <strong>transparent, rule-based NLP pipeline</strong> 
            that is interpretable and academically grounded, making it suitable for classroom 
            study of computational linguistics and NLP fundamentals.<br><br>
            The system addresses two core problems:<br>
            <strong>(1)</strong> <em>Spelling errors</em> — words that deviate from their correct form 
            (e.g., "scool" → "school"), detected via dictionary corpus lookup and corrected via 
            Levenshtein distance.<br>
            <strong>(2)</strong> <em>Grammatical errors</em> — structurally incorrect word usage 
            (e.g., "she go" → "she goes"), detected via POS tag patterns and rule-based subject-verb 
            agreement checking.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Journal References
    st.markdown("""
    <div class='mg-card'>
        <div class='about-label'>Journal & Reference Sources</div>
        <ol style='color:#4A4A5A; font-size:0.9rem; line-height:2; padding-left:1.2rem; margin:0;'>
            <li>
                Levenshtein, V. I. (1966). <em>Binary codes capable of correcting deletions, insertions, 
                and reversals.</em> Soviet Physics Doklady, 10(8), 707–710.
            </li>
            <li>
                Bird, S., Klein, E., & Loper, E. (2009). <em>Natural Language Processing with Python.</em> 
                O'Reilly Media. (NLTK reference)
            </li>
            <li>
                Loria, S. (2020). <em>TextBlob: Simplified Text Processing.</em> 
                Retrieved from https://textblob.readthedocs.io/
            </li>
            <li>
                Naber, D. (2003). <em>A Rule-Based Style and Grammar Checker.</em> 
                Diploma Thesis, University of Bielefeld. (LanguageTool basis)
            </li>
            <li>
                Jurafsky, D. & Martin, J. H. (2023). <em>Speech and Language Processing (3rd ed. draft).</em> 
                Stanford University. Chapter 2: Regular Expressions, Text Normalization, Edit Distance.
            </li>
            <li>
                Ng, H. T., Wu, S. M., Briscoe, T., Hadiwinoto, C., Susanto, R. H., & Bryant, C. (2014). 
                <em>The CoNLL-2014 Shared Task on Grammatical Error Correction.</em> 
                Proceedings of CoNLL Shared Task.
            </li>
        </ol>
    </div>
    """, unsafe_allow_html=True)

    # Group Members
    st.markdown("""
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
                <div style='font-weight:600; font-size:0.92rem;'>{name}</div>
                <div style='color:#9090A0; font-size:0.8rem;'>{nim} · {role}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Course info
    st.markdown("""
    <div class='mg-card' style='background:linear-gradient(135deg,#FFF0EB,#FAFAFA); border-left:4px solid #FF6B35;'>
        <div class='about-label'>Course Information</div>
        <div style='display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; font-size:0.88rem; color:#4A4A5A;'>
            <div><strong>Course:</strong> Natural Language Processing</div>
            <div><strong>Semester:</strong> [Semester / Year]</div>
            <div><strong>Institution:</strong> [University Name]</div>
            <div><strong>Supervisor:</strong> [Lecturer Name]</div>
        </div>
    </div>
    """, unsafe_allow_html=True)