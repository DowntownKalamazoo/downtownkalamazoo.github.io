# How to update the Downtown Kalamazoo website

Everything staff update day to day lives in this `content` folder. You edit it in your web browser on GitHub. There's nothing to install.

When you save (GitHub calls it **Commit changes**), the site rebuilds and publishes itself in about two minutes. You can watch it happen on the repository's **Actions** tab. A green check means it's live. A red X means something in your file needs fixing, and the site keeps showing the last good version until you fix it.

---

## Post news, a press release or a feature story

1. Open the `content/news` folder.
2. Open `_TEMPLATE.md`, select all the text, and copy it.
3. Go back to `content/news` and choose **Add file → Create new file**.
4. Name the file with the date first, then a few words: `2027-01-15-new-bakery-opens.md`
   The words become the page address: `downtownkalamazoo.us/news/new-bakery-opens.html`
5. Paste the template, then fill in the top section:
   - `title`: the headline
   - `date`: `YYYY-MM-DD`
   - `type`: **Press release**, **News**, **Feature**, or **In the news** (a story about downtown from another outlet)
   - `summary`: one or two sentences for the news list
   - `source` and `source_url`: who published it first, for press releases and outside stories
6. Write the story below the second `---` line. Leave a blank line between paragraphs.
7. Choose **Commit changes**.

**"In the news" items** only need the top section. Leave the story blank and the news list links straight to the outside article.

**To keep something private while you work on it**, add a line `draft: true` to the top section. Remove the line when it's ready.

### Formatting cheat sheet

| You type | You get |
|---|---|
| `**bold words**` | **bold words** |
| `*slanted words*` | *slanted words* |
| `## A subheading` | a subheading |
| `- an item` | a bulleted list |
| `1. a step` | a numbered list |
| `[link text](https://example.com)` | a link to another website |
| `[link text](../directory.html)` | a link to a page on this site |

### Adding a photo

1. Open the `files` folder (at the top level of the repository) and choose **Add file → Upload files**. Use a JPG under 1 MB, named simply, like `bakery-opening.jpg`.
2. In your story's top section, add:
   ```
   image: files/bakery-opening.jpg
   image_alt: The owners cut a ribbon in front of the bakery's new window.
   ```
   The `image_alt` sentence describes the photo for people who can't see it. Always include it.

---

## Add an event to the calendar

1. Open `content/events`, copy `_TEMPLATE.md`, and create a new file like `summer-concert.md`.
2. Fill in `title`, `date`, `time`, `where`, `summary` and `tags`.
3. For something that happens every month, use `repeats: first friday` (or `second`, `third`, `fourth` or `last`, plus any day) instead of `date`. Add `until:` with the last date, and `skip:` for any dates to leave out.
4. If you write a description below the second `---` line, the event gets its own page. Otherwise it links to `link`, or to nothing.

Past events drop off the calendar on their own.

**Holiday events** (Find the Holidays Downtown) are kept separately, in `holiday_content.py`. They also appear on the main calendar.

---

## Post a budget, report or other board document

1. Upload the PDF to the `files` folder, or copy its link if it's already on the City's site.
2. Open `content/documents.yml` and choose the pencil icon to edit.
3. Copy one of the entries, paste it at the top of the list, and change the title, board, kind, year and url. For an uploaded file, the url looks like `files/dega-budget-2027.pdf`.
4. Commit. It appears on the DDA & DEGA page.

The spaces at the start of each line matter in this file. Copy an existing entry and keep its spacing.

---

## Update the business directory

Small changes go in `content/directory-updates.yml`:

- **Fix a listing:** under `update:`, add the business's id (the end of its directory link, for example `directory.html#b-rustica` → `rustica`) and the fields to change: `desc`, `website`, `phone`, `address`.
- **Social District:** add or remove ids in the `social_district:` list.
- **Add a business:** copy an entry under `add:` and change it. `cat` is one of `shop`, `dine`, `arts`, `services` or `stay`.

---

## Downtown Ambassadors: monthly reports and the team

Everything on the Ambassadors page that changes lives in `content/ambassadors.yml`. The notes at the top of that file explain each field.

**Each month's report**
1. Open `files/ambassadors` and choose **Add file → Upload files**. Name the PDF `ambassador-report-YYYY-MM.pdf`, for example `ambassador-report-2026-08.pdf`.
2. Open `content/ambassadors.yml` and choose the pencil icon.
3. Under `reports:`, copy the top entry (from `- month:` down to `project_hours:`), paste it above itself, and change it:
   - `month`: `2026-08`
   - `file`: the PDF's path, `files/ambassadors/ambassador-report-2026-08.pdf`
   - `highlights`: one or two short sentences from the report's Highlights page
   - the numbers: copy them from the Total column of the report's "Stats By Zone" page (trash, recycling and litter in pounds, graffiti removed, hospitality assists, gallons of water, snow hours and special project hours)
4. Commit. The report shows up at the top of the list, and the year's totals and chart update on their own.

**Meet the Ambassadors**
- **Add someone:** under `team:`, copy an entry and change the name. `since` and `note` are optional.
- **Add a photo:** upload it to `files/ambassadors` (a JPG under 500 KB, cropped taller than wide), put its path in `photo:`, and write a short `photo_alt:` description. Until there's a photo, the card shows a brand pattern with their initials.
- **Remove someone:** delete their entry.

Check with each ambassador before posting their photo and full name. First names are fine.

---

## Season switch

When the holidays are over, open `build.py`, find `HOLIDAY_SEASON = True`, and change it to `HOLIDAY_SEASON = False`. The Holidays menu link, homepage banner and footer column go away, and the holiday pages stay online at `/holidays/`.

## Something went wrong?

Open the **Actions** tab, select the run with the red X, and read the error. It usually names the file and the line. The most common causes are a missing `---` line, a date that isn't written as `YYYY-MM-DD`, or a colon inside a title. Put the title in quotes, like `title: "Downtown: what's new"`.
