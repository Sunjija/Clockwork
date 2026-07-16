# ACT1 Suno 음악 제작 계획

> 상태: 모든 장르, 악기, 템포와 모티프 처리는 사용자 승인 전까지 후보이다. 지역명과 진행 순서는 ACT1 맵을 따른다.

## 제작 범위

| 분류 | 제목 | 제작 방식 | 상태 |
| --- | --- | --- | --- |
| 지역 | 림부스 | 독립 지역곡 | 후보 2안 생성 완료 |
| 지역 | 칼리고 | 독립 지역곡 | 후보 2안 생성 완료 |
| 지역 | 교차로 대공동 | 독립 지역곡 | 후보 2안 생성 완료 |
| 지역 | 정수장치 | 독립 지역곡 | 후보 2안 생성 완료 |
| 지역 | 지하심층 | 독립 지역곡 | 후보 2안 생성 완료 |
| 지역 | 터미너스 | 독립 지역곡 | 후보 2안 생성 완료 |
| 보스 | 렌토 | 정수장치 변주 | 후보 2안 생성 완료 |
| 보스 | 지하 사냥꾼 | 지하심층 변주 | 후보 2안 생성 완료 |
| 보스 | 거대 거미 | 터미너스 변주 | 후보 2안 생성 완료 |
| 선택 탐사 | 구 폐기물 선별장 | 림부스 변주 | 후보 2안 생성 완료 |
| 선택 탐사 | 폐쇄 송수로 | 정수장치 변주 | 후보 2안 생성 완료 |
| 선택 탐사 | 심층 굴착지 | 지하심층의 독립적 굴착 변주 | 기존 후보 2안은 터미너스 연결 기각 · 재생성 필요 |
| 전환 | 림부스-칼리고 교량 | 효과음과 분리된 림부스 파손·감속 변주 | 순수 BGM 2안·단순 도입 실험 2안·반복형 2안 생성 완료 |
| 기억 | 기억① — 정체성 | 정수장치에서 발생하는 제작 기억과 위화감 | 장소 연동 후보 2안 생성 완료 |
| 기억 | 기억② — 결정화 목격 | 지하심층에서 발생하는 황금빛 데이터 일치 | 장소 연동 후보 2안 생성 완료 |

## 공통 연결 규칙

- 작업용 기억 모티프 [제안]: 짧게 상승한 뒤 마지막 응답음을 비워 두는 프레이즈. 정확한 음정은 이번 후보에서 확정하지 않는다.
- 림부스에서는 모티프를 조각내고, 칼리고에서는 따뜻한 응답구로 바꾸며, 기억 회수에서 가장 전면에 둔다.
- 보스곡은 새로운 장르를 시작하지 않고 직전 지역의 리듬과 대표 악기를 공격 패턴으로 압축한다.
- 렌토 격파 후 필요한 시설 복구음은 정수장치 후보의 해소 구간에서 편집한다.
- 거대 거미 격파 후 필요한 지상 개방음은 거대 거미 후보의 종결부에서 편집한다.
- 선택 탐사곡은 긴 독립 서사보다 1~2분 반복과 입구 복귀 편집점을 우선한다.
- 기억은 독립 BGM으로 전환하지 않는다. 지역 BGM 감쇠 → 1초 정적 → 8~15초 장소 연동 오버레이 → 변형된 지역 BGM 복귀 구조를 사용한다.

## 기존 지역 후보

기존 결과의 프롬프트와 ID는 `02_suno_anchor_experiments.md`를 기준으로 한다.

## 신규 생성 결과

