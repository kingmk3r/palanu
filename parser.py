#!/usr/bin/env python3
"""
parser.py -- reference tokenizer, PEG parser and lexicon validator for PALANU.

Stdlib only.  Usage:
    python3 parser.py                 # validate lexicon, parse every sample, run negative tests
    python3 parser.py --update-spec   # also regenerate the generated tables inside spec.md
    python3 parser.py "ta ka piya tu" # parse your own sentence(s) and print the tree

Single source of truth: the lexicon, the PEG grammar and the sample corpus live in
this file; the tables in spec.md are generated from them (--update-spec).
"""
import os
import re
import sys
import itertools
from collections import Counter

# ---------------------------------------------------------------------------
# 1. PHONOLOGY
# ---------------------------------------------------------------------------
STRONG = "ptksc"   # obstruents: only ever word-initial  (c = /tS/)
SOFT = "mnlyw"     # sonorants: only ever word-internal (and n = word-final coda)
VOWELS = "aeiou"
LETTERS = set(STRONG + SOFT + VOWELS)
BANNED_SYLLABLES = {"ci", "yi", "wu"}   # ci~ti (palatalisation), yi~i, wu~u

# Syllable sets
INITIAL_SYLS = [c + v for c in STRONG for v in VOWELS if c + v not in BANNED_SYLLABLES]
MEDIAL_SYLS = [c + v for c in SOFT for v in VOWELS if c + v not in BANNED_SYLLABLES]

WORD_RE = re.compile(r"^[ptksc][aeiou](?:[mnlyw][aeiou])*n?$")
PARTICLE_RE = re.compile(r"^[ptksc][aeiou]n?$")
ROOT_RE = re.compile(r"^[ptksc][aeiou][mnlyw][aeiou]$")
SUFFIX_RE = re.compile(r"^[mnlyw][aeiou]$")


def syllables(word):
    """Split a native word into syllables (every syllable = C V, plus optional final n)."""
    out, i = [], 0
    while i < len(word):
        syl = word[i:i + 2]
        i += 2
        if i == len(word) - 1 and word[i] == "n":
            syl += "n"
            i += 1
        out.append(syl)
    return out


def phonotactic_errors(word):
    errs = []
    if not WORD_RE.match(word):
        errs.append("shape is not S V (W V)* (n)")
    else:
        for s in syllables(word):
            if s.rstrip("n") in BANNED_SYLLABLES and len(s.rstrip("n")) == 2:
                errs.append("banned syllable '%s'" % s.rstrip("n"))
    return errs


# ---------------------------------------------------------------------------
# 2. LEXICON  (form | class | gloss-tag | meaning)
# ---------------------------------------------------------------------------
# 48 particles = every legal one-syllable word.  Consonant = family, vowel = member.
PARTICLES_SRC = """
pa  PREP  to       to, toward, for (goal, recipient, beneficiary)
pe  PREP  from     from, since; than (source, standard of comparison)
pi  PREP  at       at, in, on, during (place or time)
po  PREP  with     with, by, using (instrument, means, companion, manner)
pu  GEN   of       of (attaches a noun phrase to the preceding noun)
pan PREP  because  because of, due to
pen PREP  about    about, concerning
pin PREP  like     like, as (similarity)
pon PREP  per      according to (source of information)
pun CTX   CTX      context closer: 'as for / given / then'
ta  PRON  1SG      I, me
tu  PRON  2SG      you (one person)
te  PRON  3SG      he, she, they (one person)
to  DEM   that     it, that (distal; things)
ti  DEM   this     this (proximal)
tan PRON  1PL      we, us
tun PRON  2PL      you (several)
ten PRON  3PL      they (persons)
ton DEM   those    those, they (things)
tin DEM   these    these
ka  TAM   PRS      present / general (is, does)
ke  TAM   PST      past (was, did)
ko  TAM   FUT      future (will)
ku  TAM   IMP      imperative / optative (do!, let..., may...)
ki  TAM   HYP      hypothetical (would, could, might)
sa  CONJ  and      and
se  CONJ  or       or
su  CONJ  but      but
si  COND  if       if
so  SUB   that     that, which (opens a subordinate clause)
ca  Q     Q        yes/no-question opener
cu  SEP   SEP      statement opener / sentence separator
ce  NEG   NEG      not
co  WH    what     what, which (question word; relative pronoun in a so-clause)
can EVID  EV.SEEN  evidential: I witnessed / perceived it
cen EVID  EV.INFER evidential: I infer it
con EVID  EV.TOLD  evidential: I was told / reportedly
cun NAME  NAME     opens and closes a proper name or foreign word
kan DIGIT 0        zero
ken DIGIT 1        one
kin DIGIT 2        two
kon DIGIT 3        three
kun DIGIT 4        four
san DIGIT 5        five
sen DIGIT 6        six
sin DIGIT 7        seven
son DIGIT 8        eight
sun DIGIT 9        nine
"""

# 23 suffixes = every legal soft syllable.  Consonant = family, vowel = member.
SUFFIXES_SRC = """
ma AUG   very, great-, augmentative
me ATT   somewhat, -ish, attenuative
mi DIM   little, dear, diminutive
mo CMP   more (comparative)
mu SUP   most (superlative)
na PART  a part / piece / member of
ne PRIV  without, -less
ni SIM   like, -like, resembling
no OPP   opposite, un-, anti- (polar antonym)
nu COLL  the whole set / collective / system of
la PROG  ongoing (be ...-ing)
le INCH  begin to, become
li ITER  again, repeatedly, habitually
lo PERF  completed, already done
lu CESS  stop, cease, end
ya CAUS  make / cause to
ye POT   able to be ...-ed, -able
yo PASS  undergo, be ...-ed
yu RECP  each other / oneself
wa AGT   one who does (agent)
we INS   tool or means for
wi LOC   place for
wo RES   result, product, what is ...-ed
"""

