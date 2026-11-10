# V3.2 interaction refinement — acoustic receipts and scaled listening reach

**Scope:** Interface/visual-encoding refinement in `docs/previews/v3-2-listener-reach/index.html`. No source observations, MusicBrainz recording identities, training features, acoustic clustering, weights, favourite selections, albums or personal *Home* finale were modified.

## Movement and brightness. *Not mood.*

- **Hover or keyboard focus:** a compact contextual receipt for the selected bubble shows the song title, studio album, release year, archive source category (lossless-/lossy-tagged), the current horizontal and vertical *measured* descriptor labels and exact source values in their original units.
- **Click/tap or Enter/Space:** preserves selection and opens the detailed **selected recording** receipt below the plot. It describes each descriptor's signed difference from the median and the percentage of **currently displayed source recordings** below that value. Medians, cohort ranks and axis labels recalculate when switching descriptors or the 147/103-recording cohort.
- The receipt links to the selected acoustic recording's MusicBrainz identifier. These observations describe the **archival candidate recording**, not verified original studio masters and not the mood evoked by the music.
- On narrow mobile screens, floating hover popovers are suppressed so they cannot obscure the plot; tapping a measured point or a favourite shortcut keeps the persistent evidence receipt available.
- Personal favourite gold outlines, *Home* red anchor and missing-song disclosures remain unchanged. Unmeasured songs are never given synthetic coordinates.

## Different eras. *Shared sonic DNA.*

The acoustic tree **never moves** when changing listener measures. The *outer ring only* is revised:

- Longer radial bars map a per-recording measured count from **12 to 110 SVG units** (previously ~5 to 56 units). A larger SVG viewBox prevents clipping.
- **Length:** preserves a `log1p` transformation of the chosen raw ListenBrainz count, with the observed low and high values mapped to the new displayed interval. Exact values are visible in the selected recording panel.
- **Colour:** five ordered, restrained cool-to-warm hues encode **quintile of reported counts across the displayed 147-recording snapshot**. This is a redundant cue alongside length, not a third independent metric. Gradients from muted to category colour visually emphasize bar endpoints. The gradient legend identifies lower/mid/higher reference counts and updates when switching between unique listeners and total listens.
- **Exceptions:** the three **alternate album-version recording IDs** for *Home*, *Personal Jesus*, and *The Bottom Line* remain visibly blue and dashed to distinguish identity proxies. Their lengths still use their actual *alternate-ID* counts. Original selected-MBID nulls remain null.
- **Hide overlay:** removes the radial reach bars and legend without affecting the inner dendrogram.

The listening values are ListenBrainz recording-level popularity observations, **not** worldwide audience, concert performances, or a measurement of artistic significance. The colour bands should not be interpreted as statistically meaningful categories or emotion ratings.

## QA and provenance

Local Chromium checks at 1440px and 390px covered bubble focus and keyboard selection, persistent receipts, descriptor switching, the 147 radial bars (144 gradients + 3 dashed blue proxies), all five reach quintiles, longer bar lengths, all three mode buttons, absence of JS exceptions, no document-level overflow and unchanged data payloads.

The repo's `test_v32_listener_reach.py` continues to check the source counts, selected-MBID missingness, acoustic source/album integrity and 144+3 alternate-recording separation, plus regression assertions for these interactions.

**Locked baselines:** V3.0 and V3.1 research editions remain separate, and the V2.9 original archive is unchanged.