| 제목 | 후보 | 길이 | Suno ID |
| --- | --- | ---: | --- |
| 교차로 대공동 | A | 2:38 | `6cd2ae7c-265a-4dd7-8be8-0bb83e1f3f81` |
| 교차로 대공동 | B | 2:25 | `82bc95f1-7c76-4dab-959e-670fa62fbef5` |
| 터미너스 | A | 1:09 | `26e7d859-b42d-47bc-8dad-b4c55cc770fa` |
| 터미너스 | B | 2:59 | `7e379c81-f9bb-4133-a273-2b8143a9f198` |
| 렌토 | A | 1:08 | `7281abad-f10d-4d24-ad62-081015dfd374` |
| 렌토 | B | 0:53 | `af38d3b9-238f-491f-bf1c-4a20fcadc348` |
| 지하 사냥꾼 | A | 0:30 | `14af122a-cdee-4636-a339-f19a66070d7f` |
| 지하 사냥꾼 | B | 0:30 | `8caff3cf-ae72-487e-94a7-0e5dec9b237e` |
| 거대 거미 | A | 2:20 | `3240c45c-c518-46c2-9bee-61c9c8a650b1` |
| 거대 거미 | B | 1:13 | `e2178c17-fb77-4bdc-be73-feb97bcdfb10` |
| 구 폐기물 선별장 | A | 1:19 | `83ecadd7-24e1-4506-80bf-4023391d686e` |
| 구 폐기물 선별장 | B | 1:47 | `10dddf30-3702-4a3d-8a7c-7aa911fe2c55` |
| 폐쇄 송수로 | A | 1:38 | `004c40fa-6edd-4e80-897a-94241f965ebe` |
| 폐쇄 송수로 | B | 1:29 | `537fda13-7fa1-4ae9-a7cd-5a9f7e91f8d6` |
| 심층 굴착지 구안 · 터미너스 연결 기각 | A | 3:25 | `d7445d0d-bd24-4b85-86a5-052f0566f2e7` |
| 심층 굴착지 구안 · 터미너스 연결 기각 | B | 3:08 | `6d80aa2e-bb3b-4514-902d-813cb334559e` |
| 림부스-칼리고 교량 구안 · 기각 | A | 0:49 | `4f6b5638-b998-4dec-adf6-c13e1d23128e` |
| 림부스-칼리고 교량 구안 · 기각 | B | 0:48 | `914f78b6-b1e9-4f01-8eaf-11dcad8b3018` |
| 림부스-칼리고 교량 중간안 · BGM/SFX 혼합 기각 | A | 0:53 | `d6e256cc-8263-47a6-90e4-1666c1b345d0` |
| 림부스-칼리고 교량 중간안 · BGM/SFX 혼합 기각 | B | 0:52 | `1983a397-df09-47d9-8d1d-759ecf54f41a` |
| 림부스-칼리고 교량 · 순수 BGM | A | 2:43 | `53b286bc-b37c-4c3c-ab79-090bb457070c` |
| 림부스-칼리고 교량 · 순수 BGM | B | 2:08 | `da6795be-c179-4ce9-9321-999991ba677c` |
| 림부스-칼리고 교량 · 단순 도입 실험 | A | 0:19 | `f859c783-37ca-4adb-9905-e9eda83e94c1` |
| 림부스-칼리고 교량 · 단순 도입 실험 | B | 0:19 | `176417d6-9a52-4ede-933d-11e1b0d08fb7` |
| 림부스-칼리고 교량 · 긴 반복형 | A | 1:25 | `fb82d018-9f4e-4c69-8ccd-e8b12a03d23c` |
| 림부스-칼리고 교량 · 긴 반복형 | B | 1:27 | `165758c6-3d04-48c7-81b7-151a47cc02bd` |
| 기억 회수 구안 · 기각 | A | 2:02 | `5e2d0102-1977-47eb-a5d1-0943d49c6f6a` |
| 기억 회수 구안 · 기각 | B | 0:53 | `d4de0b77-8613-4989-b75d-2623d792e1bf` |
| 기억 회수 구안 · 기각 | C | 1:24 | `9d958056-c5e1-4c08-ba0a-10db37667c63` |
| 기억 회수 구안 · 기각 | D | 1:28 | `d5a55eec-8606-45d8-bd0a-60b5bb889c7d` |
| 기억① 중간안 · 장소 연동 부족 | A | 1:16 | `ef9d1b15-014a-4000-91e1-57ea05aabb04` |
| 기억① 중간안 · 장소 연동 부족 | B | 1:17 | `8ac260ec-0141-4773-a1f4-df6044c47f62` |
| 기억② 중간안 · 장소 연동 부족 | A | 1:20 | `f7f89071-a735-41ef-9449-94650cdd7fcd` |
| 기억② 중간안 · 장소 연동 부족 | B | 1:34 | `74b21cd4-3cfb-4470-a4a1-2f0cb9dcc721` |
| 기억① — 정체성 · 장소 연동 | A | 0:49 | `1986876d-ada2-4a3a-8af4-5d88c0bcbe52` |
| 기억① — 정체성 · 장소 연동 | B | 0:31 | `445029ab-0bcd-454a-a4b1-393ba0ba97f1` |
| 기억② — 결정화 목격 · 장소 연동 | A | 1:38 | `f2451d17-6b56-41ca-8ced-07ea6b307f77` |
| 기억② — 결정화 목격 · 장소 연동 | B | 2:20 | `684e725d-aa0b-4b4e-afa5-4906f8efd505` |