# Roots: every content root is exactly C V C V (strong onset, soft medial).
# tier 1 = top-frequency core (must be mutually robust: no minimal pairs inside tier 1)
ROOTS_SRC = """
sama 1 be, same, equal                  | Skt sama, Eng same
kalo 1 do, make, work                   | Hindi karo 'do!'
pala 1 say, speak; word                 | Sp palabra
pelo 1 go, move, travel                 | Indonesian pergi
kome 1 come, arrive                     | Eng come
sile 1 see, look                        | Eng see
kono 1 know, understand                 | Eng know, Gk gno-
pena 1 think, consider                  | Fr penser
cana 1 want, wish                       | Hindi chahna
tene 1 have, hold, keep                 | Lat tenere
tona 1 give                             | Lat donare
tuma 1 take, get, receive               | Sp tomar
kaya 1 live; life; alive                | Arabic hayah
kula 1 eat; food                        | Swahili kula
piya 1 love; dear                       | Hindi piya
somo 1 person, human, someone           | Lat homo
kowa 1 thing, object, something         | -
tolo 1 place, space                     | Gk topos
temo 1 time, moment                     | Lat tempus
solu 1 sun; day                         | Lat sol
suyu 1 water, liquid                    | Turkish su, suyu
tela 1 earth, land, world               | Lat terra
tomu 1 house, home, building            | Gk domos
tanu 1 body                             | Skt tanu
poni 1 good, well                       | Lat bonus
tawa 1 big, large, great                | Mandarin da
pulu 1 many, much                       | Lat plus
sewa 1 all, every, whole                | Skt sarva
camo 1 way, path, road, method          | Sp camino
caye 1 need, must, should               | Hindi chahiye
pole 1 can, able; power                 | Sp poder
tuli 1 true, real, correct              | Eng true
kamu 1 other, different                 | -
kiyo 1 ask; question                    | -
sinu 1 new, fresh                       | Mandarin xin, Jp shin
pano 1 help, support                    | Mandarin bang
seni 1 feel; feeling                    | Lat sentire
kawe 1 use, employ                      | -
cenu 1 name; call                       | Swahili jina
sola 2 one, alone, only                 | Sp solo
kene 2 woman, female                    | Gk gyne
tano 2 man, male                        | Gk andr-
pemo 2 child, young                     | -
pamu 2 family, household                | Lat familia
sawi 2 friend                           | Arabic sahib
kuyu 2 group, together                  | -
pane 2 parent                           | Lat parens
kemo 2 head                             | -
tewi 2 hand, arm; touch                 | -
pewe 2 foot, leg                        | Lat pes
kole 2 heart, center, inside            | Lat cor
pilo 2 fire, heat, warm                 | Gk pyr
pawe 2 air, wind, breath                | -
sela 2 sky, above, heaven               | Lat caelum
pewo 2 stone, rock, hard                | Gk petra
kiwa 2 tree, plant, wood                | -
kolo 2 light, bright, clear             | -
suma 2 night, evening                   | -
sowa 2 sea, ocean                       | -
tiwe 2 animal                           | -
peya 2 money, price, value              | Swahili pesa
pinu 2 drink                            | Hindi pina
kanu 2 number, count, amount            | -
kana 2 song, music; sing                | Hindi gana
sayo 2 reason, cause                    | -
sala 2 peace, calm, rest                | Arabic salam
tuwa 2 fight, conflict                  | -
sowi 2 free, unbound                    | -
tomo 2 law, rule, norm                  | Gk nomos
sema 2 sign, meaning, symbol            | Gk sema
sono 2 sound, voice                     | Lat sonus
tayo 2 long, far                        | -
kuwi 2 fast, quick                      | -
suwe 2 easy, simple                     | -
sulo 2 beautiful                        | Hindi sundar
coyo 2 joy, happy, glad                 | Eng joy
kiwe 2 hope                             | -
temu 2 sleep                            | Jp nemu
tana 2 die; death                       | Gk thanatos
pawa 2 open                             | -
kenu 2 find, discover                   | -
tewo 2 stay, remain, wait               | -
tole 2 try, attempt                     | -
tali 2 line, rope; connect              | Malay tali
pume 2 front, before                    | -
kulu 2 circle, cycle; year              | Gk kyklos
cewe 2 self, own                        | -
tane 2 thanks, gratitude                | Ger danke
pemi 2 write, draw, mark                | -
temi 2 read                             | -
kimi 2 hear, listen                     | Jp kiku
kine 2 kind, type, class                | Gk genos
sowe 2 mind, spirit, soul               | Eng soul
sana 2 health, healthy, heal            | Lat sanus
kowe 2 fear, afraid                     | -
kele 2 choose, decide                   | Gk eklego
towe 2 trust, believe                   | -
puwe 2 pain, hurt                       | -
tuye 2 also, too, as well               | -
pele 2 cut, divide, split               | -
kumo 3 cloud                            | Jp kumo
pilu 3 rain                             | -
seme 3 seed, origin, source             | It seme
seyo 3 star                             | -
kuna 3 moon                             | Lat luna
kalu 3 mountain                         | -
telu 3 point, dot (decimal point)       | -
puyo 3 play, game                       | -
tume 3 dream                            | Jp yume
kume 3 leader, chief                    | -
puye 3 problem, trouble                 | -
kami 3 sacred, divine, god              | Jp kami
pomo 3 story, tale                      | -
pine 3 end, limit, goal                 | Lat finis
tule 3 order, rank, level               | -
cele 3 color, hue                       | -
pemu 3 sweet, pleasant                  | -
tuwi 3 clothes, cover                   | -
pelu 3 metal                            | -
kawi 3 clean, pure                      | -
tamu 3 set, collection, list            | -
cawe 3 example, instance                | -
puma 3 heavy; weight                    | -
pama 3 bridge, link across              | -
cowi 3 wonder, marvel                   | -
pome 3 form, shape                      | Lat forma
kiye 3 laugh, smile                     | -
comu 3 meat, flesh                      | -
tiyu 3 grain, rice, bread               | -
kemi 3 skin, surface                    | -
pomi 3 bone, frame                      | -
puna 3 carry, bear                      | -
kuye 3 cry, weep; tears                 | -
toye 2 exist, be present, there is      | -
piwo 2 happen, occur; event             | -
tama 3 side, edge                       | -
sumi 3 skill, art, craft                | -
comi 3 picture, image                   | -
pune 3 door, gate, entrance             | -
kewa 3 wall, barrier                    | -
poyo 3 box, container                   | -
tiye 3 follow, accompany                | -
cuma 3 succeed, achieve, win            | -
kiwo 3 danger, risk                     | -
sumu 3 add, plus, sum                   | Lat summa
tamo 3 multiply, times                  | -
sali 3 salt                             | Lat sal
cawa 3 tea                              | Mandarin cha
kiyu 3 anger, angry                     | -
cule 3 fly; wing                        | -
coli 3 state, condition, status         | -
suli 3 step, stage, phase               | -
"""


