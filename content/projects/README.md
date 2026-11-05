# City, DDA and DEGA projects

Each file in this folder is one card on the Projects page (`downtownkalamazoo.us/projects.html`): projects led by the City, the DDA or the DEGA that aren't placemaking. Placemaking projects go in `content/placemaking`, and private investment goes in `content/investment`.

**Move a project to a new stage:** open its file, choose the pencil icon, and change `progress` to **Planning**, **Approved**, **Under construction** or **Finished**, written exactly like that. Update `next` (the short line at the bottom of the card, like `"Finishes: November 2026"`) and, once it's done, add the year to `finished`.

The other lines:

- `lead`: **DEGA**, **DDA**, **DDA & DEGA** or **City**, written exactly like that
- `where` and `summary`: the area, and one or two plain sentences
- `kind`: the label on the pattern band, like **Streets** or **Getting around**
- `pattern`: arcs, confetti, dashes, dots, loops, maze, pinstripes, quilt, speckle, squiggle, stripes or waves. Leave it blank to have one picked for you.
- `order`: the order within its section. 1 comes first.
- `links`: copy a `- text:` and `url:` pair to add a link
- `page` and `page_label`: a page on this site to link to, like `waste-recycling.html`
- `news`: the file name of a related news story, without `.md`
- `image` and `image_alt`: a photo, uploaded to `files`, replaces the pattern band. Always describe it in `image_alt`.

**Add one:** open `_TEMPLATE.md`, copy it, then choose **Add file → Create new file** in this folder and name it with a few words, like `bates-alley-lighting.md`.

**Hide one:** add `draft: true` to the top section.

When you save (**Commit changes**), the site republishes in about two minutes. Watch for the green check on the **Actions** tab.