## 신규 생성 프롬프트

### 교차로 대공동

**Style**

```text
Spacious underground chamber post-minimalism, 64 BPM, E minor. Low cello and bass clarinet carry a slow route-finding figure while the unfinished memory phrase appears only as distant celesta reflections. Deep water impacts divide long stone resonances; a restrained prepared-piano pulse changes register as different passages open. Broad but readable A/B exploration loop, no climax, clean transition points.
```

**Exclude**

```text
vocals, lyrics, choir, constant drone, fast percussion, action music, horror stingers, heroic brass, generic cave ambience, excessive reverb
```

### 터미너스

**Style**

```text
Ascending industrial post-rock chamber cue, 92 BPM in elastic 6/8. Prepared piano carries a freight-pulley rhythm, plucked cello climbs one register at each section, and dry chain strikes mark platform cycles. The unfinished memory phrase is buried in the bass, then gains range as the ascent continues. Sparse lower station, driving middle climb, exposed upper landing, seamless layered exploration loop with an edit-friendly release.
```

**Exclude**

```text
vocals, lyrics, choir, arena rock, constant full drums, EDM drop, trailer braams, heroic fanfare, ticking-clock cliché, excessive distortion, excessive reverb
```

### 렌토

**Style**

```text
Three-phase industrial chamber boss cue, 88 BPM with pressure-driven meter changes. Tuned pipe strikes and low strings state a heavy predator motif while the water-treatment pulse repeatedly stalls. Phase one leaves broad gaps after each slow impact; phase two adds skittering subdivisions beneath the main meter; phase three drives upward leaps and three spaced shockwave accents. Every vulnerability window drops to exposed pipe resonance and the unfinished player phrase. Tight wet acoustics, decisive mechanical restart ending.
```

**Exclude**

```text
vocals, lyrics, choir, EDM drop, metal guitar wall, trailer braams, constant blast beats, playful animal music, heroic victory theme, excessive reverb
```

### 지하 사냥꾼

**Style**

```text
Asymmetric predatory chamber battle, 74 BPM alternating 5/8 and 7/8. Contrabass clarinet stalks in short descending cells, muted low strings pull phrases abruptly backward, and sparse frame-drum attacks arrive after misleading silences. The player memory phrase is compressed into a cornered high-register answer during brief counterattack windows. Close damp acoustics, one focused encounter arc, hard stop before the memory room.
```

**Exclude**

```text
vocals, lyrics, choir, horror trailer, jump-scare hits, jazz lounge swing, constant drums, heroic fanfare, busy orchestration, excessive sub bass, excessive reverb
```

### 거대 거미

**Style**