def _load():
    particles, suffixes, roots = {}, {}, {}
    for line in PARTICLES_SRC.strip().splitlines():
        form, cls, tag, meaning = line.split(None, 3)
        particles[form] = {"cls": cls, "tag": tag, "meaning": meaning}
    for line in SUFFIXES_SRC.strip().splitlines():
        form, tag, meaning = line.split(None, 2)
        suffixes[form] = {"tag": tag, "meaning": meaning}
    for line in ROOTS_SRC.strip().splitlines():
        left, hook = line.split("|")
        form, tier, gloss = left.split(None, 2)
        if form in roots:
            raise SystemExit("duplicate root in source: " + form)
        roots[form] = {"tier": int(tier), "gloss": gloss.strip(), "hook": hook.strip()}
    return particles, suffixes, roots


PARTICLES, SUFFIXES, ROOTS = _load()


# ---------------------------------------------------------------------------
# 3. TOKENIZER  (sound-stream segmentation -> morpheme analysis)
# ---------------------------------------------------------------------------
class ParseError(Exception):
    pass


class Token:
    __slots__ = ("text", "cls", "gloss", "morphs", "plural", "surface")

    def __init__(self, text, cls, gloss, morphs=(), plural=False, surface=None):
        self.text, self.cls, self.gloss = text, cls, gloss
        self.morphs, self.plural = list(morphs), plural
        self.surface = surface or text

    def __repr__(self):
        return "%s/%s" % (self.surface, self.cls)


def normalize(text):
    """Lower-case; punctuation is decorative (becomes a space); hyphens may mark
    morpheme or compound boundaries for teaching and are simply removed."""
    text = text.lower().replace("-", "")
    text = re.sub(r"[.,;:!?\"'()\[\]—–]", " ", text)
    bad = sorted(set(ch for ch in text if not ch.isspace() and ch not in LETTERS))
    if bad:
        raise ParseError("letters outside the 15-letter alphabet: %s" % "".join(bad))
    return text


def segment_stream(stream):
    """Recover words from an unbroken phoneme stream.  The only rule needed:
    every strong consonant (p t k s c) begins a new word.  A word-initial 'cun'
    opens a name frame (no root may begin with cun-) whose raw content runs to
    the next 'cun'.  Returns (kind, text, start, end) units."""
    out, i, n = [], 0, len(stream)
    while i < n:
        if stream[i] not in STRONG:
            raise ParseError("position %d: a word must begin with p/t/k/s/c, found '%s'"
                             % (i, stream[i]))
        if stream.startswith("cun", i):
            k = stream.find("cun", i + 3)
            if k < 0:
                raise ParseError("name frame opened with 'cun' is never closed")
            if k == i + 3:
                raise ParseError("empty name frame")
            out.append(("NAME", stream[i + 3:k], i, k + 3))
            i = k + 3
            continue
        j = i + 1
        while j < n and stream[j] not in STRONG:
            j += 1
        out.append(("WORD", stream[i:j], i, j))
        i = j
    return out


def first_gloss(gloss):
    return re.split(r"[,;]", gloss)[0].strip().replace(" ", ".")


def analyse(word):
    """Turn one native word into a Token (particle, or root + suffixes + plural)."""
    errs = phonotactic_errors(word)
    if errs:
        raise ParseError("'%s': %s" % (word, "; ".join(errs)))
    syls = syllables(word)
    if len(syls) == 1:                      # one syllable  => particle (closed class)
        if word not in PARTICLES:
            raise ParseError("'%s' is not a particle" % word)
        p = PARTICLES[word]
        return Token(word, p["cls"], p["tag"], [word])
    root, rest = word[:4], word[4:]          # >= two syllables => content word
    if root not in ROOTS:
        raise ParseError("'%s': unknown root '%s'" % (word, root))
    plural = rest.endswith("n")
    if plural:
        rest = rest[:-1]
    sufs = [rest[k:k + 2] for k in range(0, len(rest), 2)]
    for s in sufs:
        if s not in SUFFIXES:
            raise ParseError("'%s': unknown suffix '-%s'" % (word, s))
    gloss = "-".join([first_gloss(ROOTS[root]["gloss"])] + [SUFFIXES[s]["tag"] for s in sufs])
    if plural:
        gloss += "-PL"
    return Token(word, "CONTENT", gloss, [root] + ["-" + s for s in sufs] + (["-n"] if plural else []),
                 plural)


def tokenize(text):
    """Tokenize running text.  Spaces are optional: the stream is segmented by sound
    alone, and if the writer used spaces they must agree with that segmentation."""
    norm = normalize(text)
    stream = re.sub(r"\s+", "", norm)
    units = segment_stream(stream)
    allowed = set()
    for kind, w, a, b in units:
        allowed.update((a, b))
        if kind == "NAME":
            allowed.update(range(a + 3, b - 2))      # anything goes inside a name frame
    pos = 0
    for ch in norm:
        if ch.isspace():
            if pos not in allowed:
                raise ParseError("a written space falls inside a word (stream position %d)" % pos)
        else:
            pos += 1
    tokens = []
    for kind, w, a, b in units:
        if kind == "NAME":
            tokens.append(Token(w, "NAME", "NAME", [w], surface="cun %s cun" % w))
        else:
            tokens.append(analyse(w))
    return tokens


