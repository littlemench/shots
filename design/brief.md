# Shots — Product Brief

*Draft v0.1 · 2026-09-25*

## Vision
A tool for simpler, more seamless, practical and joyful exploration of photography. The focus is on showing the work and letting people find their way through it using more interesting criteria than the usual date and album.

Built for one photographer first (me), and released as open-source code others can run for themselves.

## Principles
1. **Photos first, interface second.** The brand comes through how pages are built and how images are treated, not through decoration.
2. **Meaningful discovery.** Filters describe what a photo *is* and *feels like*, not only when it was filed.
3. **Assisted, not manual.** The studio does most of the tagging work and the photographer refines it.
4. **Generous by default.** Hi-res downloads are free, with credit made easy and donating optional.

---

## 1. Gallery (audience experience)
Exploring one photographer's body of work.

### Filters: initial set
| Facet | Example values | Source |
|---|---|---|
| Camera | Leica M6, Fuji X100V | EXIF (digital), manual/roll-level (film) |
| Film stock | Portra 400, HP5+ | Manual, set per roll or batch |
| Orientation | Landscape, portrait, square | Automatic (dimensions) |
| Nature of shot | Built environment, nature, people, graphic, sport | AI-suggested, then confirmed |
| Dominant hue | Blue, red, warm, cool, monochrome | Automatic (colour extraction) |

### Filters: suggested additions (for discussion)
- **Colour vs black & white.** Automatic, and more useful than hue alone for monochrome work.
- **Light / time of day.** Golden hour, night, overcast, harsh midday.
- **Place.** City or region. Needs care with GPS privacy.
- **Year / era.**
- **Lens / focal length.** Wide, normal, tele. EXIF for digital, manual for film.
- **Format / aspect.** 35mm, 6x6, 6x7, panoramic.
- **Mood.** Quiet, busy, playful. Subjective, so possibly a later addition.

### Layout (from wireframe `design/wireframes/gallery-v1.webp`)
- **Stage:** a large featured image, full width with rounded corners. Logo top-left, filter pills overlaid top-right, download bottom-left, prev/next bottom-right.
- **Grid:** 3 columns of rounded thumbnails below the stage. The current photo has an outline.
- **Filters in the wireframe:** Albums, Locations, Types, Cameras, Colours.

### Gallery decisions (2026-09-25)
- **Opening a thumbnail** opens a fullscreen viewer on every screen size.
- **Grid:** uses flexible rows. Landscape tiles take one row and portrait tiles take two (double height).
- **Logo and filters** sit inside the hero, over the photo, as in the wireframe. On scroll they **stay pinned in place with no bar behind them**. The logo is white only while the hero is behind it. Over the grid it switches to the same frosted glass as the pills, cut to the logo's shape, so it blends in with the photos.
- **Titles are never shown.** They stay in the data and are used only for alt text and screen-reader labels. On screen, photos are identified by location and year, and the credit line reads "Photo by …".
- **Filter behaviour:** multi-select within a filter and combined across filters. Counts are shown, options with no results are disabled, and there's a *clear all*. The filter state and open photo are stored in the URL.
- **Dropped:** film stock and orientation filters.
- **ⓘ info panel:** shows the photo's tags, and each tag is clickable to show every photo that shares it.
- **Spacing:** the page margin (top and sides) matches the gap between thumbnails: 14px on desktop, 8px on mobile.
- **Random hero on load:** every visit opens on a random photo. If the link includes filters, it's chosen from within them. A link to a specific photo (`?photo=`) still opens that photo.
- **Random button:** a frosted shuffle button sits to the left of the filters. It picks a random photo for the hero from the current filtered results, never repeating the one showing, and scrolls back up to the hero if needed. Keyboard shortcut: `r`.
- **Hero corners** use the same radius as the thumbnails (14px desktop, 10px mobile).
- **Rounded corners:** thumbnails and stage are slightly clipped, but downloads are always uncropped.
- **Narrower screens (under 1100px):** a single Filter button opens a sheet and shows the matching shot count, e.g. `3 filters (5)`, or `Filters (43)` when nothing is selected. On wide screens the count sits in brackets after the pills. The viewer supports swipe.
- **Keyboard:** ← → move between photos, Esc closes, `i` toggles info, `d` opens download, `f` toggles fullscreen. This works on both the stage and the viewer.

