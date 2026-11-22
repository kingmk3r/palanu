# Palanu — a universal language for humans and machines

*Specification v1.0. The lexicon tables, grammar, sample glosses and efficiency
figures marked "generated" are produced from `parser.py`, which also checks them.
Run `python3 parser.py --update-spec` to refresh them.*

```
Pala ka pelo pin suyu.        Speech goes like water.
```

## Palanu at a glance

| | |
|---|---|
| Sounds | 15 phonemes: `p t k s c` · `m n l y w` · `a e i o u`. No tones, clusters, vowel length or voicing contrast. |
| Word boundaries | **One rule:** every `p t k s c` begins a word, and those five sounds never occur anywhere else. You can find every boundary by ear, in writing with no spaces, or with one regular expression. |
| Word shapes | Particle = 1 syllable (48 of them, closed set). Content word = 2-syllable root + 1-syllable suffixes + optional plural `-n`. You can tell a word's class from how long it is. |
| Morphology | Grammar is carried by separate particles that never change (isolating). New words are built by adding suffixes (agglutinative). There are no paradigms, agreement or exceptions. |
| Syntax | Subject – predicate marker – verb – object, with heads before modifiers. Every clause has one obligatory tense/mood particle, and it marks where the subject ends. |
| Machine side | The grammar is a 22-rule PEG. The reference parser runs it directly, with one parse or none. There are 18 annotated samples and 18 negative tests. |
| Vocabulary | 152 roots. The 39 most frequent are chosen so that no two differ by a single sound. 23 suffixes and phrasal compounding extend them, and 395 root slots are still free. |
| Script | Romanization: 15 plain ASCII letters, one letter per sound, no digraphs. The optional native script, *Semanu*, builds each glyph from how the sound is made. |

## Contents

0. Design principles and lessons from earlier languages
1. Name
2. Phonology
3. Morphology and word formation
4. Grammar (with the formal PEG)
5. Vocabulary: Zipf strategy, compounding, loans and names
6. Writing: romanization, the Semanu script, numbers
7. Eloquence: rhythm, registers, poetics
8. Core lexicon and sample sentences
9. Efficiency compared with English
10. Learning path
11. Appendix: machine interface and known limits

---

## 0. Design principles and lessons from earlier languages

Palanu is designed to meet four goals, and each one has a measurable target:

1. **Robust in speech.** Every contrast must survive noise, foreign accents and
   fast speech. Target: every sound is common across languages, and every
   word boundary can be heard in the segments themselves.
2. **Learnable.** Target: no exceptions, no paradigms, and a closed set of
   function words a learner can memorize in a week.
3. **Deterministic.** Target: a formal grammar in which every sentence has
   exactly one parse or none, checked by a program.
4. **Efficient and beautiful.** Target: speaking time comparable to English,
   with open syllables and regular rhythm that work well in verse.

What earlier projects teach:

| Language | What it got right | What went wrong | What Palanu does |
|---|---|---|---|
| **Esperanto** (1887) | Regular agglutinative morphology. The *mal-* prefix halves the adjective vocabulary. Part-of-speech endings. | European phonology (clusters, `ĉ ĝ ĥ ĵ ŝ ŭ`), accusative and adjective agreement, male-default roots (*patro → patrino*). | Keeps productive derivation and the antonym affix (`-no`). Drops agreement and case. Every root is gender-neutral. |
| **Lojban** (1987) | An unambiguous, machine-parseable grammar, and morphology designed for segmentation. | Hard consonant clusters, segmentation that relies on stress and pauses, hundreds of particles, a steep learning curve. | Segmentation comes from the sounds alone and needs no clusters. The particle set has exactly 48 members, laid out as a 5×10 table. |
| **Toki Pona** (2001) | Minimalism and open syllables, learnable in days. | It is deliberately vague. Grouping (`pi`) and predicate marking (`li`, dropped after *mi/sina*) leave real parse ambiguity. It is too coarse for technical use. | Keeps the open-syllable sound and the small core. Every slot is marked, and there is room for exact meaning. |
| **Hangul** (1443) | A featural script: glyph shapes show where and how sounds are made, so it can be learned in hours. | — | The *Semanu* script (§6) uses the same idea, with place shown by shape, manner by strokes, and vowels by position. |
| **Ithkuil** (2004–) | Very high meaning density per syllable. | Practically unspeakable and unlearnable. Coupé et al. (2019) show that humans convey information at a roughly constant rate (≈39 bits/s), so packing more into each syllable mainly slows speakers down. | Palanu does not chase density. It aims for the same rate as natural languages, using simple syllables spoken quickly, and spends its design effort on robustness and determinism. |

Coupé, Oh, Dediu & Pellegrino (2019, *Science Advances*) measured 17
languages. Information per syllable ranges from about 5 bits (e.g. Japanese)
to about 8 bits (e.g. Vietnamese), and speakers trade syllable rate against
density, so the average comes to about 39 bits/s. A designed language
therefore gains little from cramming more into each syllable. Palanu
deliberately sits at the Japanese/Spanish end of that range: low-entropy CV
syllables that can be produced and perceived quickly and reliably.

---

## 1. Name

**Palanu** /ˈpa.la.nu/, stressed on the first syllable.

* `pala` is the root for *word, speech, say*. Its mnemonic hook is Spanish
  *palabra* or Portuguese *falar*.
* `-nu` is the collective suffix: *the whole set or system of*.
* `pala-nu` therefore means *the whole of speech*, i.e. **language**. The
  name is an ordinary word of the language, built by its own regular
  derivation, in the same way that *Esperanto* is an ordinary Esperanto
  participle.

The native script is called **Semanu** (`sema-nu`, *the system of signs*).

---

## 2. Phonology

### 2.1 Inventory

| | labial | coronal | dorsal / palatal |
|---|---|---|---|
| **strong** (obstruents, word-initial only) | `p` | `t`, `s` | `k`, `c` /tʃ/ |
| **soft** (sonorants, word-internal only) | `m`, `w` | `n`, `l` | `y` /j/ |

| | front | back |
|---|---|---|
| high | `i` | `u` |
| mid | `e` | `o` |
| low | `a` | |

**Why these 15?**

* **Vowels.** /a e i o u/ is the most common vowel system in the world's
  languages (Maddieson, *Patterns of Sounds*; WALS ch. 2). Its five vowels
  are spread as far apart as possible in acoustic space (Liljencrants &
  Lindblom 1972), so speakers of 3- to 12-vowel languages all map onto them
  easily.
* **Consonants.** /m k j p w n t s l/ are among the most widespread segments
  in phoneme databases such as UPSID and PHOIBLE. /tʃ/ is common but less
  universal; it is the most distinct affricate and gives the fifth word-onset
  family.
* **What is deliberately left out**, and why:
  * **Voicing contrasts** (`p/b`, `t/d`, `k/g`). They are absent or realised
    differently in Mandarin, Korean, Finnish, Hawaiian, Tamil and most
    Australian languages.
  * **The `r/l` contrast.** It is merged in Japanese, Korean and many
    Chinese varieties.
  * **Rarer or fragile sounds:** /f v θ ð h x ʃ ʒ/.
  * **Consonant clusters, vowel length and tone** (see §2.6).

**Allowed variation.** Palanu tolerates broad allophony, so a speaker with any
accent is still understood. No single realisation is "correct".

| phoneme | acceptable realisations |
|---|---|
| p t k | aspirated or unaspirated, voiced or voiceless: [p pʰ b], [t tʰ d], [k kʰ g] |
| s | [s ɕ ʃ] |
| c | [tʃ tɕ tʂ dʒ] (always an affricate, never a plain fricative) |
| m n | before a word starting with `p`/`k`, `n` may become [m]/[ŋ] |
| l | [l ɾ r ɹ] |
| y w | [j], [w ʋ β] |
| vowels | any position inside the region of the cardinal vowel; never reduced to [ə] |

### 2.2 Positional classes: strong onsets, soft bodies

The ten consonants fall into two **disjoint positional classes**:

* **Strong** `p t k s c` occur **only at the very start of a word**.
* **Soft** `m n l y w` occur **only inside a word**. `n` may also end a word.

This split follows tendencies found across the world's languages:

* **Speakers strengthen word onsets.** Consonants are produced with longer,
  stronger closures at the start of prosodic domains (Fougeron & Keating 1997).
* **Sounds weaken between vowels.** This is the most common sound change
  (Spanish /b d g/ → [β ð ɣ], Korean intervocalic voicing, Celtic lenition,
  Finnish consonant gradation). Palanu fixes that natural tendency as a
  structural rule.
* **The two classes differ in manner, which survives noise best.** Miller &
  Nicely (1955) showed that in noise, listeners lose *place* of articulation
  first, while *manner*, *nasality* and *voicing* survive. The strong/soft
  difference is a manner difference (obstruent vs sonorant), so the cue that
  marks word boundaries is the one most likely to come through.