def count_segmentations(stream):
    """Brute-force check of self-segmentation: count every way of cutting a
    (name-free) phoneme stream into lexically valid words.  Must be exactly 1."""
    n = len(stream)
    ways = [0] * (n + 1)
    ways[n] = 1
    for i in range(n - 1, -1, -1):
        for j in range(i + 1, n + 1):
            if ways[j]:
                try:
                    analyse(stream[i:j])
                except ParseError:
                    continue
                ways[i] += ways[j]
    return ways[0]


# ---------------------------------------------------------------------------
# 4. GRAMMAR  -- this PEG text is the normative grammar (it is printed verbatim
#    in spec.md) and it is *executed* by the small packrat engine below.
#    UPPERCASE = token class, 'x' = literal word, lowercase = rule.
# ---------------------------------------------------------------------------
GRAMMAR = r"""
text       <- opener? body (opener body)* !.
opener     <- SEP / Q
body       <- context* (chain / fragment)
context    <- (condition / adjunct / npcore) CTX
condition  <- COND clause
chain      <- clause (CONJ clause)*
fragment   <- subject
clause     <- subject? predicate
subject    <- npcore (CONJ npcore)*
predicate  <- TAM EVID? NEG? vp?
vp         <- verb object? adjunct* complement?
verb       <- CONTENT
object     <- nplist
nplist     <- npcore (CONJ npcore !TAM)*
complement <- SUB clause
adjunct    <- PREP (complement / nplist)
npcore     <- head modifier* genitive* relative?
head       <- CONTENT / PRON / DEM / WH / numeral / NAME
modifier   <- CONTENT / DEM / WH / numeral / NAME
genitive   <- GEN npcore
relative   <- SUB clause
numeral    <- DIGIT+ ('telu' DIGIT+)? ('pole' DIGIT+)?
"""

TOKEN_CLASSES = {"SEP", "Q", "CTX", "COND", "CONJ", "TAM", "EVID", "NEG", "CONTENT", "SUB",
                 "PREP", "PRON", "DEM", "WH", "NAME", "GEN", "DIGIT"}


def compile_peg(text):
    """Parse the PEG notation above into nested tuples."""
    rules, order = {}, []
    for raw in text.strip().splitlines():
        line = raw.split("#")[0].strip()
        if not line:
            continue
        name, body = [x.strip() for x in line.split("<-", 1)]
        toks = re.findall(r"'[^']*'|[A-Za-z_]+|[/()*+?&!.]", body)
        pos = [0]

        def peek():
            return toks[pos[0]] if pos[0] < len(toks) else None

        def take():
            pos[0] += 1
            return toks[pos[0] - 1]

        def alt():
            seqs = [seq()]
            while peek() == "/":
                take()
                seqs.append(seq())
            return seqs[0] if len(seqs) == 1 else ("alt", seqs)

        def seq():
            items = []
            while peek() not in (None, "/", ")"):
                items.append(prefix())
            return items[0] if len(items) == 1 else ("seq", items)

        def prefix():
            if peek() in ("&", "!"):
                op = take()
                return ("and" if op == "&" else "not", suffix())
            return suffix()

        def suffix():
            e = primary()
            while peek() in ("*", "+", "?"):
                e = ({"*": "star", "+": "plus", "?": "opt"}[take()], e)
            return e

        def primary():
            t = take()
            if t == "(":
                e = alt()
                assert take() == ")", "unbalanced parenthesis in rule " + name
                return e
            if t == ".":
                return ("any",)
            if t.startswith("'"):
                return ("lit", t[1:-1])
            if t.isupper():
                assert t in TOKEN_CLASSES, "unknown token class " + t
                return ("cls", t)
            return ("ref", t)

        rules[name] = alt()
        order.append(name)
        assert pos[0] == len(toks), "trailing junk in rule " + name
    for name in order:   # every referenced rule must exist
        for ref in re.findall(r"\('ref', '(\w+)'\)", repr(rules[name])):
            assert ref in rules, "undefined rule " + ref
    return rules, order


RULES, RULE_ORDER = compile_peg(GRAMMAR)


class Parser:
    """Packrat interpreter for the compiled PEG.  Deterministic by construction:
    ordered choice, greedy repetition, no left recursion, so every input has
    at most one parse."""

    def __init__(self, tokens):
        self.toks, self.memo, self.furthest = tokens, {}, 0

    def parse(self):
        res = self.rule("text", 0)
        if res is None:
            at = self.toks[self.furthest] if self.furthest < len(self.toks) else "end of input"
            raise ParseError("no parse; stuck at token %d (%s)" % (self.furthest, at))
        return res[1]

    def rule(self, name, pos):
        key = (name, pos)
        if key not in self.memo:
            self.memo[key] = None
            r = self.match(RULES[name], pos)
            self.memo[key] = None if r is None else (r[0], (name, r[1]))
        return self.memo[key]

    def match(self, e, pos):
        kind = e[0]
        if kind in ("cls", "lit", "any"):
            if pos < len(self.toks):
                t = self.toks[pos]
                if kind == "any" or (kind == "cls" and t.cls == e[1]) or \
                        (kind == "lit" and t.text == e[1] and t.cls != "NAME"):
                    self.furthest = max(self.furthest, pos + 1)
                    return pos + 1, [t]
            return None
        if kind == "ref":
            r = self.rule(e[1], pos)
            return None if r is None else (r[0], [r[1]])
        if kind == "seq":
            kids = []
            for sub in e[1]:
                r = self.match(sub, pos)
                if r is None:
                    return None
                pos, kids = r[0], kids + r[1]
            return pos, kids
        if kind == "alt":
            for sub in e[1]:
                r = self.match(sub, pos)
                if r is not None:
                    return r
            return None
        if kind in ("star", "plus"):
            kids, n = [], 0
            while True:
                r = self.match(e[1], pos)
                if r is None or r[0] == pos:
                    break
                pos, kids, n = r[0], kids + r[1], n + 1
            return (pos, kids) if (n or kind == "star") else None
        if kind == "opt":
            r = self.match(e[1], pos)
            return r if r is not None else (pos, [])
        if kind == "and":
            return (pos, []) if self.match(e[1], pos) is not None else None
        if kind == "not":
            return (pos, []) if self.match(e[1], pos) is None else None
        raise ValueError(kind)