```text
Baroque industrial ascent boss cue, 112 BPM in tense 12/8. Prepared piano twists the Terminus pulley rhythm into an interlocking ostinato, tremolo strings trace circular wall movement, and dry web snaps interrupt the meter. The middle phase seals layers through sudden register drops; the final chase adds rising cello and controlled post-rock weight. At defeat, percussion falls away and the unfinished player phrase finally reaches a bright upper-register response as the surface gate opens. Decisive edit-friendly ending.
```

**Exclude**

```text
vocals, lyrics, choir, symphonic metal, arena rock chorus, trailer braams, heroic fanfare from the opening, EDM drop, constant maximum density, excessive reverb
```

### 구 폐기물 선별장

**Style**

```text
Industrial puzzle minimalism, 78 BPM. Muted conveyor clacks rearrange the Limbus pulse, magnetic metal tones answer across the stereo field, and a dry bass clarinet marks each sorting-state change. The damaged memory fragment appears as misplaced celesta notes that gradually align when the machinery is restored. Compact A/B loop, clear reset point, curious rather than threatening.
```

**Exclude**

```text
vocals, lyrics, choir, factory-noise wall, techno drop, slapstick machinery, busy drums, heroic melody, generic dark ambient, excessive reverb
```

### 폐쇄 송수로

**Style**

```text
Glass-toned hydraulic minimalism, 70 BPM, long horizontal phrasing. Glass harmonics carry a narrow flowing melody, tuned pipe taps mark distant pressure changes, and felt piano answers with the water-treatment motif at half density. The arrangement brightens only when valves balance, then returns to a calm hidden-route loop. Clean damp reflections, exploratory and slightly uncanny, edit-friendly tail.
```

**Exclude**

```text
vocals, lyrics, choir, spa ambience, fantasy water music, techno beat, constant arpeggios, action percussion, heroic fanfare, excessive reverb
```

### 심층 굴착지 구안 · 터미너스 연결 기각

사용자 피드백: 굴착지는 봉쇄된 시설이 아니며 터미너스와 물류·서사상 연결하지 않는다. 아래 생성안은 광차 리듬을 터미너스 도르래 리듬에 연결했으므로 기존 후보와 함께 기각한다.

**Style**

```text
Percussive industrial doom-jazz exploration, 82 BPM with heavy pauses. Piston thumps regularize the Underground Depths bass figure, mine-cart wheel rhythms answer the Terminus pulley cell, and low cello carries a wary hook through collapsed tunnels. A brighter metal response appears only near the hidden supply room. Dense enough for late exploration but never a combat climax, circular route loop with a clean return point.
```

**Exclude**

```text
vocals, lyrics, choir, jazz lounge swing, metal guitar wall, constant action drums, horror trailer, triumphant discovery fanfare, excessive sub bass, excessive reverb
```

### 림부스-칼리고 교량 구안 · 기각

사용자 피드백: 티크는 전신이 파손되어 공격보다 긴급 밀치기와 버티기만 가능한 상태다. `96 BPM` 추격 리듬과 쥐떼 세분 리듬은 티크를 정상적인 액션 주인공처럼 보이게 하므로 사용하지 않는다.

**Style**

```text
Fragile pursuit transition, 96 BPM with a damaged uneven pulse. Bowed scrap metal and muted conveyor clacks accelerate the Limbus fragment while low strings repeatedly fail to complete the phrase. Short rat-swarm subdivisions gather beneath the chase, then the entire rhythm buckles into silence as Tique collapses. A distant reed-organ warmth appears for only the final breath, pointing toward Caligo. Compact edit-friendly cue, no triumphant ending.
```

**Exclude**

```text
vocals, lyrics, choir, heroic chase music, comedy, full rock drums, EDM drop, trailer braams, long cinematic intro, triumphant cadence, excessive reverb
```

### 림부스-칼리고 교량 중간안 · BGM/SFX 혼합 기각

획득 위치가 아니라 오프닝 상태 전환 구간이다. 별도 추격곡으로 시작하지 않고 림부스 BGM의 박자와 부품이 하나씩 고장 나는 변주로 연결한다.