* **Listeners already treat salient onsets as word starts.** English listeners
  segment speech by assuming that strong syllables begin words (Cutler & Norris
  1988, the Metrical Segmentation Strategy), and lexical access runs from word
  onsets (Marslen-Wilson's Cohort model). In Palanu, every word starts with the
  most salient sound class and carries stress on that syllable.

### 2.3 Syllable and word structure

```
word      = S V ( W V )* ( n )?      S ∈ {p t k s c}   W ∈ {m n l y w}   V ∈ {a e i o u}
```

* Every syllable is **CV**. The only coda is a **word-final `n`**, and it is
  always followed by the next word's strong consonant or by a pause. As a
  result, the **only consonant sequences in the language are `n` + strong
  consonant across a word boundary** (`kan ta`, `ten pelo`), which are easy
  in essentially every language.
* **Three banned syllables.** They protect fragile contrasts:
  * `ci`: so that /ti/, which is palatalised to [tʃi] in Japanese, Korean
    and Brazilian Portuguese, never collides with a real `ci`.
  * `yi`: it would be near-identical to `i`.
  * `wu`: it would be near-identical to `u`.
* **No two vowels are ever adjacent inside a word**, so there are no
  diphthongs, no hiatus and no glide-insertion ambiguity.

### 2.4 Self-segmentation: the one rule

> **Every strong consonant begins a new word.**

**Proof sketch.** Strong consonants never occur inside a word, so each one
must be the first sound of a word. Every word begins with a strong consonant,
so every word boundary sits immediately before one. The boundaries are
therefore exactly the positions of the strong consonants. A machine finds
them with `re.split(r'(?=[ptksc])', s)`. A listener finds them as the crisp
obstruent bursts, which are also where the stress falls.

```
takapiyatu   →   ta | ka | piya | tu      "I love you"
```

**Name frames.** The single exception is a name frame. A word-initial `cun`
opens a proper name, which runs raw to the next `cun` (§5.5); no root may
begin with `cun`. Even this is detected by sound.

**Morphemes segment the same way.** Inside a content word, syllables 1–2 are
the root, each later syllable is one suffix, and a final `n` is the plural.

**Checks in `parser.py`.** For every sample, `parser.py` confirms three
things:

1. The space-free sound stream segments into exactly the same words as the
   spaced text.
2. A brute-force count of *all* ways to cut the stream into valid words finds
   exactly one.
3. A written space never falls inside a word.

### 2.5 Stress and intonation

* **Primary stress falls on the first syllable of every content word.** In
  long words, secondary stress falls on syllables 3, 5, and so on:
  `KO.no.YA.wa`, `PE.na.WE`.
* **Particles are unstressed** but keep full vowel quality. Palanu never
  reduces vowels: English-style reduction to schwa destroys exactly the
  information (vowel identity) that is most robust in noise.
* Stress is fully predictable. It is a **second, independent cue** to word
  onsets (Finnish, Hungarian and Czech use the same initial-stress pattern),
  so segmentation survives even if a consonant is misheard.
* **Intonation is free.** Questions, negation and focus are all carried by
  particles, so pitch is available purely for emotion and emphasis. This
  matters for eloquence (§7).

### 2.6 Why no tones

Tone would add information per syllable, but at four costs:

* it is hard for the majority of learners, whose native languages are not
  tonal;
* it is fragile in whispering, shouting and singing;
* it competes with intonation for the pitch channel;
* tone languages need more contrastive segments elsewhere.

Coupé et al.'s result means the extra density buys no extra information rate.
Palanu therefore leaves pitch to intonation, and to the poets.

### 2.7 Robustness to accents and noise: summary

| threat | protection |
|---|---|
| speaker lacks voicing contrast, or l/r contrast | the language has neither |
| speaker palatalises /ti/ → [tʃi] | `ci` is banned, so [tʃi] can only mean `ti` |
| speaker inserts vowels into clusters | there are no clusters |
| speaker drops final consonants | The only coda is `n`, and dropping it never moves a word boundary. It does change the word: a CVn particle becomes its CV neighbour (`kan` 0 → `ka` PRS, `can` EV.SEEN → `ca` Q), and a plural noun becomes number-neutral. The slot usually disambiguates (a digit string vs the predicate-marker slot), but this is a real weak point. Learners are taught to keep the nasal; nasalising the vowel is enough. See §11.3. |
| noise masks place of articulation | boundaries depend on manner (obstruent vs sonorant), which survives noise best |
| vowel confusion between neighbours (e/i, o/u) | tier-1 roots are kept ≥ 2 phonemes apart (§5.1) |
| fast speech | CV syllables; vowels are never reduced |

### 2.8 Phonotactic facts (generated)

<!-- BEGIN:FACTS -->
| quantity | value |
|---|---|
| phonemes | 15 (5 strong + 5 soft consonants, 5 vowels) |
| legal word-initial syllables (S V) | 24 |
| legal word-internal syllables (W V) | 23 |
| max. phonotactic information per syllable | 4.55 bits |
| particles (all legal monosyllables) | 48 |
| suffixes (all legal soft syllables) | 23 |
| possible C V C V roots | 552 (547 usable; the 5 cun- forms are reserved) |
| roots assigned | 152 (tier 1: 39) |
| roots still free for future coinage | 395 |
| minimal pairs inside tier 1 | 0 |
<!-- END:FACTS -->

Each syllable carries at most about 4.6 bits, close to Japanese. Following
Coupé et al., Palanu is expected to be spoken at a high syllable rate, like
other CV languages. Pellegrino, Coupé & Marsico (2011) measured about 7.8
syllables/s for Japanese and Spanish, against about 6.2 for English. The
information rate should therefore be ordinary (about 39 bits/s), not
superhuman. §9 estimates speaking time for the sample corpus under that
assumed rate.

---

## 3. Morphology and word formation

### 3.1 Typology: isolating grammar, agglutinative words

Palanu is **isolating at the level of grammar** and **agglutinative at the
level of vocabulary**.

**Grammar is isolating.** Tense, mood, evidence, negation, case relations,
clause linking and questions are all expressed by separate one-syllable
particles that never change. There are three reasons:

* **It is learnable.** Pidgins and creoles, created under strong
  learnability pressure, converge on invariant pre-verbal tense and aspect
  particles (Haitian *te*, Tok Pisin *bin* and the predicate marker *i*).
  McWhorter (2001) argues creole grammars are among the simplest attested.
* **It is efficient.** No syllables are spent on agreement or redundant case
  endings.
* **It suits machines.** Every grammatical meaning is a separate token with
  one fixed tag.

**Vocabulary is agglutinative.** Words are built as root + suffix + suffix…,
each piece with exactly one meaning, in the manner of Turkish, Swahili and
Esperanto. A small set of roots then multiplies into a large vocabulary, and
learners memorise roots, not words: `kono` *know* → `kono-ya` *teach* →
`kono-ya-wa` *teacher* → `kono-ya-wi` *school*.

**Fusion is rejected.** There are no fusional endings, no stem changes and no
irregular forms. A morpheme always looks and sounds the same.

**Only suffixes are used.** This is forced by the phonology: a prefix would
start with a strong consonant and so become a separate word. It is also the
cross-linguistically favoured choice. Greenberg's universals and Cutler,
Hawkins & Gilligan (1985) document a strong suffixing preference, explained by
listeners processing the stem first. In Palanu the root is always the first,
stressed, strong-onset part of the word, which is where lexical access happens.

### 3.2 Word classes are visible in the shape

| shape | class | count |
|---|---|---|
| `S V` or `S V n`: **one syllable** | particle (closed class) | 48. Every legal monosyllable is a particle, and every particle is a monosyllable. |
| `S V W V`: **two syllables** | bare root | 152 assigned of 547 possible |
| root + `(W V)*` + `(n)` | derived or inflected content word | open |

Rules:

* A **root is exactly two syllables**. It never ends in `n`.
* A **suffix is exactly one soft syllable** (`W V`). There are 23 legal soft
  syllables, and all 23 are suffixes.
* **Plural** is a final `-n` on a content word used as a noun.

So morpheme boundaries inside a word are **positional**: syllables 1–2 are the
root, each later syllable is a suffix, and a final `n` is the plural.
`konoyawan` = `kono` + `-ya` + `-wa` + `-n` = *teachers*. A parser never needs
to search.

### 3.3 Particles (generated)

The **consonant names the family** and the **vowel picks the member**, so the
48 particles form a table of 5 consonants × (5 vowels, plus 5 vowels + n). The
same featural idea underlies Hangul.

<!-- BEGIN:PARTICLES -->
| form | class | gloss tag | meaning | family |
|---|---|---|---|---|
| **pa** | PREP | to | to, toward, for (goal, recipient, beneficiary) | p- relators |
| **pe** | PREP | from | from, since; than (source, standard of comparison) | p- relators |
| **pi** | PREP | at | at, in, on, during (place or time) | p- relators |
| **po** | PREP | with | with, by, using (instrument, means, companion, manner) | p- relators |
| **pu** | GEN | of | of (attaches a noun phrase to the preceding noun) | p- relators |
| **pan** | PREP | because | because of, due to | p- relators |
| **pen** | PREP | about | about, concerning | p- relators |
| **pin** | PREP | like | like, as (similarity) | p- relators |
| **pon** | PREP | per | according to (source of information) | p- relators |
| **pun** | CTX | CTX | context closer: 'as for / given / then' | p- relators |
| **ta** | PRON | 1SG | I, me | t- persons & pointers |
| **tu** | PRON | 2SG | you (one person) | t- persons & pointers |
| **te** | PRON | 3SG | he, she, they (one person) | t- persons & pointers |
| **to** | DEM | that | it, that (distal; things) | t- persons & pointers |
| **ti** | DEM | this | this (proximal) | t- persons & pointers |
| **tan** | PRON | 1PL | we, us | t- persons & pointers |
| **tun** | PRON | 2PL | you (several) | t- persons & pointers |
| **ten** | PRON | 3PL | they (persons) | t- persons & pointers |
| **ton** | DEM | those | those, they (things) | t- persons & pointers |
| **tin** | DEM | these | these | t- persons & pointers |
| **ka** | TAM | PRS | present / general (is, does) | k- predicate markers / digits 0-4 |
| **ke** | TAM | PST | past (was, did) | k- predicate markers / digits 0-4 |
| **ko** | TAM | FUT | future (will) | k- predicate markers / digits 0-4 |
| **ku** | TAM | IMP | imperative / optative (do!, let..., may...) | k- predicate markers / digits 0-4 |
| **ki** | TAM | HYP | hypothetical (would, could, might) | k- predicate markers / digits 0-4 |
| **sa** | CONJ | and | and | s- clause linkers / digits 5-9 |
| **se** | CONJ | or | or | s- clause linkers / digits 5-9 |
| **su** | CONJ | but | but | s- clause linkers / digits 5-9 |
| **si** | COND | if | if | s- clause linkers / digits 5-9 |
| **so** | SUB | that | that, which (opens a subordinate clause) | s- clause linkers / digits 5-9 |
| **ca** | Q | Q | yes/no-question opener | c- discourse & evidence |
| **cu** | SEP | SEP | statement opener / sentence separator | c- discourse & evidence |
| **ce** | NEG | NEG | not | c- discourse & evidence |
| **co** | WH | what | what, which (question word; relative pronoun in a so-clause) | c- discourse & evidence |
| **can** | EVID | EV.SEEN | evidential: I witnessed / perceived it | c- discourse & evidence |
| **cen** | EVID | EV.INFER | evidential: I infer it | c- discourse & evidence |
| **con** | EVID | EV.TOLD | evidential: I was told / reportedly | c- discourse & evidence |
| **cun** | NAME | NAME | opens and closes a proper name or foreign word | c- discourse & evidence |
| **kan** | DIGIT | 0 | zero | k- predicate markers / digits 0-4 |
| **ken** | DIGIT | 1 | one | k- predicate markers / digits 0-4 |
| **kin** | DIGIT | 2 | two | k- predicate markers / digits 0-4 |
| **kon** | DIGIT | 3 | three | k- predicate markers / digits 0-4 |
| **kun** | DIGIT | 4 | four | k- predicate markers / digits 0-4 |
| **san** | DIGIT | 5 | five | s- clause linkers / digits 5-9 |
| **sen** | DIGIT | 6 | six | s- clause linkers / digits 5-9 |
| **sin** | DIGIT | 7 | seven | s- clause linkers / digits 5-9 |
| **son** | DIGIT | 8 | eight | s- clause linkers / digits 5-9 |
| **sun** | DIGIT | 9 | nine | s- clause linkers / digits 5-9 |
<!-- END:PARTICLES -->

**Digits** use the same consonant-and-vowel logic:

* the `k`-series (`kan ken kin kon kun`) is 0–4;
* the `s`-series (`san sen sin son sun`) is 5–9;
* within each series, the vowel order *a e i o u* counts up.

### 3.4 Suffixes (generated)

Suffix families are also organised by consonant:

| consonant | family |
|---|---|
| `m` | degree |
| `n` | polarity and part |
| `l` | aspect |
| `y` | valency |
| `w` | nominalisers |

<!-- BEGIN:SUFFIXES -->
| suffix | tag | meaning | family | example |
|---|---|---|---|---|
| **-ma** | AUG | very, great-, augmentative | m- degree | tawa-ma *huge* |
| **-me** | ATT | somewhat, -ish, attenuative | m- degree | poni-me *fairly good* |
| **-mi** | DIM | little, dear, diminutive | m- degree | pemo-mi *baby* |
| **-mo** | CMP | more (comparative) | m- degree | tawa-mo *bigger* |
| **-mu** | SUP | most (superlative) | m- degree | pume-mu *first* |
| **-na** | PART | a part / piece / member of | n- polarity & part | kiwa-na *leaf* |
| **-ne** | PRIV | without, -less | n- polarity & part | sono-ne *silent* |
| **-ni** | SIM | like, -like, resembling | n- polarity & part | sela-ni *sky-like = blue* |
| **-no** | OPP | opposite, un-, anti- (polar antonym) | n- polarity & part | poni-no *bad* |
| **-nu** | COLL | the whole set / collective / system of | n- polarity & part | pala-nu *language* |
| **-la** | PROG | ongoing (be ...-ing) | l- aspect | kula-la *eating* |
| **-le** | INCH | begin to, become | l- aspect | solu-le *morning* |
| **-li** | ITER | again, repeatedly, habitually | l- aspect | kome-li *return* |
| **-lo** | PERF | completed, already done | l- aspect | kula-lo *has eaten* |
| **-lu** | CESS | stop, cease, end | l- aspect | temu-lu *wake up* |
| **-ya** | CAUS | make / cause to | y- valency / voice | kono-ya *teach* |
| **-ye** | POT | able to be ...-ed, -able | y- valency / voice | kalo-ye *possible* |
| **-yo** | PASS | undergo, be ...-ed | y- valency / voice | sile-yo *be seen* |
| **-yu** | RECP | each other / oneself | y- valency / voice | pala-yu *converse* |
| **-wa** | AGT | one who does (agent) | w- nominalisers | kono-ya-wa *teacher* |
| **-we** | INS | tool or means for | w- nominalisers | pena-we *computer* |
| **-wi** | LOC | place for | w- nominalisers | kono-ya-wi *school* |
| **-wo** | RES | result, product, what is ...-ed | w- nominalisers | pemi-wo *text, book* |
<!-- END:SUFFIXES -->

### 3.5 Composition rules

1. **Suffixes apply left to right.** Each one takes the whole word so far as
   its input: `kono-ya-wa` = AGT(CAUS(*know*)) = *one who causes to know* =
   *teacher*. Changing the order changes the meaning compositionally:
   `kono-wa-ya` = *make someone a knower*.
2. **Any order is legal**, and the meaning is always the composition. There
   are no lexical gaps or blocking effects to memorise.
3. **Plural `-n` comes last** and only on nominals. The validator rejects
   `pelon` used as a verb.
4. **Roots have no fixed part of speech.** The slot a word occupies decides
   its role:

| slot | role | example with `poni` |
|---|---|---|
| right after the predicate marker | predicate (verb) | `ta ka poni` *I am well* |
| head of a noun phrase | entity | `poni pu tu` *your goodness* |
| after a head | modifier | `somo poni` *a good person* |

### 3.6 Derivation at work

| word | analysis | meaning |
|---|---|---|
| `poni-no` | good-OPP | bad |
| `tawa-no` | big-OPP | small |
| `pena-we` | think-INS | computer |
| `kalo-we` | do-INS | machine |
| `pelo-we` | go-INS | vehicle |
| `sile-we` | see-INS | eye |
| `kimi-we` | hear-INS | ear |
| `pala-we` | speak-INS | mouth |
| `pena-wi` | think-LOC | brain |
| `sana-wi` | health-LOC | hospital |
| `solu-le` | sun-INCH | morning |
| `solu-lu` | sun-CESS | evening |
| `temu-le` | sleep-INCH | fall asleep |
| `temu-lu` | sleep-CESS | wake up |
| `kiwa-na` | tree-PART | leaf |
| `kiwa-nu` | tree-COLL | forest |
| `kiwa-wo` | plant-RES | fruit |
| `somo-nu` | person-COLL | humanity, society |
| `tomu-nu` | house-COLL | town |
| `pemo-mi` | child-DIM | baby |
| `sala-ma` | peace-AUG | hello! (lit. *great peace*) |
| `pawe-ma` | wind-AUG | storm |
| `kowe-no` | fear-OPP | courage |
| `kiwo-ne` | danger-PRIV | safe |
| `sono-ne` | sound-PRIV | silent |
| `kome-yu` | come-RECP | meet |
| `pala-yu` | speak-RECP | converse |
| `tona-yu` | give-RECP | trade |
| `kono-le` | know-INCH | learn |
| `kono-lu` | know-CESS | forget |
| `kome-li` | come-ITER | return |
| `poni-ya` | good-CAUS | repair |
| `tana-ya` | die-CAUS | kill |
| `pilo-ya` | heat-CAUS | cook |
| `sile-ya` | see-CAUS | show |
| `pelo-ya` | go-CAUS | send |
| `pemi-wo` | write-RES | text, book |
| `pala-wo` | say-RES | message |
| `kono-wo` | know-RES | information, data |
| `camo-nu` | way-COLL | program, algorithm |
| `tali-nu` | line-COLL | network |
| `sema-nu` | sign-COLL | script, code |
| `kalo-ye` | do-POT | possible |
| `piya-me` | love-ATT | like, be fond of |
| `pume-mu` | front-SUP | first |
| `pume-no` | front-OPP | after, next |

Colours come from the similative suffix `-ni` (*like*):

| word | analysis | colour |
|---|---|---|
| `sela-ni` | sky-like | blue |
| `kiwa-ni` | plant-like | green |
| `pilo-ni` | fire-like | red |
| `solu-ni` | sun-like | yellow |
| `kolo-ni` | light-like | white |
| `suma-ni` | night-like | black |

---

## 4. Grammar

### 4.1 The clause template

```
[opener] [context… pun] [subject] TAM [EVID] [NEG] [verb [object] [adjunct…] [so-clause]]
  cu/ca    (time, place,               ka   can    ce    (any content word as predicate)
           condition, topic)            ke   cen
                                        ko   con
                                        ku
                                        ki
```

**Word order is SVO with heads before modifiers.** SVO and SOV together
account for the large majority of languages (Dryer, WALS ch. 81). SVO is the
order of English, Mandarin, Spanish, Swahili, Indonesian, French, Portuguese
and Vietnamese, the largest pool of L1 and L2 speakers.

**SVO puts the obligatory predicate marker between the two noun phrases.** The
marker therefore doubles as the boundary between subject and predicate. Tok
Pisin *i* and Toki Pona *li* do the same, but in Palanu the marker is never
optional and it also carries tense and mood. You get the boundary at no extra
cost.

### 4.2 Tense, aspect, mood

**Every clause has exactly one predicate marker:**

| marker | meaning | example | translation |
|---|---|---|---|
| `ka` | present / general (realis, non-past) | `ta ka kula` | I eat / I am eating |
| `ke` | past | `ta ke kula` | I ate |
| `ko` | future | `ta ko kula` | I will eat |
| `ku` | imperative / optative / hortative | `ku kula!` | eat! |
| | | `tan ku kula` | let us eat |
| | | `tu ku sana` | may you be well |
| `ki` | hypothetical: would / could / might, conditional consequent, polite requests | `ca tu ki tona suyu pa ta?` | would you give me water? |

**Aspect is shown by verb suffixes.** They combine freely with any tense:

| suffix | aspect | example | translation |
|---|---|---|---|
| `-la` | ongoing | `ke kula-la` | was eating |
| `-lo` | completed / perfect | `ko kula-lo` | will have eaten |
| `-le` | inchoative | `ka pilo-le` | is getting warm |
| `-li` | iterative / habitual | `ka kome-li` | comes back / keeps coming |
| `-lu` | cessative | `ke temu-lu` | woke up |

### 4.3 Evidentiality and certainty

An **optional** evidential follows the predicate marker. Without one, a
sentence is a plain assertion.

| particle | meaning | example | translation |
|---|---|---|---|
| `can` | I witnessed or perceived it | `te ke can pelo` | she left (I saw it) |
| `cen` | I infer it from evidence | `te ke cen pelo` | she must have left |
| `con` | I was told; reportedly | `te ke con pelo` | she left, they say |

Uncertainty about the event itself is expressed with `ki`: `te ki pelo`
*she might leave / might have left*.

**Precedent.** Grammatical evidentials exist in roughly a quarter of the
world's languages, including Turkish *-miş*, Quechua *-mi/-si/-chá*, Tibetan
and Bulgarian (Aikhenvald 2004).

**Use for humans.** Evidentials give a compact way to be honest about the
source of a claim.

**Use for machines.** They are provenance metadata built into the grammar. A
knowledge system can store *sensor-observed* vs *inferred* vs *reported*
facts directly from the parse.

**Cost.** One syllable, and only when wanted. In sample 8, `con` does the work
of English *is said to* or *reportedly*.

### 4.4 Negation and polarity

**Clause negation** is `ce` after the predicate marker and any evidential:
`ta ka ce kono` *I don't know*. Its scope is the predicate, and the order
`TAM EVID NEG` is fixed, so `ke con ce` means *reportedly didn't*.

**Lexical opposites** use the suffix `-no`: `poni-no` *bad*, `pawa-no`
*closed*. This is the contrary (*small*), not the contradiction (*not big*),
which is `ka ce tawa`.

**Universal negatives** use the numeral zero, so no separate negative
pronouns are needed:

| phrase | literal meaning | translation |
|---|---|---|
| `somo kan` | person zero | nobody |
| `kowa kan` | thing zero | nothing |
| `temo kan` | time zero | never |

### 4.5 Questions

**Yes/no questions** start with the opener `ca`. The pattern matches Esperanto
*ĉu*, Polish *czy* and Yiddish *tsi*. Because the marker comes first, the
listener knows from the first syllable that a question is coming.

**Answers** echo the predicate marker:

| answer | literal meaning | translation |
|---|---|---|
| `ka` | it is so | yes |
| `ka ce` | it is not so | no |
| `ko`, `ke ce`, etc. | (tense-matched echo) | yes / no |

This is the strategy of Finnish, Irish and Mandarin.

**Content questions** keep the question word `co` in place (*wh-in-situ*, as in
Mandarin, Japanese, Hindi and Turkish), so word order never changes. `co`
combines with a generic noun to give every question word without new
vocabulary:

| Palanu | literal meaning | English |
|---|---|---|
| `co` | what | what |
| `somo co` | which person | who |
| `tolo co` | which place | where |
| `temo co` | which time | when |
| `sayo co` | which reason | why |
| `pan co` | because of what | why |
| `camo co` | which way | how |
| `kanu co` | which number | how many |
| `kine co` | which kind | what kind |

### 4.6 Noun phrases

```
npcore = head modifier* (pu npcore)* (so clause)?
```

* **Head first, then modifiers.** Each modifier narrows everything before it:
  `tiwe sela kolo-ni` = *(animal of the sky), white* = *white bird*.
* **Numerals and demonstratives** are ordinary modifiers: `somo kin` *two
  people*, `tomu ti` *this house*.
* **There are no articles.** Bare nouns are definite or indefinite by
  context, as in Mandarin, Russian, Hindi and Japanese. Add `ti`/`to` when
  pointing matters.
* **Number is neutral by default.** Add `-n` for an explicit plural
  (`tiwe-n` *animals*), or use a numeral or a quantifier (`pulu` *many*,
  `sewa` *all*).
* **The genitive uses `pu`:** `tomu pu te` *her house*,
  `somo-n pu tela` *the people of Earth*. A `pu` phrase always attaches to the
  noun immediately before it, and nested `pu` phrases branch to the right.
* **Relative clauses** are `so` + a clause containing exactly one `co`, which
  marks the gap. `somo so co ke kalo ti` = *person that [who made this]*;
  `kowa so ta ke sile co` = *thing that [I saw which]*.
  * The explicit gap pronoun works like the resumptive strategy of Arabic,
    Hebrew and Persian. It makes every position relativisable (subject,
    object, oblique, possessor) without the processing cost of an invisible
    gap (cf. the Keenan–Comrie accessibility hierarchy).
  * The validator enforces exactly one `co`.

### 4.7 Pronouns

| | singular | plural |
|---|---|---|
| 1st person | `ta` I | `tan` we |
| 2nd person | `tu` you | `tun` you all |
| 3rd person, human | `te` he / she / they | `ten` they |
| 3rd person, thing (far) | `to` it, that | `ton` those |
| near | `ti` this | `tin` these |

* Pronouns are **gender-neutral**. Sex can be stated when relevant
  (`somo kene` *a woman*).
* There are no case forms: `ta` is *I*, *me* and, with `pu`, *my*.
* The reflexive uses the root `cewe` *self*.
* Personal pronouns (`ta tu te tan tun ten`) can head a noun phrase and take
  modifiers (`tan sewa` *all of us*). They never act as modifiers.
  Possession always uses `pu`.

### 4.8 Linking clauses

| construction | form | example | translation |
|---|---|---|---|
| coordination | clause `sa` / `se` / `su` clause | `ta ke pelo sa te ke kome` | I left and she came |
| complement clause | verb `so` clause | `ta ka kono so tu ka pala tuli` | I know that you speak truly |
| adverbial clause | preposition + `so` clause | `pi so` *when*, `pan so` *because*, `pa so` *so that*, `pin so` *as if* | |
| condition | `si` clause `pun` main clause | `si tu ko kome pun tan ko kula` | if you come, we will eat |

**Coordination of clauses vs noun phrases.** After `sa`, `se` or `su`, the
parser checks what follows:

* if a predicate marker follows the next noun phrase, `sa` joins **clauses**;
* otherwise it joins **noun phrases**.

| example | what `sa` joins | translation |
|---|---|---|
| `ta ke sile kowa sa tolo` | noun phrases | I saw the thing and the place |
| `ta ke sile kowa sa tu ko pelo` | clauses | I saw the thing, and you will go |

**The `pun` context frame.** Anything placed before the subject is a *context*
and is closed by `pun` (*as for… / given… / then*). Contexts can be:

| context type | example | translation |
|---|---|---|
| time or place | `pi solu ti pun …` | today, … |
| condition | `si … pun …` | if …, then … |
| topic | `ta pun …` | as for me, … |
| vocative | `cun Malia cun pun ku kome` | Maria, come! |

Toki Pona *la* plays a similar role. Fronting is what lets poets and speakers
reorder for emphasis without making the parse ambiguous.

### 4.9 Sentences and discourse

**Openers.** A text is a sequence of sentences. Every sentence after the first
begins with an opener:

* `cu` for a statement;
* `ca` for a yes/no question.

The first sentence may omit `cu`. The opener is the spoken full stop: it makes
sentence boundaries audible and deterministic, and it costs one syllable per
sentence.

**Fragments and short answers.** A bare noun phrase is a complete utterance
(`salama!` *hello!*). A bare predicate marker is a complete predicate, which
makes it the short answer (`ka` *yes*, `ka ce` *no*).

### 4.10 Zero irregularity: guarantees

1. Every morpheme has exactly one form and one meaning tag.
2. Every rule applies to every word in its class. There are no exceptions,
   no suppletion, no defective paradigms.
3. Spelling = pronunciation = morphological analysis.
4. Word class can be read off word length. Morpheme boundaries can be read
   off syllable position. Word boundaries can be read off consonant class.
5. Every sentence has one parse or none.

### 4.11 Formal grammar (generated, and executed by the reference parser)

**Notation.**

* Lower-case names are rules.
* UPPER-case names are token classes from the lexicon: `TAM`, `EVID`, `NEG`,
  `PRON`, `DEM`, `WH`, `PREP`, `GEN`, `SUB`, `CONJ`, `COND`, `CTX`, `SEP`,
  `Q`, `DIGIT`, `NAME`, and `CONTENT` (any content word).
* `'x'` is a literal word.
* The operators are standard PEG: ordered choice `/`, greedy `* + ?`, and
  lookaheads `& !`.

<!-- BEGIN:GRAMMAR -->
```peg
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
```
<!-- END:GRAMMAR -->

**Why the parse is deterministic.** A PEG cannot be ambiguous: ordered choice
commits to the first alternative that succeeds, and repetition is greedy. The
grammar has no left recursion, so the packrat interpreter in `parser.py` runs
in time linear in the number of words. The linguistically important decisions
are written into the grammar as explicit rules:

| question | rule |
|---|---|
| prepositional phrase after the verb phrase | attaches to the clause (`po` = instrument/manner); `pu` is the only noun-attaching relator |
| clause vs NP coordination | decided by whether a predicate marker follows (`!TAM` lookahead) |
| how far a subordinate clause extends | as far as it can (greedy); to end it earlier, front material with `pun` or start a new sentence with `cu` |
| how modifiers group | strictly left-to-right; for any other grouping use `pu` |

**Constraints checked after the PEG**, because they are not context-free:

* a verb may not carry plural `-n`;
* a relative clause contains exactly one `co`.

---

## 5. Vocabulary

### 5.1 Zipf-optimised length tiers

Zipf's law of abbreviation says that more frequent words are shorter. Palanu
builds this into its structure through three length tiers:

| length | what goes there | why |
|---|---|---|
| **1 syllable** (48 particles) | function meanings: tense, persons, relators, linking, negation, question, evidence, digits | In every corpus of every language, function words are the most frequent tokens. |
| **2 syllables** (152 roots) | core concepts, ranked in 3 frequency tiers | Tier 1 (39 roots) covers the highest-frequency content meanings: *be, do, say, go, come, see, know, think, want, have, give, take, live, eat, love, person, thing, place, time, good, big, many, all, …* |
| **3+ syllables** | derived and compound words | less frequent meanings, built transparently from tiers 1–2 |

**Corpus check.** `parser.py` counts word types in the 18 samples. The 15
most frequent types (led by `ka`, `ke`, `tu`, `pa`) average 1.47 syllables;
all other types average 1.75.

**Robustness check.** The most frequent words are the ones most often heard in
bad conditions. The validator therefore enforces that **no two tier-1 roots
form a minimal pair**: any two differ in at least two of their four phonemes.
The result is 0 minimal pairs among the 39 tier-1 roots. Lower tiers may have
neighbours, and context disambiguates them.

### 5.2 Where the roots come from

Roots are *a posteriori* wherever the CVCV mould allows. Each root has a
**mnemonic hook** drawn from a broad sample of major languages, not only
European ones:

* Latin / Romance: `tene` *have* < *tenere*; `camo` *way* < *camino*
* Greek: `tolo` *place* < *topos*; `tana` *die* < *thanatos*
* Sanskrit / Hindi: `sewa` *all* < *sarva*; `cana` *want* < *chāhnā*;
  `caye` *must* < *chāhiye*
* Mandarin: `sinu` *new* < *xīn*
* Japanese: `kumo` *cloud*
* Arabic: `kaya` *life* < *ḥayāh*; `sala` *peace* < *salām*
* Swahili: `kula` *eat*
* Turkish: `suyu` *water* < *su/suyu*
* Malay: `tali` *rope*

Where no good hook fits the mould, the root is arbitrary but still chosen for
distinctness. All 152 roots are listed in §8.

### 5.3 Compounding

Compounds are **phrasal and head-first**. A compound is simply a noun phrase
whose meaning has become conventional:

| compound | literal meaning | gloss |
|---|---|---|
| `tolo kiwa` | place of plants | garden |
| `tiwe sela` | animal of the sky | bird |
| `tiwe suyu` | water animal | fish |
| `tiwe tomu` | house animal | pet, dog |
| `camo suyu` | way of water | river |
| `suyu pewo` | stone water | ice |
| `kana tanu` | song of the body | dance |
| `kana pala` | song words | poem |
| `palawe tayo` | far mouth | telephone |
| `kalowe somoni` | person-like machine | robot |

Rules:

1. The head comes first, and modifiers restrict it left to right.
2. If a modifier is itself complex, use `pu`: `tomu pu kume tawa`
   = *house of [the great leader]*.
3. In writing, a lexicalised compound may be joined with a hyphen
   (`tolo-kiwa`). The parser ignores hyphens, and since every word starts with
   a strong consonant, even `tolokiwa` re-segments correctly.

Compounds need no new parsing machinery, and they can never be mis-segmented.

### 5.4 Technical terms

When a new concept needs a word, use the first option that works:

1. **Calque from roots and suffixes.** This is preferred, as Icelandic and
   Chinese do: `pena-we` *computer*, `camo-nu` *algorithm*, `kono-wo`
   *data*, `kaya-na` *cell* (life-part), `tali-nu` *network*, `sema-nu`
   *code*, `pele-wo` *fraction*.
2. **International symbols and names** go inside a `cun` frame (§5.5):
   `cun tiyenaye cun` *DNA*.
3. **A new root.** 395 well-formed CVCV slots are still unassigned. A new root
   must pass the same automatic checks as existing ones: valid shape, unique
   form, and, if it is proposed for tier 1, at least two phonemes away from
   every other tier-1 root. The registry is the `ROOTS_SRC` table in
   `parser.py`.

### 5.5 Proper names and foreign words: the `cun` frame

A name is spoken and written between two `cun` particles:
`cun Malia cun` *Maria*, `cun Tokiyo cun` *Tokyo*, `cun Ata cun` *Ada*.

* **Inside the frame**, phonotactics are relaxed. Any sequence of the 15
  letters is allowed except `cun` itself, including clusters and codas, so
  names stay recognisable.
* **Sound mapping.** Foreign sounds map to the nearest Palanu sound:

| foreign sound(s) | Palanu |
|---|---|
| b, d, g | p, t, k |
| f, v | p, w |
| r | l |
| z | s |
| sh, ch, j | c |
| h | dropped |
| x | ks |
| th | t |
| any vowel | nearest of a e i o u |

* **Why two delimiters.** The frame is audible: the listener hears the
  syllable `cun` open and close the name, like spoken quotation marks. A
  machine can find the frame boundaries without a lexicon.
* **In the native script**, the frame is drawn as a cartouche (§6.2).

A name can head a noun phrase directly (`cun Ata cun ke pemi …`), or be
attached to a common noun (`tomunu cun Lakos cun` *the city Lagos*).

---

## 6. Writing

### 6.1 Romanization (canonical, machine form)

The romanization uses **15 lower-case ASCII letters**, a strict one-to-one
mapping between letters and phonemes:

```
p t k s c   m n l y w   a e i o u
```

* **No digraphs and no diacritics.** `c` is always /tʃ/ (as in Indonesian
  and Malay spelling and in Sanskrit transliteration), and `y` is always /j/.
* **Spaces are conventional but optional.** Text self-segments, so
  `takapiyatu` is valid.
* **Hyphens are optional teaching aids** inside words (`kono-ya-wa`).
* **Capitals and punctuation are decorative.** Every grammatical signal
  (question, statement boundary, clause frame, quotation of names) is a spoken
  particle, so stripping all punctuation loses nothing. The reference parser
  removes it.
* **Collation order** is `a e i o u p t k s c m n l y w`, which matches the
  particle tables.

### 6.2 Semanu, the featural native script

Like Hangul, Semanu builds each glyph from articulatory features, and each
**syllable is one square block**.

**1. Consonant shape = place of articulation.** The shape is a picture of the
active articulator:

| place | shape | consonants |
|---|---|---|
| labial | circle or arc (lips) | `p m w` |
| coronal | upright stroke (tongue tip) | `t s n l` |
| dorsal / palatal | hook (back of the tongue) | `k c y` |

**2. Extra strokes = manner of articulation:**

| manner | mark | consonants |
|---|---|---|
| stop | plain shape | `p t k` |
| fricative | wavy stroke through the shape (hiss) | `s` |
| affricate | stop shape plus wave | `c` |
| nasal | dot inside the shape (resonance) | `m n` |
| liquid | curl at the foot | `l` |
| glide | shape drawn open or dashed | `w y` |

**3. The gate bar.** The five strong consonants carry a heavy horizontal bar
across the top of the block. Every word therefore visibly begins with a barred
block, and word division shows on the page even with no spaces, just as it
shows in sound.

**4. Vowel = a mark at the vowel's place in the mouth.** The block is a
miniature vowel chart. Learners "write where the tongue is", the same
principle as the IPA vowel chart:

```
    i ·       · u        high
    e ·       · o        mid
         · a             low
   front     back
```

**5. Coda `n`** is a small tail at the lower right of the block.

Sketches of four blocks (ASCII approximation):

```
 pa            ka            ta            mi
 ══════        ══════        ══════
  ╭─╮           │╭─          │              ·  ╭─╮
  ╰─╯           ╰╯           │                 │·│
    ·             ·            ·               ╰─╯
 lips+gate     hook+gate     tip+gate      lips+nasal dot, vowel high-front
 vowel low     vowel low     vowel low     (no gate: soft, word-internal)
```

**Further properties:**

* **Direction.** Left to right in lines. Vertical columns are also allowed,
  since blocks are square.
* **Names.** A `cun` frame is drawn as a **cartouche**, an oval around the
  name blocks. This echoes Egyptian royal names and shows the relaxed
  phonotactics inside.
* **Learnability.** A learner who knows the 3 places, 6 manner marks, the
  gate bar, the 5 vowel positions and the `n` tail can read every glyph. That
  is about 15 ideas, comparable to Hangul's 24 jamo.
* **Encoding.** The romanization is the canonical interchange form. Semanu is
  a rendering layer (font ligatures from the ASCII stream, or a Private Use
  Area block), so machines never depend on it.

### 6.3 Number system

**Base 10, positional.** Base 10 keeps compatibility with the world's
numerals, keyboards and software; base 12's divisibility advantages do not
justify a universal break. The digits are one syllable each and built
featurally:

| digit | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |
|---|---|---|---|---|---|---|---|---|---|---|
| word | kan | ken | kin | kon | kun | san | sen | sin | son | sun |

**Reading numbers.**

| kind | Palanu | value | notes |
|---|---|---|---|
| integer | `ken kin kon` | 123 | digits are read in order |
| decimal fraction | `kin telu san` | 2.5 | `telu` = *point* |
| scientific notation | `son telu kin pole sun` | 8.2 × 10⁹ | `pole` = *power* |
| negative | `kanuno kin` | −2 | *number-opposite* + numeral |
| ordinal | `tule kin` | second | *rank two* |
| fraction | `ken pele kin` | ½ | *one divided-by two* |

* **Integers** have no "hundred/thousand" words to learn. 12,345 is
  `ken kin kon kun san`: 5 syllables against 10 for *twelve thousand three
  hundred and forty-five* (sample 12).
* **Scientific notation** maps directly to floating point, so it is
  machine-exact.
* **Arithmetic** uses ordinary roots: `sumu` *plus*, `sumuno` *minus*,
  `tamo` *times*, `pele` *divided by*, `sama` *equals*.
  `kin sumu kin ka sama kun` = *2 + 2 = 4*.

**Why monosyllabic digits.** Short-term memory holds about as much as can be
rehearsed in roughly two seconds (Baddeley's phonological loop). Digit span
therefore depends on how long digit names take to say: Ellis & Hennelly
(1980) found that Welsh speakers' smaller digit spans came from longer digit
names, and Chinese speakers' short digit names support larger spans.

**Robustness of digits:**

* Within a series, digits differ by vowel, which is the most noise-robust cue.
* Across series, they differ in manner (stop `k` vs fricative `s`), not just
  place.
* The `-n` coda marks a digit and keeps digits apart from the CV function
  particles.

---

## 7. Eloquence

### 7.1 Sound texture

Every word opens on a crisp obstruent and flows on through sonorants and open
vowels: `PA-la-nu`, `KO-no-ya-wa`, `SO-lu-le`. The texture resembles languages
often called musical, such as Italian, Japanese and Hawaiian:

* every syllable ends in a vowel, except an occasional soft `-n`;
* about half of all consonants are sonorants;
* there are no clusters.

Because no vowel is ever reduced, sung Palanu keeps its words intact.

### 7.2 Rhythm and metre

Two facts give Palanu a built-in metre:

* content words are stressed on the first syllable, with secondary stress on
  odd syllables;
* particles are unstressed.

Unstressed particles act as pickup syllables (anacrusis) before each stressed
word. The result is a dactylic–trochaic lilt:

```
 PA la ka | PE lo pin | SU yu          / x x | / x x | / x
 sa SU yu ka | PE lo pa | TO lo | SE wa   x / x x | / x x | / x | / x
```

Trochaic tetrameter, the metre of the Finnish *Kalevala*, a direct product of
Finnish initial stress, comes naturally: four content words per line
(`TO-lo SE-wa KA-ya SU-yu`).

### 7.3 Poetic devices

| device | how it works | example |
|---|---|---|
| **Rhyme** | Suffix families give rhyme without effort: aspect `-la/-lo/-le`, nominalisers `-wa/-wo/-wi`, degree `-ma/-mi`. Plural `-n` gives consonant rhyme. | `kula-la / pala-la` (*eating / speaking*); `solu-le … temu-le` (*morning … falling asleep*) |
| **Alliteration** | Every word begins with one of five consonants. Germanic alliterative verse depends on word-initial stressed consonants, and Palanu has both. | `kono, kome, kaya` |
| **Parallelism** | A fixed clause template makes parallel lines easy. | the sample poem's repeated `ka kaya po …` |
| **Fronting** | The `pun` frame moves time, place, condition or a vocative to the front for emphasis without ambiguity. | `pi suma pun …` *in the night, …* |
| **Epistrophe** | Repeating the same final word across lines. | lines 1 and 3 of the poem both end in `suyu` |
| **Intensifier and endearment suffixes** | `-ma` intensifies (`salama`, `piyama` *great love*); `-mi` endears (`sawimi` *dear little friend*). | |
| **Free intonation** | Particles carry questions and negation, so pitch is free for feeling. | |

### 7.4 Registers

Palanu has four registers. All of them use the same grammar; they differ only
in what is made explicit:

| register | use | features |
|---|---|---|
| **Exact** (machine-facing, legal, scientific) | protocols, contracts, data | explicit evidentials on every claim; full numerals with `telu` / `pole`; no omitted subjects; `pon` (*according to*) cites sources; `cu` before every sentence |
| **Plain** (everyday) | conversation | shared subjects omitted after `sa` (`ta ke kome sa ke kula`); fragments as answers (`ka`, `ka ce`, `somo co?`) |
| **Courteous** | requests, ceremony | `ki` for requests (`ca tu ki pano ta?` *would you help me?*); the optative `ku` for wishes (`tu ku sana` *may you be well*); `tane` *thanks*; `salama` greetings; `-mi` for affection |
| **Poetic** | song, verse | `pun`-fronting, ellipsis, parallel clauses, suffix rhyme, elaborate compound images such as `tiwe sela kolo-ni` *a white bird* |

### 7.5 The poem

*Suyu (Water).* The full interlinear gloss is sample 18 in §8.

```
Pala ka pelo pin suyu,               Speech goes like water,
sa suyu ka pelo pa tolo sewa;        and water goes to every place;
cu tolo sewa ka kaya po suyu,        every place lives by water,
sa somo sewa ka kaya po pala.        and every person lives by speech.
Cu pala sewa ka sama ken.            All speech is one.
```

* **Structure.** The poem is a chiasmus (*speech → water → place → water →
  person → speech*) that resolves on the numeral `ken`, *one*.
* **Stress.** Every line opens on a stressed content word or on a light
  particle leading into one.
* **Sound.** Lines 1 and 3 end on `suyu` (epistrophe), and lines 2 and 4 end
  on the same open vowel `-a` (`sewa`, `pala`), an assonant rhyme on the
  unstressed final syllable.
* **Machine check.** The whole poem is a single text that the PEG parses with
  four `cu`/`sa` sentence links.

---

## 8. Core lexicon and sample sentences

### 8.1 Root lexicon (generated, 152 roots)

**Tiers:**

* **1** = core high-frequency set (no minimal pairs inside it)
* **2** = common
* **3** = specialised

**Hooks** are mnemonic look-alikes, not claims of etymological descent.

<!-- BEGIN:ROOTS -->
| # | root | tier | meaning | mnemonic hook |
|---|---|---|---|---|
| 1 | **camo** | 1 | way, path, road, method | Sp camino |
| 2 | **cana** | 1 | want, wish | Hindi chahna |
| 3 | **caye** | 1 | need, must, should | Hindi chahiye |
| 4 | **cenu** | 1 | name; call | Swahili jina |
| 5 | **kalo** | 1 | do, make, work | Hindi karo 'do!' |
| 6 | **kamu** | 1 | other, different | - |
| 7 | **kawe** | 1 | use, employ | - |
| 8 | **kaya** | 1 | live; life; alive | Arabic hayah |
| 9 | **kiyo** | 1 | ask; question | - |
| 10 | **kome** | 1 | come, arrive | Eng come |
| 11 | **kono** | 1 | know, understand | Eng know, Gk gno- |
| 12 | **kowa** | 1 | thing, object, something | - |
| 13 | **kula** | 1 | eat; food | Swahili kula |
| 14 | **pala** | 1 | say, speak; word | Sp palabra |
| 15 | **pano** | 1 | help, support | Mandarin bang |
| 16 | **pelo** | 1 | go, move, travel | Indonesian pergi |
| 17 | **pena** | 1 | think, consider | Fr penser |
| 18 | **piya** | 1 | love; dear | Hindi piya |
| 19 | **pole** | 1 | can, able; power | Sp poder |
| 20 | **poni** | 1 | good, well | Lat bonus |
| 21 | **pulu** | 1 | many, much | Lat plus |
| 22 | **sama** | 1 | be, same, equal | Skt sama, Eng same |
| 23 | **seni** | 1 | feel; feeling | Lat sentire |
| 24 | **sewa** | 1 | all, every, whole | Skt sarva |
| 25 | **sile** | 1 | see, look | Eng see |
| 26 | **sinu** | 1 | new, fresh | Mandarin xin, Jp shin |
| 27 | **solu** | 1 | sun; day | Lat sol |
| 28 | **somo** | 1 | person, human, someone | Lat homo |
| 29 | **suyu** | 1 | water, liquid | Turkish su, suyu |
| 30 | **tanu** | 1 | body | Skt tanu |
| 31 | **tawa** | 1 | big, large, great | Mandarin da |
| 32 | **tela** | 1 | earth, land, world | Lat terra |
| 33 | **temo** | 1 | time, moment | Lat tempus |
| 34 | **tene** | 1 | have, hold, keep | Lat tenere |
| 35 | **tolo** | 1 | place, space | Gk topos |
| 36 | **tomu** | 1 | house, home, building | Gk domos |
| 37 | **tona** | 1 | give | Lat donare |
| 38 | **tuli** | 1 | true, real, correct | Eng true |
| 39 | **tuma** | 1 | take, get, receive | Sp tomar |
| 40 | **cewe** | 2 | self, own | - |
| 41 | **coyo** | 2 | joy, happy, glad | Eng joy |
| 42 | **kana** | 2 | song, music; sing | Hindi gana |
| 43 | **kanu** | 2 | number, count, amount | - |
| 44 | **kele** | 2 | choose, decide | Gk eklego |
| 45 | **kemo** | 2 | head | - |
| 46 | **kene** | 2 | woman, female | Gk gyne |
| 47 | **kenu** | 2 | find, discover | - |
| 48 | **kimi** | 2 | hear, listen | Jp kiku |
| 49 | **kine** | 2 | kind, type, class | Gk genos |
| 50 | **kiwa** | 2 | tree, plant, wood | - |
| 51 | **kiwe** | 2 | hope | - |
| 52 | **kole** | 2 | heart, center, inside | Lat cor |
| 53 | **kolo** | 2 | light, bright, clear | - |
| 54 | **kowe** | 2 | fear, afraid | - |
| 55 | **kulu** | 2 | circle, cycle; year | Gk kyklos |
| 56 | **kuwi** | 2 | fast, quick | - |
| 57 | **kuyu** | 2 | group, together | - |
| 58 | **pamu** | 2 | family, household | Lat familia |
| 59 | **pane** | 2 | parent | Lat parens |
| 60 | **pawa** | 2 | open | - |
| 61 | **pawe** | 2 | air, wind, breath | - |
| 62 | **pele** | 2 | cut, divide, split | - |
| 63 | **pemi** | 2 | write, draw, mark | - |
| 64 | **pemo** | 2 | child, young | - |
| 65 | **pewe** | 2 | foot, leg | Lat pes |
| 66 | **pewo** | 2 | stone, rock, hard | Gk petra |
| 67 | **peya** | 2 | money, price, value | Swahili pesa |
| 68 | **pilo** | 2 | fire, heat, warm | Gk pyr |
| 69 | **pinu** | 2 | drink | Hindi pina |
| 70 | **piwo** | 2 | happen, occur; event | - |
| 71 | **pume** | 2 | front, before | - |
| 72 | **puwe** | 2 | pain, hurt | - |
| 73 | **sala** | 2 | peace, calm, rest | Arabic salam |
| 74 | **sana** | 2 | health, healthy, heal | Lat sanus |
| 75 | **sawi** | 2 | friend | Arabic sahib |
| 76 | **sayo** | 2 | reason, cause | - |
| 77 | **sela** | 2 | sky, above, heaven | Lat caelum |
| 78 | **sema** | 2 | sign, meaning, symbol | Gk sema |
| 79 | **sola** | 2 | one, alone, only | Sp solo |
| 80 | **sono** | 2 | sound, voice | Lat sonus |
| 81 | **sowa** | 2 | sea, ocean | - |
| 82 | **sowe** | 2 | mind, spirit, soul | Eng soul |
| 83 | **sowi** | 2 | free, unbound | - |
| 84 | **sulo** | 2 | beautiful | Hindi sundar |
| 85 | **suma** | 2 | night, evening | - |
| 86 | **suwe** | 2 | easy, simple | - |
| 87 | **tali** | 2 | line, rope; connect | Malay tali |
| 88 | **tana** | 2 | die; death | Gk thanatos |
| 89 | **tane** | 2 | thanks, gratitude | Ger danke |
| 90 | **tano** | 2 | man, male | Gk andr- |
| 91 | **tayo** | 2 | long, far | - |
| 92 | **temi** | 2 | read | - |
| 93 | **temu** | 2 | sleep | Jp nemu |
| 94 | **tewi** | 2 | hand, arm; touch | - |
| 95 | **tewo** | 2 | stay, remain, wait | - |
| 96 | **tiwe** | 2 | animal | - |
| 97 | **tole** | 2 | try, attempt | - |
| 98 | **tomo** | 2 | law, rule, norm | Gk nomos |
| 99 | **towe** | 2 | trust, believe | - |
| 100 | **toye** | 2 | exist, be present, there is | - |
| 101 | **tuwa** | 2 | fight, conflict | - |
| 102 | **tuye** | 2 | also, too, as well | - |
| 103 | **cawa** | 3 | tea | Mandarin cha |
| 104 | **cawe** | 3 | example, instance | - |
| 105 | **cele** | 3 | color, hue | - |
| 106 | **coli** | 3 | state, condition, status | - |
| 107 | **comi** | 3 | picture, image | - |
| 108 | **comu** | 3 | meat, flesh | - |
| 109 | **cowi** | 3 | wonder, marvel | - |
| 110 | **cule** | 3 | fly; wing | - |
| 111 | **cuma** | 3 | succeed, achieve, win | - |
| 112 | **kalu** | 3 | mountain | - |
| 113 | **kami** | 3 | sacred, divine, god | Jp kami |
| 114 | **kawi** | 3 | clean, pure | - |
| 115 | **kemi** | 3 | skin, surface | - |
| 116 | **kewa** | 3 | wall, barrier | - |
| 117 | **kiwo** | 3 | danger, risk | - |
| 118 | **kiye** | 3 | laugh, smile | - |
| 119 | **kiyu** | 3 | anger, angry | - |
| 120 | **kume** | 3 | leader, chief | - |
| 121 | **kumo** | 3 | cloud | Jp kumo |
| 122 | **kuna** | 3 | moon | Lat luna |
| 123 | **kuye** | 3 | cry, weep; tears | - |
| 124 | **pama** | 3 | bridge, link across | - |
| 125 | **pelu** | 3 | metal | - |
| 126 | **pemu** | 3 | sweet, pleasant | - |
| 127 | **pilu** | 3 | rain | - |
| 128 | **pine** | 3 | end, limit, goal | Lat finis |
| 129 | **pome** | 3 | form, shape | Lat forma |
| 130 | **pomi** | 3 | bone, frame | - |
| 131 | **pomo** | 3 | story, tale | - |
| 132 | **poyo** | 3 | box, container | - |
| 133 | **puma** | 3 | heavy; weight | - |
| 134 | **puna** | 3 | carry, bear | - |
| 135 | **pune** | 3 | door, gate, entrance | - |
| 136 | **puye** | 3 | problem, trouble | - |
| 137 | **puyo** | 3 | play, game | - |
| 138 | **sali** | 3 | salt | Lat sal |
| 139 | **seme** | 3 | seed, origin, source | It seme |
| 140 | **seyo** | 3 | star | - |
| 141 | **suli** | 3 | step, stage, phase | - |
| 142 | **sumi** | 3 | skill, art, craft | - |
| 143 | **sumu** | 3 | add, plus, sum | Lat summa |
| 144 | **tama** | 3 | side, edge | - |
| 145 | **tamo** | 3 | multiply, times | - |
| 146 | **tamu** | 3 | set, collection, list | - |
| 147 | **telu** | 3 | point, dot (decimal point) | - |
| 148 | **tiye** | 3 | follow, accompany | - |
| 149 | **tiyu** | 3 | grain, rice, bread | - |
| 150 | **tule** | 3 | order, rank, level | - |
| 151 | **tume** | 3 | dream | Jp yume |
| 152 | **tuwi** | 3 | clothes, cover | - |
<!-- END:ROOTS -->

### 8.2 Sample sentences with interlinear gloss (generated)

**How to read each sample:**

* **Line 1** is the sentence as written.
* **Line 2** splits it into morphemes.
* **Line 3** is the gloss.

`parser.py` verifies five things for every sample:

* it parses under the PEG;
* the space-free stream segments the same way;
* segmentation is unique by brute force;
* each gloss item matches the lexicon;
* the number of gloss items equals the number of words.

**Gloss abbreviations:**

| type | abbreviations |
|---|---|
| tense / mood | PRS, PST, FUT, IMP, HYP |
| evidentials | EV.SEEN / EV.INFER / EV.TOLD |
| sentence and clause particles | NEG, Q, SEP (statement opener), CTX (context closer `pun`), REL (`co` as relative pronoun) |
| suffixes | the tags in §3.4 |
| plural | PL |

<!-- BEGIN:SAMPLES -->
**1. Plain transitive clause**

```
Ta ka piya tu.
ta   ka   piya  tu
1SG  PRS  love  2SG
```
> I love you.

**2. Past + witnessed evidential + recipient**

```
Te ke can tona kula pa somo pulu.
te   ke   can      tona  kula  pa  somo    pulu
3SG  PST  EV.SEEN  give  food  to  person  many
```
> I saw her give food to many people.

**3. Yes/no question**

```
Ca tu ka pala palanu?
ca  tu   ka   pala   pala-nu
Q   2SG  PRS  speak  word-COLL
```
> Do you speak Palanu?

**4. Content question (in situ) + phrasal compound**

```
Tu ke sile co pi tolo kiwa?
tu   ke   sile  co    pi  tolo   kiwa
2SG  PST  see   what  at  place  plant
```
> What did you see in the garden?

**5. Negation + cause + clause coordination + time**

```
Tan ko ce pelo pan pilu, su tan ko pelo pi solu pumeno.
tan  ko   ce   pelo  pan      pilu  su   tan  ko   pelo  pi  solu  pume-no
1PL  FUT  NEG  go    because  rain  but  1PL  FUT  go    at  day   front-OPP
```
> We won't go because of the rain, but we'll go tomorrow.

**6. Relative clause (gap = co) + copula + derivation**

```
Somo so co ke kalo ti ka sama konoyawa poni.
somo    so    co   ke   kalo  ti    ka   sama  kono-ya-wa     poni
person  that  REL  PST  make  this  PRS  be    know-CAUS-AGT  good
```
> The person who made this is a good teacher.

**7. Counterfactual conditional + perfective**

```
Si tu ke kome pun tan ki kulalo po tu.
si  tu   ke   kome  pun  tan  ki   kula-lo   po    tu
if  2SG  PST  come  CTX  1PL  HYP  eat-PERF  with  2SG
```
> If you'd come, we'd have eaten with you.

**8. Reported evidential + inchoative**

```
Tela ka con pilole.
tela   ka   con      pilo-le
earth  PRS  EV.TOLD  warm-INCH
```
> The Earth is said to be warming.

**9. Inferred evidential + genitive**

```
Te ke cen pelo pe tomu pu te.
te   ke   cen       pelo  pe    tomu   pu  te
3SG  PST  EV.INFER  go    from  house  of  3SG
```
> She must've left her house.

**10. Complement clause**

```
Ta ka kono so tu ka pala tuli.
ta   ka   kono  so    tu   ka   pala  tuli
1SG  PRS  know  that  2SG  PRS  say   true
```
> I know you're telling the truth.

**11. Fronted context + numeral + place noun**

```
Pi solu ti pun somo ken kin kon ke kome pa konoyawi.
pi  solu  ti    pun  somo    ken  kin  kon  ke   kome  pa  kono-ya-wi
at  day   this  CTX  person  1    2    3    PST  come  to  know-CAUS-LOC
```
> Today, one hundred and twenty-three people came to the school.

**12. Digit-string number**

```
Peya ka sama ken kin kon kun san.
peya   ka   sama  ken  kin  kon  kun  san
price  PRS  be    1    2    3    4    5
```
> The price is twelve thousand three hundred and forty-five.

**13. Scientific numeral (mantissa telu fraction pole exponent)**

```
Somon pu tela ka kanu son telu kin pole sun.
somo-n     pu  tela   ka   kanu   son  telu   kin  pole   sun
person-PL  of  earth  PRS  count  8    point  2    power  9
```
> There are 8.2 billion people on Earth.

**14. Proper name frame + calque + superlative**

```
Cun Ata cun ke pemi camonu pumemu pa penawe.
cun ata cun  ke   pemi   camo-nu   pume-mu    pa   pena-we
NAME         PST  write  way-COLL  front-SUP  for  think-INS
```
> Ada wrote the first program for a computer.

**15. Comparative**

```
Ti ka tawamo pe to.
ti    ka   tawa-mo  pe    to
this  PRS  big-CMP  than  that
```
> This is bigger than that.

**16. Imperative + plural**

```
Ku tona suyu pa tiwen.
ku   tona  suyu   pa  tiwe-n
IMP  give  water  to  animal-PL
```
> Give the animals water.

**17. Universal statement (UDHR art. 1, abridged)**

```
Somo sewa ka kayale pi sowi sa sama.
somo    sewa  ka   kaya-le    pi  sowi  sa   sama
person  all   PRS  live-INCH  in  free  and  equal
```
> All human beings are born free and equal.

**18. Poem: Suyu (Water)**

```
Pala ka pelo pin suyu,
pala  ka   pelo  pin   suyu
word  PRS  go    like  water

sa suyu ka pelo pa tolo sewa;
sa   suyu   ka   pelo  pa  tolo   sewa
and  water  PRS  go    to  place  all

cu tolo sewa ka kaya po suyu,
cu   tolo   sewa  ka   kaya  po    suyu
SEP  place  all   PRS  live  with  water

sa somo sewa ka kaya po pala.
sa   somo    sewa  ka   kaya  po    pala
and  person  all   PRS  live  with  word

Cu pala sewa ka sama ken.
cu   pala  sewa  ka   sama  ken
SEP  word  all   PRS  be    1
```
> Speech goes like water,  
> and water goes to every place;  
> every place lives by water,  
> and every person lives by speech.  
> All speech is one.

<!-- END:SAMPLES -->

---

## 9. Efficiency compared with English

### 9.1 Syllables per sentence (generated)

* **Palanu syllables** are counted by the parser. A name frame counts as its
  vowels + 2 (for the two `cun`).
* **English syllables** are counted from the hand-syllabified renderings stored
  in `parser.py` (e.g. `the per.son who made this`), so every count can be
  audited.
* **Estimated time** assumes 7.8 syll/s for Palanu (the rate Pellegrino et al.
  2011 measured for the CV-syllable languages Japanese and Spanish) and 6.19
  syll/s for English (same study).

<!-- BEGIN:EFFICIENCY -->
| # | sample | Palanu words | Palanu syll. | Palanu phonemes | English words | English syll. | syll. ratio P/E | est. time P/E |
|---|---|---|---|---|---|---|---|---|
| 1 | Plain transitive clause | 4 | 5 | 10 | 3 | 3 | 1.67 | 1.32 |
| 2 | Past + witnessed evidential + recipient | 8 | 12 | 25 | 8 | 10 | 1.20 | 0.95 |
| 3 | Yes/no question | 5 | 8 | 16 | 4 | 6 | 1.33 | 1.06 |
| 4 | Content question | 7 | 10 | 20 | 7 | 8 | 1.25 | 0.99 |
| 5 | Negation + cause + clause coordination + time | 13 | 19 | 41 | 11 | 14 | 1.36 | 1.08 |
| 6 | Relative clause | 10 | 17 | 34 | 9 | 11 | 1.55 | 1.23 |
| 7 | Counterfactual conditional + perfective | 10 | 13 | 28 | 8 | 9 | 1.44 | 1.15 |
| 8 | Reported evidential + inchoative | 4 | 7 | 15 | 7 | 8 | 0.88 | 0.69 |
| 9 | Inferred evidential + genitive | 8 | 10 | 21 | 5 | 5 | 2.00 | 1.59 |
| 10 | Complement clause | 8 | 11 | 22 | 6 | 7 | 1.57 | 1.25 |
| 11 | Fronted context + numeral + place noun | 12 | 18 | 40 | 10 | 15 | 1.20 | 0.95 |
| 12 | Digit-string number | 8 | 10 | 25 | 9 | 13 | 0.77 | 0.61 |
| 13 | Scientific numeral | 10 | 15 | 34 | 7 | 11 | 1.36 | 1.08 |
| 14 | Proper name frame + calque + superlative | 7 | 17 | 35 | 8 | 12 | 1.42 | 1.12 |
| 15 | Comparative | 5 | 7 | 14 | 5 | 6 | 1.17 | 0.93 |
| 16 | Imperative + plural | 5 | 8 | 17 | 4 | 7 | 1.14 | 0.91 |
| 17 | Universal statement | 8 | 14 | 28 | 8 | 11 | 1.27 | 1.01 |
| 18 | Poem: Suyu | 32 | 50 | 102 | 25 | 32 | 1.56 | 1.24 |
| | **total** | | **251** | | | **188** | **1.34** | **1.06** |
<!-- END:EFFICIENCY -->

### 9.2 Reading the numbers honestly

**Overall.** Palanu uses about **34% more syllables** than English across the
18 samples. The English baselines are deliberately the plainest natural
spoken form, contractions included (*we'll, you'd, must've*). That ratio is
expected: Palanu syllables are simple CV (≈4.6 bits maximum), while English
syllables are among the most complex in the world (up to CCCVCCCC).

Coupé et al. show that this kind of difference is compensated by speaking
rate. At the rate measured for CV languages, the **estimated speaking time is
within about 6% of English (ratio ≈1.06)**. That estimate rests on the assumed
7.8 syll/s; it is not a measurement of Palanu speakers.

Palanu does not beat the ≈39 bits/s human channel, and no language does. The
aim is to land near it while staying fully regular and deterministic.

**Where Palanu wins:**

| construction | example | syllables (Palanu vs English) |
|---|---|---|
| evidentials | `con` vs *is said to* (sample 8) | 7 vs 8 |
| digit-string numbers | `ken kin kon kun san` (sample 12) | 10 vs 13 |

Tense and aspect stacks only break even: `ki kulalo` and *would have eaten*
are both 4 syllables.

**Where it loses:**

* **Disyllabic roots vs English monosyllables** (`piya` vs *love*, sample 1).
* **The obligatory predicate marker.**
* **Name frames.** `cun` … `cun` adds 2 syllables (sample 14).
* **Relative clauses with an explicit gap** (sample 6).

Each of these losses buys something: segmentation by sound, a boundary every
parser can see, and zero ambiguity.

**Against other designed languages:**

* **Ithkuil** is far denser per syllable, but humans cannot produce or
  understand it at natural speed.
* **Toki Pona** is often shorter, because it leaves precision to context. It
  cannot express sample 13 (`8.2 × 10⁹`) or sample 8 (reported evidence) at
  all.
* **Palanu** sits deliberately in between.

---

## 10. Learning path

The plan relies on the closed design: the whole grammar fits on one page, and
the function vocabulary fits in two 5×5 tables.

### Day 1: sounds, the rule, first sentences (about 2 hours)

1. **The 15 sounds.** Learn the strong set `p t k s c`, the soft set
   `m n l y w`, and the vowels `a e i o u`. Practise the three banned
   syllables by noticing they are never needed.
2. **The one rule.** *A strong consonant starts a word.* Segment ten unspaced
   lines by ear and on paper.
3. **The clause frame:** subject + `ka/ke/ko` + verb + object.
4. **Twelve particles:** `ta tu te`, `ka ke ko`, `ce`, `ca`, `cu`, `pa`,
   `pi`, `sa`.
5. **The first 20 tier-1 roots.** Learn them with their hooks (`sama kalo pala
   pelo kome sile kono pena cana tene tona tuma kaya kula piya somo kowa tolo
   temo poni`).
6. **Practice.** Produce 50 sentences of the form `ta ke sile somo poni`
   (*I saw a good person*), and answer `ca …?` questions with `ka` / `ka ce`.

### Week 1: the whole grammar (about 1 hour a day)

* **All 48 particles**, as a 5 × 10 table (consonant = family, vowel =
  member), including the digits. Learners can count, tell the time and read
  phone numbers from day 3.
* **All 23 suffixes** in their 5 families. Derivation games: turn any root
  into a doer, a tool, a place, an opposite and a collective (`pena` →
  `penawa`, `penawe`, `penawi`, `penano`, `penanu`).
* **All 39 tier-1 roots.**
* **Questions, relative clauses and context frames:** `co`-questions, `so … co`
  relative clauses, `si … pun` conditionals, `pi … pun` time frames.
* **Evidentials:** `can`, `cen`, `con`. Retell a story three ways, as
  witness, as detective and as gossip.
* **Script.** Read and write Semanu blocks for all 24 strong and 23 soft
  syllables, and recognise word starts by the gate bar.
* **Goal:** hold a slow everyday conversation, and parse any sentence by hand
  using §4.1.

### Month 1: fluency foundations (about 30 minutes a day)

* **All 152 roots**, with spaced repetition at about 5 a day, plus 300 common
  derivations. Most are guessable once the suffixes are known.
* **Names and compounds.** Adapt your name and city into `cun` frames, and
  learn 50 standard compounds.
* **Registers.** Rewrite one paragraph in the exact, plain, courteous and
  poetic registers.
* **Fluency.** Aim for natural speed (about 7–8 syllables/s) with clear word
  onsets. Record yourself, run `parser.py` on the transcript, and fix every
  rejected sentence. The parser is a tireless grammar tutor.
* **Poetry.** Compose a 4-line poem in trochaic metre with suffix rhyme.
* **Goal:** comfortable conversation on everyday and technical topics, and
  reading Semanu at speed.

**What makes this pace plausible:**

* There is nothing irregular to memorise, so effort goes only into roots.
* Every phoneme is already in, or close to, the learner's native inventory.
* The function words are a closed, featurally organised set.

These are the properties that let Esperanto and Toki Pona learners reach use
quickly. Palanu adds a machine checker to the learning loop.

---

## 11. Appendix: machine interface and known limits

### 11.1 Processing pipeline

The reference implementation is `parser.py` (Python 3, standard library only).
It processes text in five steps:

1. **Normalise.** Lower-case the text, strip punctuation and hyphens, and
   reject any letter outside the 15-letter alphabet.
2. **Segment.** Remove whitespace, then split before each `[ptksc]`. A
   word-initial `cun` opens a name frame that runs to the next `cun`. If the
   writer used spaces, check that none fall inside a word.
3. **Analyse each word.**
   * One syllable → look it up in the particle table.
   * Otherwise → root = first four letters, then suffixes in two-letter steps,
     then an optional final `n` = plural.
4. **Parse** with the PEG of §4.11 (packrat; linear time; one parse or none).
5. **Check** the semantic constraints (no plural verbs; exactly one `co` per
   relative clause).

**Command line:**

| command | what it does |
|---|---|
| `python3 parser.py` | runs the validation suite: lexicon checks, all samples, negative tests, Zipf check, efficiency figures |
| `python3 parser.py "ta ka piya tu"` | prints the bracketed parse tree |
| `python3 parser.py --update-spec` | regenerates the generated tables in this file |

### 11.2 Lexicon validation rules (enforced)

* **Root shape:** every root matches `^[ptksc][aeiou][mnlyw][aeiou]$`, avoids
  `ci`, `yi` and `wu`, and does not begin with `cun`.
* **Closed classes are complete:**
  * the particle set equals the set of all legal monosyllables;
  * the suffix set equals the set of all legal soft syllables.
* **Forms are unique:** no form is duplicated within or across classes, and
  each root has a distinct head gloss.
* **Tier 1 has no minimal pairs.**
* **Root count** is between 150 and 200.
* **Samples:** every gloss item matches the lexicon, and the number of gloss
  items equals the number of tokens.

### 11.3 Known limits (vagueness is allowed; ambiguity is not)

Some things are deliberately vague. Vagueness, unlike ambiguity, never yields
two parses:

* nouns are number-neutral unless `-n` or a numeral is used;
* there are no articles;
* the present marker `ka` covers both habitual and ongoing action.

**Rule-fixed defaults.** Some readings are fixed by grammar rule rather than
by meaning, and speakers must learn them:

| situation | fixed reading |
|---|---|
| a prepositional phrase after the verb phrase | attaches to the clause |
| subordinate clauses | extend greedily |
| stacked modifiers | group left to right |

The grammar always provides an alternative form for the other reading: `pu`,
`pun`-fronting, or a new sentence.

**Quantifier scope** ("every person loves a person") is resolved by linear
order: earlier means wider scope. This is a convention, not yet a formal
semantics.

**Minimal pairs among the particles.** The 48 particles use every legal
monosyllable, so the particle grid is dense. Neighbours differ by one vowel
(`ke`/`ki`, `ko`/`ku`) or by the coda `n` (`ka`/`kan`, `ca`/`can`, `cu`/`cun`).
This is the opposite of the tier-1 root policy, and it is a deliberate
trade-off: monosyllabic function words are what make Palanu as short as it is.

The risk is contained by syntax. Each family occupies a different syntactic
slot, so most confusions produce a sentence that fails to parse rather than a
different well-formed sentence. For example, a misheard `kan` in a digit string
yields a stray predicate marker. In the exact register, speakers stress the
coda nasal and the vowel of particles that carry tense or number.

**What v1.0 does not settle:**

* the native script's code points;
* a full phonetic timing model;
* semantics for idioms.

All three are open for v1.1.

