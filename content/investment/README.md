# Investing in downtown

Each building or project on the Investing in downtown page (`downtownkalamazoo.us/investment.html`) is one file in this folder. This page is for private investment: restorations, new buildings and other projects by owners and developers. Projects led by the City, the DDA or the DEGA go on the Projects page instead.

**Update one:** open its file, choose the pencil icon, change the top section, and commit.

- `kind`: a few words, like **New development**, **Historic restoration** or **Renovation**
- `status`: a few words, like **Site plan approved**, **Under construction**, **Planned** or **Complete**
- `where`: the address
- `summary`: one or two sentences
- `order`: where it appears on the page. 1 comes first.
- `links`: copy a `- text:` and `url:` pair to add a link. A page on this site, like `projects.html`, works too.
- `image` and `image_alt`: a photo or rendering, uploaded to `files` (a wide JPG under 1 MB). Always describe it in `image_alt`.

**Add one:** open `_TEMPLATE.md`, copy it, then choose **Add file → Create new file** in this folder and name it with a few words, like `edison-lofts.md`.

**Remove one:** add `draft: true` to the top section to hide it, or delete the file.

When you save (**Commit changes**), the site republishes in about two minutes. Watch for the green check on the **Actions** tab.