사용자 피드백: 교량 삐걱임, 서보 고장음, 쥐 긁는 소리처럼 인게임에서 재생할 효과음을 BGM 프롬프트에 포함했다. 음악과 효과음의 역할이 섞이므로 사용하지 않는다.

**Style**

```text
Near-collapse limping transition continuing directly from the Limbus cue, 56 BPM in unstable 6/8 with missing beats. Bowed scrap metal, bridge groans and muted conveyor clacks slow down, misfire and drop out; each movement is one heavy servo lurch followed by exhausted silence. Rats register only as brief dry scratches and two short threat bursts, never a chase groove. Low cello rises once for an emergency shove. The pulse loses pieces and stops as Tique collapses; one distant reed-organ breath hints at Morbi and Caligo.
```

**Exclude**

```text
vocals, lyrics, choir, fast tempo, chase music, action groove, rat-swarm ostinato, constant drums, heroic struggle, trailer braams, triumphant cadence, comedy, energetic rock, EDM drop, excessive reverb
```

### 림부스-칼리고 교량 · 순수 BGM

BGM은 빠지는 박자, 누락되는 음, 늦게 진입하는 연주와 감소하는 다이내믹만으로 티크의 파손을 표현한다. 금속 마찰, 서보, 교량, 쥐, 충돌음은 별도 SFX 자산으로 구현한다.

**Style**

```text
Pure instrumental chamber transition derived from the Limbus theme, 54 BPM in unstable 6/8. Muted felt piano states the same damaged motif with missing notes and long rests; pizzicato cello enters slightly late while bass clarinet holds fragile unresolved lines. Two brief harmonic compressions mark danger without accelerating the tempo. Dynamics, register and orchestration thin steadily until the phrase can no longer continue; one distant reed-organ chord hints at Caligo after the collapse. Musical instruments only.
```

**Exclude**

```text
vocals, lyrics, choir, sound effects, foley, field recording, scraping metal, machinery noises, servo sounds, bridge groans, creature sounds, rat scratches, cinematic impacts, fast tempo, chase music, action groove, constant drums, heroic struggle, trailer braams, excessive reverb
```

### 림부스-칼리고 교량 · 단순 도입 실험

사용자 피드백: 순수 BGM 후보는 시작부터 멜로디 변화가 많다. 첫 24초는 3음 동기 하나를 거의 바꾸지 않고 반복하고, 중반 이후에만 두 번의 작은 변화가 생기도록 멜로디 행동을 제한한다. 생성 결과는 두 안 모두 0:19이므로, 단순성뿐 아니라 교량 구간에 필요한 재생 길이를 충족하는지도 함께 검토한다.

**Style**

```text
Pure instrumental chamber transition derived from the Limbus theme, 54 BPM in unstable 6/8. Open with 24 seconds of one simple three-note muted felt-piano figure, repeated almost unchanged with long rests. Bass clarinet sustains one low pedal; pizzicato cello marks only the last beat of every second bar. Keep the melody narrow, sparse and repetitive, with no counter-melody and very few chord changes. After the midpoint, allow only two small changes: the cello rises one octave, then one compressed harmony signals danger. Gradually remove notes and end on a single distant reed-organ chord hinting at Caligo. Musical instruments only, loop-friendly.
```

**Exclude**

```text
vocals, lyrics, choir, sound effects, foley, field recording, machinery noises, creature sounds, cinematic impacts, busy melody, melodic development, counter-melody, ornamentation, arpeggios, frequent chord changes, modulation, fast tempo, chase music, action groove, constant drums, heroic swell, trailer braams, excessive reverb
```

### 림부스-칼리고 교량 · 긴 반복형

`24 seconds` 지시가 두 후보 모두 0:19로 끝나는 짧은 큐를 유도했으므로 초 단위 지시를 제거했다. 대신 전체 길이를 2~3분으로 요청하고 첫 40% 동안 동일한 3음 동기 외의 새 선율을 금지했다. 실제 생성 결과는 1:25와 1:27이며, 길이보다 도입부의 단순성과 게임 구간 적합성을 우선 비교한다.