TRANSPARENT = {"head", "modifier", "verb", "opener"}


def show(node):
    """Bracketed tree; trivial wrapper rules are flattened."""
    if isinstance(node, Token):
        return "%s:%s" % (node.surface, node.gloss)
    name, kids = node
    inner = " ".join(show(k) for k in kids)
    return inner if name in TRANSPARENT else "[%s %s]" % (name, inner)


def walk(node, path=()):
    yield node, path
    if not isinstance(node, Token):
        for k in node[1]:
            yield from walk(k, path + (node[0],))


def semantic_checks(tree):
    """Constraints stated in the spec that a context-free PEG cannot express."""
    errs = []
    for node, path in walk(tree):
        if isinstance(node, Token):
            continue
        name, kids = node
        if name == "verb" and kids[0].plural:
            errs.append("verb '%s' carries plural -n (only nominals pluralise)" % kids[0].text)
        if name == "relative":
            gap = [t for t, p in walk(node) if isinstance(t, Token) and t.cls == "WH"
                   and p.count("relative") == 1]
            if len(gap) != 1:
                errs.append("relative clause must contain exactly one 'co' (the gap); found %d"
                            % len(gap))
    return errs


def parse_text(text):
    toks = tokenize(text)
    tree = Parser(toks).parse()
    errs = semantic_checks(tree)
    if errs:
        raise ParseError("; ".join(errs))
    return toks, tree


# ---------------------------------------------------------------------------
# 5. SAMPLE CORPUS  (text | interlinear gloss | English | English syllabified)
#    The English syllabification is written out (dots = syllable breaks) so
#    the counts in the efficiency table can be audited by eye.
# ---------------------------------------------------------------------------
SAMPLES = [
    ("Plain transitive clause",
     "Ta ka piya tu.",
     "1SG PRS love 2SG",
     "I love you.",
     "I love you"),
    ("Past + witnessed evidential + recipient",
     "Te ke can tona kula pa somo pulu.",
     "3SG PST EV.SEEN give food to person many",
     "I saw her give food to many people.",
     "I saw her give food to ma.ny peo.ple"),
    ("Yes/no question",
     "Ca tu ka pala palanu?",
     "Q 2SG PRS speak word-COLL",
     "Do you speak Palanu?",
     "do you speak Pa.la.nu"),
    ("Content question (in situ) + phrasal compound",
     "Tu ke sile co pi tolo kiwa?",
     "2SG PST see what at place plant",
     "What did you see in the garden?",
     "what did you see in the gar.den"),
    ("Negation + cause + clause coordination + time",
     "Tan ko ce pelo pan pilu, su tan ko pelo pi solu pumeno.",
     "1PL FUT NEG go because rain but 1PL FUT go at day front-OPP",
     "We won't go because of the rain, but we'll go tomorrow.",
     "we won't go be.cause of the rain but we'll go to.mor.row"),
    ("Relative clause (gap = co) + copula + derivation",
     "Somo so co ke kalo ti ka sama konoyawa poni.",
     "person that REL PST make this PRS be know-CAUS-AGT good",
     "The person who made this is a good teacher.",
     "the per.son who made this is a good tea.cher"),
    ("Counterfactual conditional + perfective",
     "Si tu ke kome pun tan ki kulalo po tu.",
     "if 2SG PST come CTX 1PL HYP eat-PERF with 2SG",
     "If you'd come, we'd have eaten with you.",
     "if you'd come we'd have ea.ten with you"),
    ("Reported evidential + inchoative",
     "Tela ka con pilole.",
     "earth PRS EV.TOLD warm-INCH",
     "The Earth is said to be warming.",
     "the Earth is said to be warm.ing"),
    ("Inferred evidential + genitive",
     "Te ke cen pelo pe tomu pu te.",
     "3SG PST EV.INFER go from house of 3SG",
     "She must've left her house.",
     "she must've left her house"),
    ("Complement clause",
     "Ta ka kono so tu ka pala tuli.",
     "1SG PRS know that 2SG PRS say true",
     "I know you're telling the truth.",
     "I know you're tel.ling the truth"),
    ("Fronted context + numeral + place noun",
     "Pi solu ti pun somo ken kin kon ke kome pa konoyawi.",
     "at day this CTX person 1 2 3 PST come to know-CAUS-LOC",
     "Today, one hundred and twenty-three people came to the school.",
     "to.day one hun.dred and twen.ty three peo.ple came to the school"),
    ("Digit-string number",
     "Peya ka sama ken kin kon kun san.",
     "price PRS be 1 2 3 4 5",
     "The price is twelve thousand three hundred and forty-five.",
     "the price is twelve thou.sand three hun.dred and for.ty five"),
    ("Scientific numeral (mantissa telu fraction pole exponent)",
     "Somon pu tela ka kanu son telu kin pole sun.",
     "person-PL of earth PRS count 8 point 2 power 9",
     "There are 8.2 billion people on Earth.",
     "there are eight point two bil.lion peo.ple on Earth"),
    ("Proper name frame + calque + superlative",
     "Cun Ata cun ke pemi camonu pumemu pa penawe.",
     "NAME PST write way-COLL front-SUP for think-INS",
     "Ada wrote the first program for a computer.",
     "A.da wrote the first pro.gram for a com.pu.ter"),
    ("Comparative",
     "Ti ka tawamo pe to.",
     "this PRS big-CMP than that",
     "This is bigger than that.",
     "this is big.ger than that"),
    ("Imperative + plural",
     "Ku tona suyu pa tiwen.",
     "IMP give water to animal-PL",
     "Give the animals water.",
     "give the an.i.mals wa.ter"),
    ("Universal statement (UDHR art. 1, abridged)",
     "Somo sewa ka kayale pi sowi sa sama.",
     "person all PRS live-INCH in free and equal",
     "All human beings are born free and equal.",
     "all hu.man be.ings are born free and e.qual"),
    ("Poem: Suyu (Water)",
     "Pala ka pelo pin suyu,\n"
     "sa suyu ka pelo pa tolo sewa;\n"
     "cu tolo sewa ka kaya po suyu,\n"
     "sa somo sewa ka kaya po pala.\n"
     "Cu pala sewa ka sama ken.",
     "word PRS go like water\n"
     "and water PRS go to place all\n"
     "SEP place all PRS live with water\n"
     "and person all PRS live with word\n"
     "SEP word all PRS be 1",
     "Speech goes like water,\n"
     "and water goes to every place;\n"
     "every place lives by water,\n"
     "and every person lives by speech.\n"
     "All speech is one.",
     "speech goes like wa.ter\n"
     "and wa.ter goes to ev.ery place\n"
     "ev.ery place lives by wa.ter\n"
     "and ev.ery per.son lives by speech\n"
     "all speech is one"),
]