### Visual direction (from `design/references/`)
- A dark, cinematic base. Controls are thin outlines, frosted glass or light pills, so the image carries the colour.
- Controls have no outlines. They're filled with frosted glass instead.
- Icons come from [pixelarticons](https://pixelarticons.com) (MIT licence), sized in multiples of 6px so the pixels stay crisp.
- Type: a single family, Geist. Body text is Regular (400); headings are Medium (500) with slightly tighter letter spacing (-0.02em). There's no serif.
- The photo in focus on the stage fills the whole container, edge to edge, with a soft gradient at the bottom so the controls stay readable. The fullscreen viewer still shows the whole, uncropped photo.

### Brand identity
- **Direction:** a wordmark only, with no separate logo or brand mark. A subtle photographic easter egg is built into the letters, and that detail can double as the favicon.
- **Explorations:** `design/logo/wordmarks.html` (the current direction) and `design/logo/routes.html` (the earlier mark, wordmark and lockup routes).

### Real photos (2026-09-28)
- 938 film scans in `design/sample-photos/` (gitignored). The file metadata is the lab scanner's, not the camera's. There are no dates and no GPS, so **folder names are the metadata source**.
- **Folder rules:**
  - camera → Camera (Nikon FM, Olympus Mju II, Polaroid 340AF, Zenit 11)
  - the remaining title → Album. This is shown in the info panel, but it's **not a filter** (removed 2026-09-30).
  - a 4-digit year → Year
  - a place name → Location
  - `B&W` in the name or as a subfolder → Black & white
  - numbered roll subfolders merge into the parent album
  - `Test` folders are skipped, and accidental duplicates are removed
- **Suggestions review:** `sample-photos/_shots-review.json` holds per-photo rotation, types, hidden and status ("suggested"). This is the prototype of Studio's review step.
- **Web copies:** `prototype/photos/` (gitignored). `_data.js` is generated from folder names plus the review file.
- **Studio needs this surfaced:** rotation fixes (labs often scan portrait frames as landscape), blank or fogged frames to hide, a per-album publish switch, and editable album names.

### Prototype
`design/prototype/gallery.html`. Run the `prototype` launch config, or serve that folder and open `/gallery.html`. The placeholder photos come from picsum.photos with illustrative metadata. Dominant colours were calculated from the actual pixels.

### Downloads
- Free hi-res download for every shot.
- Optional donation prompt at download time. Links out to an external service (Ko-fi, Stripe Payment Link, etc.). No payments are handled in-app.
- Credit information with a one-click copy: photographer name, title, link, licence.
- **Open question:** which licence? (e.g. CC BY 4.0, or custom terms.)

### Future: conversational search
Visitors describe what they want ("quiet blue streets at dusk") and the tool surfaces the most relevant shots. The tag model should be designed now so it can support this later: structured tags, plus a free-text description per photo.

---

## 2. Studio (photographer experience)
Getting photos in and making them discoverable. *To be designed collaboratively.*

### Ingest
- v1: link a folder (e.g. Google Drive) as the source, rather than hosting uploads.
- Later: direct upload / other storage.
- **Open question:** Drive works for personal use, but open-source users may prefer a local folder or S3-compatible storage. Worth building a storage abstraction early.

### Assisted tagging
- On ingest, extract what's knowable automatically (EXIF, orientation, hue, colour/B&W).
- Suggest subjective tags (nature of shot, light, mood) using a vision model, mapped to the same facets the gallery filters on.
- The photographer reviews suggestions, then accepts, edits or rejects them. Tags have a *suggested* vs *confirmed* state.
- Batch actions for things shared across a set, e.g. applying camera + film stock to a whole roll.

---

## Inputs pending
- [ ] Gallery wireframe → `design/wireframes/`
- [ ] Aesthetic references → `design/references/`
- [ ] Top frustrations with Flickr (design anti-principles)
- [ ] "More interesting criteria" — further thoughts

### Curated library (2026-10-02)
- **Source:** `design/photos/` (gitignored), processed by `tools/process_photos.py`.
- **Photo ids** come from file contents, so renaming or moving folders keeps rotations and tags.
- **Duplicates skipped automatically:** exact copies, near-identical frames, and copies scanned at a different rotation. Originals win over `name(1).jpg` copies.
- **Locations have two tiers, Country › Place:** e.g. Spain › Mallorca. Choosing a country includes all its places. Folders that name only a country (e.g. Greece) get no place.
- **Public album names** can be overridden in the tool (e.g. employer references removed).
- **Result:** 1,078 photos. Every photo has suggested types and has been checked for rotation (status "suggested", awaiting your review).
