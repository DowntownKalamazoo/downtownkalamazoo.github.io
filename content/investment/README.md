# Private investment

Each building or project by a private owner or developer is one file in this folder. It shows as a card, with the diamond marker, on the Projects page (`downtownkalamazoo.us/projects.html`). Projects led by the City, the DDA or the DEGA go in `content/projects` or `content/placemaking` instead.

**Update one:** open its file, choose the pencil icon, change the top section, and commit.

- `progress`: **Planning**, **Approved**, **Under construction** or **Finished**, written exactly like that. This decides which section of the Projects page the card is in.
- `next`: one short line at the bottom of the card, like `"Opens: fall 2027"`. Keep the quotation marks.
- `finished`: the year it finished, like `2025`. Projects that finished this year or last year get a full card; older ones go in the Finished since 2016 list.
- `kind`: the label on the card's pattern band, like **New development**, **Historic restoration** or **Renovation**
- `pattern`: which brand pattern fills the band: arcs, confetti, dashes, dots, loops, maze, pinstripes, quilt, speckle, squiggle, stripes or waves
- `status`: a few words, like **Site plan approved**. It shows at the bottom of the card only when `next` is blank.
- `where`: the address
- `summary`: one or two sentences
- `order`: the order within its section. 1 comes first.
- `links`: copy a `- text:` and `url:` pair to add a link. A page on this site, like `projects.html`, works too.
- `image` and `image_alt`: a photo or rendering, uploaded to `files` (a wide JPG under 1 MB), replaces the pattern band. Always describe it in `image_alt`.

**Add one:** open `_TEMPLATE.md`, copy it, then choose **Add file → Create new file** in this folder and name it with a few words, like `edison-lofts.md`.

**Remove one:** add `draft: true` to the top section to hide it, or delete the file.

When you save (**Commit changes**), the site republishes in about two minutes. Watch for the green check on the **Actions** tab.