**Style**

```text
Pure instrumental chamber exploration-transition derived from the Limbus theme, 54 BPM in unstable 6/8, 2 to 3 minute loopable cue. For the first 40 percent, repeat exactly one simple three-note muted felt-piano cell with the same pitches and rhythm, separated by long rests. Bass clarinet sustains one low pedal; pizzicato cello marks only the last beat of every second bar. Introduce no new melodic material. In the middle, allow one change only: cello doubles the cell one octave higher once, then withdraws. The final third gradually removes notes and leaves one unresolved distant reed-organ chord that can return to the opening. Musical instruments only.
```

**Exclude**

```text
vocals, lyrics, choir, sound effects, foley, field recording, machinery noises, creature sounds, cinematic impacts, busy melody, melodic development, counter-melody, ornamentation, arpeggios, frequent chord changes, modulation, fast tempo, chase music, action groove, constant drums, heroic swell, trailer braams, excessive reverb
```

### 기억 회수 구안 · 기각

사용자 피드백: 4안 모두 지나치게 슬프고 감정을 선행 규정한다. 정본의 `감정 부여는 플레이어 몫` 원칙과 맞지 않아 사용하지 않는다.

**Style**

```text
Intimate two-stage memory miniature, free pulse around 52 BPM. In the first section, solo celesta exposes a short rising phrase but leaves its answer missing; one bowed cello harmonic responds from far away. After a clean silence, felt piano restates the same contour with a warmer cello answer and one quiet bell-like metal resolution, creating a fuller second-memory edit. Close dry room, emotionally clear but restrained, separate edit points and a gentle unresolved tail.
```

**Exclude**

```text
vocals, lyrics, choir, sentimental orchestral swell, music-box cliché, generic sad piano, trailer emotion, percussion groove, magical sparkle effects, excessive reverb
```

### 기억① 중간안 · 장소 연동 부족

**Style**

```text
Mechanical recognition miniature, 76 BPM, bright and curious rather than sad. A crisp three-note celesta signal clicks into alignment with tiny tuned-metal relays; warm reed organ answers like a familiar workshop breathing back to life. The phrase gains one clean rhythmic layer, then a brief golden harmonic glitch interrupts the final response and cuts to silence. Intimate, alert, edit-friendly source cue.
```

**Exclude**

```text
vocals, lyrics, choir, sadness, melancholy, piano ballad, mournful cello, sentimental swell, lullaby, music-box cliché, horror stinger, magical sparkle, excessive reverb
```

### 기억② 중간안 · 장소 연동 부족

**Style**

```text
Data-recognition flash cue, 92 BPM, lucid awe and alert curiosity rather than sadness. Bright glass tones spread outward like a city-scale signal while dry tuned-metal pulses lock into the same three-note recognition cell from the first memory. A sudden golden harmonic expansion fills the space for one instant, then collapses to a single cold confirmation tone and silence. Precise, uncanny, non-tragic, edit-friendly source cue.
```

**Exclude**

```text
vocals, lyrics, choir, sadness, melancholy, piano ballad, mournful strings, sentimental swell, horror trailer, jump scare, heroic fanfare, magical fantasy, ambient wash, excessive reverb
```

### 기억① — 정체성 · 장소 연동

획득 위치: 정수장치 상부 코어실 `act1-room-018`. 정수장치 BGM에서 분리되지 않고 시설 재가동 리듬이 기억 신호로 정렬되는 오버레이이다.

**Style**

```text
Location-bound memory overlay continuing directly from the Water Treatment cue, 96 BPM. Begin mid-pattern with tuned pipe marimba and pump thumps in uneven 7/8; after the facility restart the pulse locks into clear 4/4 and reveals a crisp three-note recognition signal. One warm reed-organ breath suggests the workshop, then a golden metal-harmonic glitch interrupts before the local water rhythm resumes. No standalone intro, no emotional climax, clean 8-to-15-second extractable center.
```

**Exclude**