# Sentences that MUST be rejected (phonology, morphology, syntax, semantics).
NEGATIVE = [
    ("lapa ka kome", "word-initial soft consonant"),
    ("ta ka kaa", "vowel hiatus inside a word"),
    ("ta ka tawu", "banned syllable wu"),
    ("ta ka pinyo", "word-internal coda n"),
    ("ta ka pi ya tu", "space inside a word"),
    ("ta ka keyu", "well-formed but unassigned root"),
    ("ta ka piyaxa", "letter outside the alphabet"),
    ("ta ka konoyi", "banned syllable yi"),
    ("ta ka sama ko", "stray TAM marker after a complete clause"),
    ("ta tu ka pelo", "two subjects without a conjunction"),
    ("ka pelo ka pelo", "two sentences without an opener"),
    ("ta ka pelo pun", "dangling context closer"),
    ("ta ka pelon", "plural -n on a verb"),
    ("somo so ta ke sile ka poni", "relative clause without its co gap"),
    ("cun malia ka kome", "unclosed name frame"),
    ("sa ta ka pelo", "sentence-initial conjunction"),
    ("ta ka pu tolo", "genitive without a head noun"),
    ("ta ke ce can pelo", "evidential after negation (order is TAM EVID NEG)"),
]

# Particle glosses accepted in hand-written interlinear lines besides the tag.
GLOSS_ALT = {"co": {"REL"}, "pe": {"than"}, "pi": {"in", "on"}, "pa": {"for"},
             "pan": {"because"}, "to": {"it"}}

ENGLISH_RATE = 6.19   # syllables/s, English     (Pellegrino, Coupe & Marsico 2011)
PALANU_RATE = 7.8     # syllables/s, assumed = CV languages Japanese 7.84 / Spanish 7.82 (same study)


def word_syllables(tok):
    if tok.cls == "NAME":
        return 2 + max(1, len(re.findall(r"[aeiou]+", tok.text)))   # cun ... cun
    return len(syllables(tok.text))


def check_gloss(text, gloss):
    """Hand-written gloss must align 1:1 with tokens and agree with the lexicon."""
    errs = []
    for tline, gline in zip(text.splitlines(), gloss.splitlines()):
        toks, gl = tokenize(tline), gline.split()
        if len(toks) != len(gl):
            errs.append("gloss has %d items for %d words in: %s" % (len(gl), len(toks), tline))
            continue
        for t, g in zip(toks, gl):
            if t.cls == "NAME":
                ok = g == "NAME"
            elif t.cls == "CONTENT":
                want = t.gloss.split("-")
                got = g.split("-")
                senses = {s.strip().replace(" ", ".") for s in
                          re.split(r"[,;]", ROOTS[t.morphs[0]]["gloss"])}
                ok = len(want) == len(got) and got[1:] == want[1:] and got[0] in senses
            else:
                ok = g == t.gloss or g in GLOSS_ALT.get(t.text, set())
            if not ok:
                errs.append("gloss '%s' does not match '%s' (%s)" % (g, t.text, t.gloss))
    if len(text.splitlines()) != len(gloss.splitlines()):
        errs.append("gloss line count differs from text line count")
    return errs


def hamming1(a, b):
    return len(a) == len(b) and sum(x != y for x, y in zip(a, b)) == 1


def validate_lexicon():
    """Returns (errors, facts)."""
    errs, facts = [], {}
    for f in PARTICLES:
        if not PARTICLE_RE.match(f) or phonotactic_errors(f):
            errs.append("bad particle shape: " + f)
    for f in SUFFIXES:
        if not SUFFIX_RE.match(f) or f in BANNED_SYLLABLES:
            errs.append("bad suffix shape: " + f)
    for f in ROOTS:
        if not ROOT_RE.match(f) or phonotactic_errors(f):
            errs.append("bad root shape: " + f)
        if f.startswith("cun"):
            errs.append("root may not begin with cun- (reserved for name frames): " + f)
    # closed classes are complete: every legal monosyllable / soft syllable is used once
    all_mono = set(INITIAL_SYLS) | {s + "n" for s in INITIAL_SYLS}
    if set(PARTICLES) != all_mono:
        errs.append("particle set != all legal monosyllables: %s"
                    % sorted(all_mono ^ set(PARTICLES)))
    if set(SUFFIXES) != set(MEDIAL_SYLS):
        errs.append("suffix set != all legal soft syllables: %s"
                    % sorted(set(MEDIAL_SYLS) ^ set(SUFFIXES)))
    # tier-1 robustness: no two tier-1 roots differ by a single phoneme
    t1 = [f for f in ROOTS if ROOTS[f]["tier"] == 1]
    pairs = [(a, b) for i, a in enumerate(t1) for b in t1[i + 1:] if hamming1(a, b)]
    if pairs:
        errs.append("tier-1 minimal pairs: %s" % pairs)
    # glosses unique within roots (no accidental synonyms)
    heads = Counter(first_gloss(ROOTS[f]["gloss"]) for f in ROOTS)
    dup = [g for g, n in heads.items() if n > 1]
    if dup:
        errs.append("duplicate head glosses: %s" % dup)
    if not 150 <= len(ROOTS) <= 200:
        errs.append("root count %d outside 150-200" % len(ROOTS))
    space = [a + b for a in INITIAL_SYLS for b in MEDIAL_SYLS]
    facts.update(particles=len(PARTICLES), suffixes=len(SUFFIXES), roots=len(ROOTS),
                 tier1=len(t1), tier1_min_pairs=len(pairs), root_space=len(space),
                 free_roots=len(space) - len(ROOTS) - sum(1 for s in space if s.startswith("cun")))
    return errs, facts


