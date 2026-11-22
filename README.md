<div align="center">

# Palanu

**Pala ka pelo pin suyu.**
*Speech goes like water.*

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Spec: CC BY 4.0](https://img.shields.io/badge/spec-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![Python 3](https://img.shields.io/badge/python-3-3776AB?logo=python&logoColor=white)](parser.py)
[![Parser](https://img.shields.io/badge/parser-18%2F18%20passing-brightgreen)](parser.py)

A universal spoken and written language for humans and machines.

15 sounds · one segmentation rule · zero irregularities · one parse or none

[Specification](spec.md) · [Reference parser](parser.py) · [Quickstart](#quickstart)

</div>

---

## Why Palanu?

Palanu is a constructed language you can speak, write, and parse. It uses only fifteen sounds that nearly any speaker already has, marks every word boundary with a single audible rule, and has a formal grammar in which every sentence has exactly one parse or none.

The name is an ordinary word of the language: `pala` *word, speech* plus the collective suffix `-nu`, so **Palanu** means *the whole of speech* — language.

It is designed to be easy to say, easy to hear, easy to write, and easy for a machine to take apart. The grammar is a 22-rule PEG. The reference parser runs that grammar directly: 18 annotated samples parse, and 18 deliberately invalid sentences are rejected.

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

## The 15 sounds

Only the most common, widely shared sounds of the world's languages. There is no voicing contrast, no `r`/`l` distinction, and no tones.

| | labial | coronal | dorsal / palatal |
|---|---|---|---|
| **Strong** (obstruents, word-initial only) | `p` | `t`, `s` | `k`, `c` /tʃ/ |
| **Soft** (sonorants, word-internal only) | `m`, `w` | `n`, `l` | `y` /j/ |

| | front | back |
|---|---|---|
| high | `i` | `u` |
| mid | `e` | `o` |
| low | `a` | |

Three syllables are banned, to protect fragile contrasts: `ci` (so palatalised `/ti/` never collides with a real `ci`), `yi` (too close to `i`), and `wu` (too close to `u`).

Broad accents are welcome. No single realisation is "correct": `p t k` may be aspirated or voiced, `l` may be `[l ɾ r ɹ]`, and vowels may sit anywhere in their region, as long as they are never reduced to schwa.

## The one rule

> **Every strong consonant begins a new word.**

`p t k s c` occur only at the start of a word. Soft consonants `m n l y w` occur only inside a word (and `n` may also end one). So the word boundaries are exactly the positions of the strong consonants. A listener hears them as crisp obstruent bursts; a machine finds them with one regular expression:

```python
re.split(r'(?=[ptksc])', s)
```

```
takapiyatu   →   ta | ka | piya | tu      "I love you"
```

Spaces are optional. The parser confirms, for every sample, that the space-free sound stream segments into the same words, and that a brute-force count of all valid cuts finds exactly one.

The single exception is a name frame: a word-initial `cun` opens a proper name that runs raw to the next `cun`. Even this is detected by sound.

## Word shape is word class

```
word  =  S V ( W V )* ( n )?
         S ∈ {p t k s c}    W ∈ {m n l y w}    V ∈ {a e i o u}
```

| shape | class | count |
|---|---|---|
| `S V` or `S V n`: **one syllable** | particle (closed class) | 48. Every legal monosyllable is a particle, and every particle is a monosyllable. |
| `S V W V`: **two syllables** | bare root | 152 assigned of 547 possible |
| root + `(W V)*` + `(n)` | derived or inflected content word | open |

Morpheme boundaries inside a word are positional: syllables 1–2 are the root, each later syllable is a suffix, and a final `n` is the plural. `konoyawan` = `kono` + `-ya` + `-wa` + `-n` = *teachers*. A parser never needs to search.

```mermaid
flowchart LR
    A["Strong onset<br/>p t k s c"] --> B[Vowel]
    B --> C["Soft consonant<br/>m n l y w"]
    C --> D[Vowel]
    D --> E["Optional suffixes<br/>(W V)…"]
    E --> F["Optional plural -n"]
    F --> G[Word]
```

A one-syllable word stops after the first vowel (or that vowel plus a final `n`) and is always a particle. Grammar is isolating — tense, mood, evidence, negation and questions are separate particles that never change — while vocabulary is agglutinative: `kono` *know* → `kono-ya` *teach* → `kono-ya-wa` *teacher* → `kono-ya-wi` *school`.

## How a sentence is parsed

```mermaid
flowchart TD
    A[Input text] --> B["1. Normalise<br/>lowercase, strip punctuation"]
    B --> C["2. Segment<br/>split before each p t k s c"]
    C --> D{3. Analyse each word}
    D -->|"one syllable"| E[Look up particle]
    D -->|"two or more syllables"| F["Root + suffixes<br/>+ optional plural -n"]
    E --> G["4. PEG parse<br/>22 rules · one parse or none"]
    F --> G
    G --> H["5. Semantic checks<br/>e.g. no plural verbs"]
```

## Sample sentences

Glosses are taken from the specification. Line 1 is the sentence, line 2 splits it into morphemes, and line 3 is the gloss.

**Plain transitive clause**

```
Ta ka piya tu.
ta   ka   piya  tu
1SG  PRS  love  2SG
```
> I love you.

**Yes/no question**

```
Ca tu ka pala palanu?
ca  tu   ka   pala   pala-nu
Q   2SG  PRS  speak  word-COLL
```
> Do you speak Palanu?

**Negation, cause, and coordination**

```
Tan ko ce pelo pan pilu, su tan ko pelo pi solu pumeno.
tan  ko   ce   pelo  pan      pilu  su   tan  ko   pelo  pi  solu  pume-no
1PL  FUT  NEG  go    because  rain  but  1PL  FUT  go    at  day   front-OPP
```
> We won't go because of the rain, but we'll go tomorrow.

**Universal statement (UDHR art. 1, abridged)**

```
Somo sewa ka kayale pi sowi sa sama.
somo    sewa  ka   kaya-le    pi  sowi  sa   sama
person  all   PRS  live-INCH  in  free  and  equal
```
> All human beings are born free and equal.

**Poem: *Suyu* (Water)**

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

The other thirteen annotated samples — evidentials, relative clauses, conditionals, numerals, names, and more — are in [spec.md](spec.md#82-sample-sentences-with-interlinear-gloss-generated).

## Quickstart

The reference parser is a single Python 3 file with no dependencies beyond the standard library.

```bash
git clone https://github.com/kingmk3r/palanu.git
cd palanu
python3 parser.py
```

A passing run ends with:

```
RESULT: PASS -- 18/18 samples parsed, 18/18 negative tests rejected, lexicon valid
```

Parse a sentence of your own and print the tree:

```bash
python3 parser.py "Ta ka piya tu."
```

Regenerate the generated tables inside `spec.md` (lexicon, grammar, sample glosses, and efficiency figures) from the parser, which is the single source of truth:

```bash
python3 parser.py --update-spec
```

The file is named `spec.md` (not `SPEC.md`) because the parser looks for that path.

## Efficiency, honestly

Palanu does not yet beat English on raw syllable count, and the specification does not pretend otherwise.

Across the 18 sample sentences, Palanu uses **251 syllables** against **188** in plain spoken English — about **34% more syllables**. Because Palanu syllables are simple CV, they can be spoken faster. At the rates Pellegrino et al. (2011) measured for CV languages (7.8 syll/s) versus English (6.19 syll/s), the **estimated speaking time is about 6% longer** than English (ratio ≈ 1.06). That estimate rests on an assumed rate; it is not a measurement of Palanu speakers.

The extra syllables buy something: segmentation by sound, a boundary every parser can see, and zero ambiguity. Palanu wins on evidentials (`con` vs *is said to*) and on digit-string numbers; it loses on disyllabic roots versus English monosyllables, the obligatory predicate marker, name frames, and explicit relative-clause gaps.

Palanu does not beat the ≈39 bits/s human channel described by Coupé et al. (2019), and no language does. The aim is to land near it while staying fully regular and deterministic.

## Known limits

Vagueness is allowed; ambiguity is not. Nouns are number-neutral unless `-n` or a numeral is used, there are no articles, and the present marker `ka` covers both habitual and ongoing action. None of these yields two parses.

Some readings are fixed by grammar rather than by meaning: a prepositional phrase after the verb phrase attaches to the clause, subordinate clauses extend greedily, and stacked modifiers group left to right. The grammar always provides an alternative form for the other reading.

Quantifier scope is resolved by linear order (earlier means wider scope). This is a convention, not yet a formal semantics.

The 48 particles use every legal monosyllable, so neighbours can differ by one vowel or by a coda `n`. Syntax usually turns a mishearing into an ungrammatical sentence rather than a different well-formed one, but this density is a real trade-off against the tier-1 root policy (no minimal pairs). Dropping a final `n` is also a weak point: it never moves a word boundary, but it can change the word.

v1.0 does not settle the native script's code points, a full phonetic timing model, or semantics for idioms.

## Roadmap

Open for v1.1, as listed in the specification:

- Code points for the Semanu script
- A full phonetic timing model
- Semantics for idioms

The lexicon still has **395 free root slots**. Contributions that respect the phonology, the unique-form rules, and the tier-1 no-minimal-pair constraint are welcome.

## Contributing

1. Keep the one rule: strong consonants only begin words; soft consonants only appear inside them.
2. Add no irregular forms, agreement, or stem changes.
3. After any change to the lexicon, grammar, or samples, run `python3 parser.py` and make sure it still reports `RESULT: PASS`.
4. If you change generated tables, refresh them with `python3 parser.py --update-spec` and commit `spec.md` together with `parser.py`.

Issues and pull requests are welcome.

## License

- **Code** (`parser.py` and related software) is released under the [MIT License](LICENSE).
- **The language specification** (`spec.md`, including the phonology, grammar, lexicon, and sample texts) is released under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

---

<div align="center">

*Pala ka pelo pin suyu.*

</div>
