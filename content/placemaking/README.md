# Placemaking projects

Each placemaking project is one file in `content/placemaking`. It shows as a card on the Projects page (`downtownkalamazoo.us/projects.html`) and makes its own page, for example `downtownkalamazoo.us/placemaking/rose-street-plaza.html`.

**Update a project** (new funding, a construction date, a photo): open its file, choose the pencil icon, change the top section, and commit.

- `progress`: **Planning**, **Approved**, **Under construction** or **Finished**, written exactly like that. This decides which section of the Projects page the card is in.
- `next`: one short line at the bottom of the card, like `"Finishes: November 2026"`. Keep the quotation marks.
- `finished`: the year it finished, like `2027`, once it's done.
- `pattern`: which brand pattern fills the card's band: arcs, confetti, dashes, dots, loops, maze, pinstripes, quilt, speckle, squiggle, stripes or waves.
- `lead`: who leads it: **DEGA**, **DDA**, **DDA & DEGA** or **City**, written exactly like that
- `funding`: **Fully funded**, **Partially funded** or **Seeking funding**, written exactly like that
- `stage`: shown on the project's own page. A few words, like **In design**, **Construction approved**, **Under construction** or **Complete**. Leave it blank if there's nothing to say yet.
- `where`, `timeline`, `design`: plain sentences. Blank ones are left off the page.
- `order`: the order within its section of the Projects page. 1 comes first.
- `links`: copy a `- text:` and `url:` pair to add a link. For a PDF you uploaded to `files`, the url looks like `files/rose-street-plaza-design.pdf`.
- `image` and `image_alt`: a photo or rendering for the top of the page, uploaded to `files` (a wide JPG under 1 MB). Always describe it in `image_alt`.

Write the project description below the second `---` line, the same way as a news story.

**Add a project:** open `_TEMPLATE.md`, copy it, then choose **Add file → Create new file** in `content/placemaking`. Name it with a few words, like `exchange-alley.md`. The Projects page counts update on their own.

**Hide a project while you work on it:** add `draft: true` to the top section.

When you save (**Commit changes**), the site republishes in about two minutes. Watch for the green check on the **Actions** tab.