def zipf_check(corpus_tokens):
    """In the sample corpus, the most frequent word types must be the shortest."""
    freq = Counter(t.text for t in corpus_tokens if t.cls != "NAME")
    ranked = [w for w, _ in freq.most_common()]
    top = ranked[:15]
    rest = ranked[15:]
    mean = lambda ws: sum(len(syllables(w)) for w in ws) / max(1, len(ws))
    return mean(top), mean(rest), freq.most_common(15)


# ---------------------------------------------------------------------------
# 6. GENERATED SPEC SECTIONS  (python3 parser.py --update-spec)
# ---------------------------------------------------------------------------
def md_particles():
    fam = {"p": "relators", "t": "persons & pointers", "k": "predicate markers / digits 0-4",
           "s": "clause linkers / digits 5-9", "c": "discourse & evidence"}
    rows = ["| form | class | gloss tag | meaning | family |", "|---|---|---|---|---|"]
    for f, p in PARTICLES.items():
        rows.append("| **%s** | %s | %s | %s | %s- %s |" % (f, p["cls"], p["tag"], p["meaning"],
                                                         f[0], fam[f[0]]))
    return "\n".join(rows)


def md_suffixes():
    fam = {"m": "degree", "n": "polarity & part", "l": "aspect", "y": "valency / voice",
           "w": "nominalisers"}
    rows = ["| suffix | tag | meaning | family | example |", "|---|---|---|---|---|"]
    ex = {"ma": "tawa-ma *huge*", "me": "poni-me *fairly good*", "mi": "pemo-mi *baby*",
          "mo": "tawa-mo *bigger*", "mu": "pume-mu *first*", "na": "kiwa-na *leaf*",
          "ne": "sono-ne *silent*", "ni": "sela-ni *sky-like = blue*", "no": "poni-no *bad*",
          "nu": "pala-nu *language*", "la": "kula-la *eating*", "le": "solu-le *morning*",
          "li": "kome-li *return*", "lo": "kula-lo *has eaten*", "lu": "temu-lu *wake up*",
          "ya": "kono-ya *teach*", "ye": "kalo-ye *possible*", "yo": "sile-yo *be seen*",
          "yu": "pala-yu *converse*", "wa": "kono-ya-wa *teacher*", "we": "pena-we *computer*",
          "wi": "kono-ya-wi *school*", "wo": "pemi-wo *text, book*"}
    for f, s in SUFFIXES.items():
        rows.append("| **-%s** | %s | %s | %s- %s | %s |" % (f, s["tag"], s["meaning"], f[0],
                                                          fam[f[0]], ex[f]))
    return "\n".join(rows)


def md_roots():
    rows = ["| # | root | tier | meaning | mnemonic hook |", "|---|---|---|---|---|"]
    for i, (f, r) in enumerate(sorted(ROOTS.items(), key=lambda kv: (kv[1]["tier"], kv[0])), 1):
        rows.append("| %d | **%s** | %d | %s | %s |" % (i, f, r["tier"], r["gloss"], r["hook"]))
    return "\n".join(rows)


def md_samples():
    out = []
    for i, (title, text, gloss, en, ensyl) in enumerate(SAMPLES, 1):
        out.append("**%d. %s**\n" % (i, title))
        out.append("```")
        for tl, gl in zip(text.splitlines(), gloss.splitlines()):
            toks = tokenize(tl)
            words = [t.surface if t.cls != "CONTENT" else "-".join(
                [t.morphs[0]] + [m[1:] for m in t.morphs[1:] if m != "-n"]) + ("-n" if t.plural else "")
                for t in toks]
            gls = gl.split()
            width = [max(len(w), len(g)) for w, g in zip(words, gls)]
            out.append(tl)
            out.append("  ".join(w.ljust(n) for w, n in zip(words, width)).rstrip())
            out.append("  ".join(g.ljust(n) for g, n in zip(gls, width)).rstrip())
            out.append("")
        out[-1] = "```"
        out.append("> " + en.replace("\n", "  \n> ") + "\n")
    return "\n".join(out)


def efficiency_rows():
    rows = []
    for i, (title, text, gloss, en, ensyl) in enumerate(SAMPLES, 1):
        toks = tokenize(text)
        p_syl = sum(word_syllables(t) for t in toks)
        p_seg = sum(len(t.text) + (6 if t.cls == "NAME" else 0) for t in toks)
        e_syl = sum(len(w.split(".")) for w in ensyl.split())
        rows.append((i, title, len(toks), p_syl, p_seg, len(en.split()), e_syl))
    return rows


def md_efficiency():
    rows = efficiency_rows()
    out = ["| # | sample | Palanu words | Palanu syll. | Palanu phonemes | English words | "
           "English syll. | syll. ratio P/E | est. time P/E |", "|---|---|---|---|---|---|---|---|---|"]
    tp = te = 0
    for i, title, w, ps, pg, ew, es in rows:
        tp, te = tp + ps, te + es
        out.append("| %d | %s | %d | %d | %d | %d | %d | %.2f | %.2f |" % (
            i, title.split(" (")[0], w, ps, pg, ew, es, ps / es,
            (ps / PALANU_RATE) / (es / ENGLISH_RATE)))
    out.append("| | **total** | | **%d** | | | **%d** | **%.2f** | **%.2f** |" % (
        tp, te, tp / te, (tp / PALANU_RATE) / (te / ENGLISH_RATE)))
    return "\n".join(out)


