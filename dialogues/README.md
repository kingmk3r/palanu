# Palanu dialogues

[Back to the README](../README.md#hear-palanu) · [Translations and glossary](../TRANSLATIONS.md)

Five recorded conversations in Palanu, with English translations. Every Palanu line was checked with the reference parser (`python3 parser.py "<line>"` from the repo root) and every line parses.

Audio was made with ElevenLabs `eleven_v4` using stock Japanese-native voices: **Hdo** (male) and **Madoka** (female) for dialogues 1–4, and **AiMoTo**, a warm radio-host voice (male), with **kaori** (female) for dialogue 5. No real person's voice was cloned or imitated. For the speech model only, each Palanu syllable was respelled as one katakana (`c` → チャ/チェ/チョ/チュ, `si` → シ, word-final `n` → ン; the spec allows `l` to be heard as `[ɾ]` and `s` before `i` as `[ɕ]`). Palanu stress falls on the first syllable; Japanese pitch accent handles this only approximately. Short emotion tags like `[excited]` set the tone. Lines were generated one at a time and joined with 0.45 s gaps, then loudness-normalised. The text below is canonical Palanu.

Each dialogue has an `.mp3`, an `.mp4` with the Palanu line and English subtitle burned in, and an `.srt` subtitle file timed from the clip lengths. An earlier take with Spanish-native voices (JOHN C, Alina, Santiago, Olivia) is kept in [`es/`](es/).

**Blind transcription check.** Two finished dialogues were uploaded and transcribed from scratch with ElevenLabs Scribe, which had never seen the text, and the result was compared letter by letter with the Palanu (lower-cased, punctuation and spaces removed; `r`→`l`, `sh`→`s`, `ch`→`c` folded, as the spec allows). Scribe heard dialogue 5 as Korean and wrote it in Hangul, which was romanised before comparing.

| Dialogue | Match |
|:--|--:|
| 1. At the market | 93.9% |
| 5. A cosmic talk show | 97.9% |

Most misses in dialogue 1 are devoiced or dropped `u` in short particles (`cu`, `ku`, `pu`), a normal Japanese habit.

## 1. At the market

Audio: [dialogue-1-market.mp3](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-1-market.mp3) · Video: [dialogue-1-market.mp4](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-1-market.mp4) · Subtitles: [dialogue-1-market.srt](dialogue-1-market.srt). Speakers: A = Shopper (male), B = Fruit seller (female).

**A:** Salama, sawi! Ca tu ka tene kiwawo sinu?  
*Hello, friend! Do you have fresh fruit?*

**B:** Ka! Cu kiwawo pu ta ka sinu, sa to ka pemu. Cu ku sile!  
*Yes! My fruit is fresh and sweet. Take a look!*

**A:** Peya pu kiwawo soluni ka sama co?  
*What is the price of the yellow fruit?*

**B:** Peya ka sama kin pa kiwawo ken.  
*It's two for one fruit.*

**A:** Ta ka cana kiwawo san. Ca tu ki tona tiyu tuye?  
*I want five. Could you give me some bread too?*

**B:** Ka. Cu peya pu sewa ka sama ken kin. Cu tane, sawi!  
*Sure. The price of everything is twelve. Thank you, friend!*

**A:** Tane! Cu tu ku tene solu poni!  
*Thanks! Have a good day!*

**Notes:** Numbers use the spec's digit words: `kin` = 2, `san` = 5, `ken kin` = 12 (the twelve covers five fruits at two each, plus bread).

## 2. At the doctor's

Audio: [dialogue-2-doctor.mp3](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-2-doctor.mp3) · Video: [dialogue-2-doctor.mp4](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-2-doctor.mp4) · Subtitles: [dialogue-2-doctor.srt](dialogue-2-doctor.srt). Speakers: A = Doctor (male), B = Patient (female).

**A:** Salama. Cu tu ka seni camo co?  
*Hello. How are you feeling?*

**B:** Kemo pu ta ka puwe, sa ta ka pilo.  
*My head hurts, and I have a fever.*

**A:** Puwe ke kome pi temo co?  
*When did the pain start?*

**B:** Puwe ke kome pi solu kin pume.  
*It started two days ago.*

**A:** Puye ka ce tawa. Cu ku pinu suyu pulu, sa ku temu pulu.  
*It's not a big problem. Drink lots of water, and sleep a lot.*

**B:** Ca ta ka caye sanawe?  
*Do I need medicine?*

**A:** Ka. Cu ku tuma sanawe ti pi solulu.  
*Yes. Take this medicine in the evening.*

**B:** Tane, sanayawa! Cu ta ka kiwe so ta ko sana kuwi.  
*Thank you, doctor! I hope I'll get well quickly.*

**Notes:** `sanawe` (health-INS, 'a means of health') is a calque for *medicine*, and `sanayawa` (heal-CAUS-AGT, 'one who makes healthy') is a calque for *doctor*. Neither is in the spec's tables, but both follow its suffix rules.

## 3. Two friends plan a trip

Audio: [dialogue-3-trip.mp3](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-3-trip.mp3) · Video: [dialogue-3-trip.mp4](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-3-trip.mp4) · Subtitles: [dialogue-3-trip.srt](dialogue-3-trip.srt). Speakers: A = Tomas (male), B = Maria / Malia (female).

**A:** Salama, cun Malia cun! Ca tu ko pelo po ta pa sowa?  
*Hi, Maria! Will you come with me to the sea?*

**B:** Ka! Cu ta ka piya sowa. Cu tan ko pelo pi temo co?  
*Yes! I love the sea. When will we go?*

**A:** Tan ki pelo pi solu sin pumeno.  
*We could go in a week.*

**B:** Ca tan ko pelo po pelowe se culewe?  
*Will we go by car, or by plane?*

**A:** Culewe ka kuwi, su peya pu to ka tawa. Cu tan ku pelo po pelowe!  
*The plane is fast, but it's expensive. Let's take the car!*

**B:** Poni! Cu ta ko puna kula sa suyu.  
*Great! I'll bring food and water.*

**A:** Cu tan ko kana pi camo!  
*Then we'll sing on the road!*

**B:** Cu pelo ti ko sama sulo. Tane, sawi!  
*This trip will be beautiful. Thanks, friend!*

**Notes:** `pelowe` = vehicle/car (from the spec). `culewe` (fly-INS) = airplane, a calque. Line 7 was planned as "And we'll sing...", but a sentence can't open with `sa`, so it uses the `cu` opener instead.

## 4. A tense moment at work

Audio: [dialogue-4-apology.mp3](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-4-apology.mp3) · Video: [dialogue-4-apology.mp4](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-4-apology.mp4) · Subtitles: [dialogue-4-apology.srt](dialogue-4-apology.srt). Speakers: A = Coworker (male), B = Ana (female).

**A:** Cun Ana cun pun, pemiwo pu tu ke ce kome pa ta. Cu puye ka sama co?  
*Ana, your report never reached me. What's the problem?*

**B:** Ta ka seni ponino pen ti. Cu penawe pu ta ke tana.  
*I feel terrible about this. My computer died.*

**A:** Kume ke kiyu. Cu te ke caye pemiwo pi solu ti.  
*The boss was angry. She needed the report today.*

**B:** Ta ka kono, sa tu ka tuli. Cu ta ke caye pala pa tu pume.  
*I know, and you're right. I should have told you sooner.*

**A:** Ca tu ki kalo pemiwo sinu pi solulu ti?  
*Could you make a new report by this evening?*

**B:** Ka. Cu ta ko kalo to pi solulu ti. Cu ta ka tane tu pan so tu ke tewo.  
*Yes. I'll have it done this evening. Thank you for waiting.*

**A:** Sala, sawi. Cu tan ka kuyu.  
*It's all right, friend. We're a team.*

**Notes:** Palanu has no word for "sorry", so the apology is `ta ka seni ponino pen ti`, "I feel bad about this". Line 3 originally began with "But" (`su`), which can't open a sentence, so it was dropped.

## 5. A cosmic talk show: stars, black holes and the expanding universe

Audio: [dialogue-5-astrophysics.mp3](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-5-astrophysics.mp3) · Video: [dialogue-5-astrophysics.mp4](https://cdn.jsdelivr.net/gh/kingmk3r/palanu@main/dialogues/dialogue-5-astrophysics.mp4) · Subtitles: [dialogue-5-astrophysics.srt](dialogue-5-astrophysics.srt). Speakers: A = Host, an excited astrophysicist (male), B = Co-host, curious and funny (female).

**A:** Salama, somon pu tela! Cu pi solu ti pun tan ko palayu pen seyon sa sewanu.  
*Greetings, people of Earth! Today we're talking about the stars and the universe.*

**B:** Ta ka kono kowa kan pen seyon. Cu seyo ka sama co?  
*I know absolutely nothing about stars. So what is a star?*

**A:** Seyo ka sama pilo tawama pi sela suma. Cu pi kole pu to pun seyo ka tali cun atom cun tawano pa cun atom cun tawamo.  
*A star is a gigantic fire in the night sky. Deep in its heart, the star fuses small atoms into bigger atoms.*

**B:** Cu cun atom cun tawamo ke pelo pa tolo co?  
*So where did those bigger atoms go?*

**A:** Pi so seyo tawa ke tana pun to ke pelema, sa cun atom cun ke pelo pa sewanu. Cu pelu pu suyu piloni pu tu ke kome pe seyo! Cu tan sewa ka sama seyonan. Cu ku pena pen to!  
*When a big star died, it exploded, and its atoms flew out into the universe. The iron in your blood came from a star! We are all made of star pieces. Think about that!*

**B:** Cowi! Cu ta ka sama seyo! Cu ta ke kono to pume. Cu pune sumani ka sama co?  
*Whoa! So I'm a star! I knew it all along. And what's a black hole?*

**A:** Pi so seyo tawama ka tana pun to ki sama pune sumani. Cu pole puma pu to ka tawama, sa kolo ka ce pole pelo pe to.  
*When a giant star dies, it can become a black hole. Its gravity is so enormous that not even light can escape it.*

**B:** Ca pune sumani ki tuma ta? Cu ta ka kowe!  
*Could a black hole grab me? I'm scared!*

**A:** Ka ce, sawi. Cu to ka tayoma pe tan. Cu pole puma ka kuluya tolo, sa kolo ka tiye tolo kuluyo.  
*No, my friend. It's very far from us. Gravity bends space itself, and light follows that bent space.*

**B:** Ta ke pena so kolo ka pelo pi tali sola!  
*I thought light only travels in a straight line!*

**A:** Cu sewanu ka tawale! Cu pi so tu ka sile seyo tayo pun tu ka sile kolo so co ke pelo kulu kolo ken kan kan kan. Cu tu ka sile temo pume!  
*And the universe is expanding! When you look at a distant star, you see light that traveled a thousand light-years. You are looking into the past!*

**B:** Sewanu ka tawale, sa tanu pu ta ka tawale tuye, pan kula pulu! Tane, sawi!  
*The universe is expanding, and so is my waistline, thanks to all the food! Thanks, friend!*

**Notes:** Technical terms follow §5.3/5.4 (head-first compounds, calques) and the `cun` frame (§5.5):
- `sewanu` (all-COLL) = the universe. `seyonan` (star-PART-PL) = pieces of stars, i.e. stardust.
- `pune sumani` ("black door") = black hole. `pole puma` ("power of weight") = gravity.
- `kulu kolo` ("year of light") = light-year. `ken kan kan kan` = 1000.
- `cun atom cun` = "atom", a foreign word inside a name frame. `pelu` (metal) is used for iron.
- `pelema` (split-AUG) = explode. `kuluya` (circle-CAUS) = bend. `kuluyo` (circle-PASS) = bent. `tawale` (big-INCH) = grows, expands.
- `suyu piloni` ("red liquid") = blood.

Simplifications: "fuses atoms" became `tali` ("connects/joins"), and "a straight line" became `tali sola` ("a single line").