```text
vocals, lyrics, choir, sadness, melancholy, piano ballad, mournful cello, sentimental swell, standalone cinematic intro, heroic fanfare, magical fantasy, ambient wash, excessive reverb
```

### 기억② — 결정화 목격 · 장소 연동

획득 위치: 지하심층 기억 회수실 `act1-room-028`. 지하심층 BGM의 저음과 공백을 유지한 채 기억①의 인식 신호가 황금빛 데이터 일치로 재검출되는 오버레이이다.

**Style**

```text
Location-bound memory overlay continuing directly from the Underground Depths cue, 58 BPM. Contrabass clarinet, bowed low cello, wet-stone pulses and long rests remain in place as the hunter rhythm disappears. The same three-note recognition signal from the first memory surfaces in glass-metal overtones above the depth texture; one city-scale golden expansion flashes, collapses to a dry confirmation tone, then the original damp exploration bed resumes. No standalone intro, non-tragic, clean 8-to-15-second extractable center.
```

**Exclude**

```text
vocals, lyrics, choir, sadness, melancholy, piano ballad, mournful strings, sentimental swell, horror trailer, jump scare, standalone cinematic intro, heroic fanfare, magical fantasy, excessive reverb
```

## 청취 순서

1. 기억① — 정체성 → 기억② — 결정화 목격
2. 림부스 → 림부스-칼리고 교량 → 칼리고
3. 교차로 대공동 → 정수장치 → 렌토
4. 지하심층 → 지하 사냥꾼
5. 터미너스 → 거대 거미
6. 구 폐기물 선별장 → 폐쇄 송수로 → 심층 굴착지

이 순서로 들으며 모티프 연결, 지역 구분, 장시간 반복 피로, 보스 패턴 가독성을 평가한다.

## 선별 기록

| 제목 | 후보 | 우선 확인할 항목 | 선택 |
| --- | --- | --- | --- |
| 기억① — 정체성 · 장소 연동 | A/B | 정수장치 리듬이 기억 신호로 정렬되고 다시 지역곡으로 복귀하는지 |  |
| 기억② — 결정화 목격 · 장소 연동 | A/B | 지하심층의 공백을 유지하면서 기억① 신호가 재검출되는지 |  |
| 림부스 | A/B | 손상된 각성, 반복 피로 |  |
| 림부스-칼리고 교량 · 순수 BGM | A/B + 단순 도입 A/B + 긴 반복형 A/B | 효과음 없이 파손 상태가 들리는지, 긴 반복형의 첫 40%가 충분히 단순한지, 0:19 실험안보다 1:25·1:27 후보가 구간에 적합한지 |  |
| 칼리고 | A/B | 생존 공동체의 온기, 축제 음악처럼 들리지 않는지 |  |
| 교차로 대공동 | A/B | 허브 방향감, 장시간 탐색 적합성 |  |
| 정수장치 | A/B | 퍼즐 리듬과 복구 전후 편집 가능성 |  |
| 렌토 | A/B | 3페이즈 구분과 공격 틈의 정적 |  |
| 지하심층 | A/B | 매복 예고, 공포 효과 과잉 여부 |  |
| 지하 사냥꾼 | A/B | 짧은 전투에서 리듬이 즉시 읽히는지 |  |
| 터미너스 | A/B | 하부·중부·상부의 상승 구조 |  |
| 거대 거미 | A/B | 터미너스 연속성, 지상 개방 종결부 |  |
| 구 폐기물 선별장 | A/B | 림부스 변주로 인식되는지 |  |
| 폐쇄 송수로 | A/B | 정수장치와 구별되는 수평 탐사감 |  |
| 심층 굴착지 | 재생성 대기 | 지하심층과 구별되는 독립 굴착 리듬과 후반 탐사 밀도 |  |

우선 `기억① — 정체성`과 `기억② — 결정화 목격`을 고른 뒤 나머지 곡을 판정한다. 독립적으로 좋은 곡보다 선택된 인식 신호와 연결되는 후보를 우선한다.