def md_facts():
    errs, f = validate_lexicon()
    return "\n".join([
        "| quantity | value |", "|---|---|",
        "| phonemes | 15 (5 strong + 5 soft consonants, 5 vowels) |",
        "| legal word-initial syllables (S V) | %d |" % len(INITIAL_SYLS),
        "| legal word-internal syllables (W V) | %d |" % len(MEDIAL_SYLS),
        "| max. phonotactic information per syllable | %.2f bits |" % (
            sum(__import__("math").log2(n) for n in (len(INITIAL_SYLS), len(MEDIAL_SYLS))) / 2),
        "| particles (all legal monosyllables) | %d |" % f["particles"],
        "| suffixes (all legal soft syllables) | %d |" % f["suffixes"],
        "| possible C V C V roots | %d (%d usable; the 5 cun- forms are reserved) |" % (
            f["root_space"], f["root_space"] - 5),
        "| roots assigned | %d (tier 1: %d) |" % (f["roots"], f["tier1"]),
        "| roots still free for future coinage | %d |" % f["free_roots"],
        "| minimal pairs inside tier 1 | %d |" % f["tier1_min_pairs"],
    ])


GENERATED = {"FACTS": md_facts, "PARTICLES": md_particles, "SUFFIXES": md_suffixes,
             "ROOTS": md_roots, "GRAMMAR": lambda: "```peg\n" + GRAMMAR.strip() + "\n```",
             "SAMPLES": md_samples, "EFFICIENCY": md_efficiency}


SPEC_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spec.md")


def update_spec(path=SPEC_PATH):
    with open(path, encoding="utf-8") as fh:
        doc = fh.read()
    for key, fn in GENERATED.items():
        pat = re.compile(r"(<!-- BEGIN:%s -->\n).*?(<!-- END:%s -->)" % (key, key), re.S)
        if not pat.search(doc):
            print("  (spec.md has no %s block; skipped)" % key)
            continue
        body = fn()
        doc = pat.sub(lambda m: m.group(1) + body + "\n" + m.group(2), doc)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    print("spec.md generated sections refreshed")


# ---------------------------------------------------------------------------
# 7. MAIN
# ---------------------------------------------------------------------------
def main(argv):
    if len(argv) > 1 and not argv[1].startswith("--"):
        for s in argv[1:]:
            try:
                toks, tree = parse_text(s)
                print(show(tree))
            except ParseError as e:
                print("REJECTED:", e)
        return 0
    failures = 0
    print("PALANU reference parser\n")
    print("[1] Lexicon")
    errs, facts = validate_lexicon()
    for e in errs:
        print("  FAIL", e)
    failures += len(errs)
    print("  %(particles)d particles, %(suffixes)d suffixes, %(roots)d roots (tier 1: %(tier1)d), "
          "%(free_roots)d free root slots; tier-1 minimal pairs: %(tier1_min_pairs)d" % facts)
    print("\n[2] Samples (spaced text, unspaced sound-stream, brute-force segmentation, PEG, gloss)")
    corpus, samples_ok = [], 0
    for i, (title, text, gloss, en, ensyl) in enumerate(SAMPLES, 1):
        try:
            toks, tree = parse_text(text)
            stream = re.sub(r"\s+", "", normalize(text))
            same = [t.text for t in tokenize(stream)] == [t.text for t in toks]
            if not same:
                raise ParseError("unspaced stream segments differently")
            names = re.findall(r"cun.*?cun", stream)
            pieces = [p for p in re.split(r"cun.*?cun", stream) if p]
            ways = [count_segmentations(p) for p in pieces]
            if any(w != 1 for w in ways):
                raise ParseError("segmentation not unique: %s" % ways)
            gerrs = check_gloss(text, gloss)
            if gerrs:
                raise ParseError("; ".join(gerrs))
            corpus += toks
            samples_ok += 1
            print("  ok  %2d  %-58s %2d words, %2d syll." % (
                i, text.replace("\n", " ")[:58], len(toks), sum(word_syllables(t) for t in toks)))
        except ParseError as e:
            failures += 1
            print("  FAIL %2d  %s\n        %s" % (i, text.replace("\n", " "), e))
    print("\n[3] Negative tests (each must be rejected)")
    rejected = 0
    for text, why in NEGATIVE:
        try:
            parse_text(text)
            failures += 1
            print("  FAIL accepted: %-28s (%s)" % (text, why))
        except ParseError as e:
            rejected += 1
            print("  ok  rejected: %-28s %s -> %s" % (text, "(" + why + ")", str(e)[:60]))
    print("\n[4] Zipf check on the sample corpus")
    top, rest, common = zipf_check(corpus)
    print("  15 most frequent word types: %s" % ", ".join("%s(%d)" % wc for wc in common))
    print("  mean syllables: top-15 = %.2f, all other types = %.2f" % (top, rest))
    if not top < rest:
        failures += 1
        print("  FAIL frequent words are not shorter")
    print("\n[5] Efficiency vs English (syllables)")
    rows = efficiency_rows()
    tp, te = sum(r[3] for r in rows), sum(r[6] for r in rows)
    print("  Palanu %d syll. vs English %d syll. (ratio %.2f); est. duration ratio %.2f "
          "at %.1f vs %.2f syll/s" % (tp, te, tp / te, (tp / PALANU_RATE) / (te / ENGLISH_RATE),
                                      PALANU_RATE, ENGLISH_RATE))
    print("\n[6] Palanu examples quoted in spec.md (informational: letter lists etc. are expected misses)")
    try:
        with open(SPEC_PATH, encoding="utf-8") as fh:
            doc = fh.read()
    except OSError:
        doc = ""
    full, frag, bad = 0, 0, []
    for sp in dict.fromkeys(re.findall(r"`([a-z][a-z \-]*[a-z])`", doc)):
        try:
            tokenize(sp)
        except ParseError as e:
            bad.append((sp, str(e)))
            continue
        try:
            parse_text(sp)
            full += 1
        except ParseError:
            frag += 1
    print("  %d spans parse as complete sentences, %d are valid word sequences (phrases), "
          "%d are not Palanu text:" % (full, frag, len(bad)))
    for sp, e in bad:
        print("    - %-28s %s" % (sp, e[:60]))
    if "--update-spec" in argv:
        update_spec(SPEC_PATH)
    n = len(SAMPLES)
    print("\nRESULT: %s -- %d/%d samples parsed, %d/%d negative tests rejected, lexicon %s" % (
        "PASS" if failures == 0 else "FAIL", samples_ok, n,
        rejected, len(NEGATIVE), "valid" if not errs else "INVALID"))
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
