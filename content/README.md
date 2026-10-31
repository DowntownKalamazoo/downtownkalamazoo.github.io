# How to update the Downtown Kalamazoo website

Everything staff update day to day lives in this `content` folder. You edit it in your web browser on GitHub. There's nothing to install.

When you save (GitHub calls it **Commit changes**), the site rebuilds and publishes itself in about two minutes. You can watch it happen on the repository's **Actions** tab. A green check means it's live. A red X means something in your file needs fixing, and the site keeps showing the last good version until you fix it.

---

## Post news, a press release or a feature story

Posts appear on the News & stories page (`news.html`) once you commit.

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
3. For an event that runs more than one day, like a weekend festival, add `end:` with the last day. It shows as one bar across those days in the month view, and under each of those days in the list.
4. For something that happens every month, use `repeats: first friday` (or `second`, `third`, `fourth` or `last`, plus any day) instead of `date`. For something weekly, use `repeats: every wednesday` (or any day). Add `starts:` with the first date, `until:` with the last date, and `skip:` for any dates to leave out. Repeating events show on the calendar up to a year ahead.
5. Write a description below the second `---` line if you have one. Every event gets its own page either way. Without a description, the page points people to `link` for details.

The calendar page has two views. **Month** shows a calendar grid (on phones, a smaller grid where people tap a day to see its events). **List** shows every event by day. Visitors switch between them, and the filter buttons come from each event's `tags`.

Past events drop off the calendar on their own.

### A series with a different lineup each night (Beats on Bates)

A series has one main file, like `beats-on-bates.md`, that sets the schedule, time, place and general description. Every date shows on the calendar right away, labeled with the series name.

When a night's lineup is set, give that night its own file:

1. In `content/events`, copy `_SERIES_NIGHT_TEMPLATE.md` and name the new file with the series and the date, like `beats-on-bates-2027-06-02.md`.
2. Fill in `series` (the main file's name, without `.md`), `date`, `title` (the lineup, like *Chris Canas Band and DJ No Limit*) and `summary`. Write about the performers below the second `---` line, and add a photo if you have one.
3. Commit.

That night gets its own page, and the calendar shows the lineup under the series name. Anything you leave out, like the time or place, comes from the main file. Change it in the night's file only if that night is different, like a rain location.

The series page lists the whole season: **Coming up** shows every date, with "Lineup to come" for nights without a file yet. **Earlier this season** keeps the nights that already happened, so the season's lineup stays on the site.

**Holiday events** (Find the Holidays Downtown) are kept separately, in `holiday_content.py`. They also appear on the main calendar.

The **Find the Holidays Downtown** page updates itself every morning from those events: **Next up** shows the next event, **Upcoming holiday events** drops dates once they pass, and **Make a day of it** features plans that go with the next events. Two settings sit near the top of `holiday_content.py`:

- `SBS_GIVEAWAY` sets the dates the "Curious? Pick an envelope." card shows beside Downtown Dollars (`show_from` and `show_until`, both included). Change the dates to move it, or set `show_until` to an earlier date than `show_from` to hide it.
- `HUB_PLAN_FALLBACK` lists the plans (by their slug from `content/itineraries.yml`) that fill the plan spots when there aren't enough upcoming events, in order.

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
- **Add a business:** copy an entry under `add:` and change it. `cat` is one of `shop`, `dine`, `arts`, `services`, `stay`, `offices` (offices & professional) or `orgs` (organizations). Offices and organizations show in the directory but not in Plan your day.

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
4. Commit. The report shows up first in the Monthly reports section, and the numbers in the ribbon under the page header update on their own.

**Hours, phone and the header photo**
These are at the top of `content/ambassadors.yml`. Change `phone:` or a line under `hours:` and commit. The call button and hours at the top of the page and the "Need something cleaned up?" box update together. To swap the group photo, upload a wide JPG under 500 KB to `files/ambassadors`, put its path in `team_photo:`, and update `team_photo_alt:` to describe it.

**Meet the Ambassadors**
- **Add someone:** under `team:`, copy an entry and change the name. `role` (for example, Operations Manager) is optional and shows under their name.
- **Add a photo:** upload it to `files/ambassadors` (a JPG under 500 KB, cropped taller than wide), put its path in `photo:`, and write a short `photo_alt:` description. Everyone with a photo appears in one line of photos. Until someone has a photo, they're listed by name under "Also on the team."
- **Remove someone:** delete their entry.

Check with each ambassador before posting their photo and full name. First names are fine.

---

## Our team page and the board list

Everything on the Our team page lives in `content/team.yml`. The notes at the top of that file explain each field. The same file holds the board list, which also appears on the DDA & DEGA page.

**Turn the page on**
The page stays hidden while the file says `draft: true`. Replace every placeholder in square brackets, like `"[Staff name 1]"`, with the real detail, then change the line to `draft: false` and commit. The page appears at `downtownkalamazoo.us/team.html`, with links from the About menu, the About page and the footer. If any `[placeholder]` is left, the Actions tab shows a red X naming it, and the site keeps the last good version.

**Staff**
- **Update someone:** change their `title`, `handles` (the "Talk to me about" lines), `email` or `phone` and commit. Each person also gets a "Save contact card" link that builds itself from these details.
- **Add a photo:** upload a JPG to `files/team` (cropped taller than wide, under 500 KB), put its path in `photo:`, and describe it in `photo_alt:`. Until then, their initials show on a brand pattern.
- **Name and pronouns:** `pronunciation` and `pronouns` are optional. Leave them as `""` to skip them.
- **Add or remove someone:** copy or delete a whole entry under `staff:`.

Check with each person before posting their photo, email and phone.

**Who to contact**
Each entry under `contacts:` is one line of the list: what people need (`need`), a short `detail`, and `who` to reach. `who` is a staff member's name written exactly as in the staff list, or one of **Downtown Ambassadors**, **DDA & DEGA page** or **Downtown team**. If someone's responsibilities change, change the name next to that line.

**The board**
Under `members:`, change a name or `role` after an appointment, and update `board_as_of:` to the month you checked. Both pages update together. Set `show_board_roster: false` to show a link to the DDA & DEGA page on the Our team page instead of the full list.

**Optional extras:** `office_hours` adds hours to the "Visit the office" box. `hiring_text` and `hiring_url` together add a "Work downtown" box.

---

## Holiday itineraries (Plan your day)

All 50 plans on the Plan your day page live in one file, `content/itineraries.yml`. Each plan makes its own page, like `downtownkalamazoo.us/holidays/plan/family-afternoon.html`, and shows up in the Plan your day filters. The notes at the top of the file explain every field.

**Change a plan:** open `content/itineraries.yml`, choose the pencil icon, find the plan by its `title`, edit it and commit.

- **Business names link on their own.** Write a name exactly as it appears in the business directory (Sarkozy Bakery, Bell's Eccentric Café) and it links to that business's listing. The plan's "Places on this plan" list, with addresses and phone numbers, fills in from those names too. Holiday events, Santa's Workshop, the Holly Jolly Trolley and Downtown Dollars link the same way.
- **To link other words**, write `[the words](gifts.html)` with a page on this site, like `gifts.html#foodie` for the Holiday Gift Guide with "the foodie" filled in.
- `budget` is one of `"Free"`, `"$"`, `"$$"` or `"$$$"`, in quotes. `who` and `days` decide which filters the plan appears under.
- `events` lists the holiday events the plan goes with. Those event pages show the plan under "Make a day of it."
- `gifts` adds a Holiday Gift Guide link under the plan's stops, already filled in: `all`, `art-lover`, `foodie`, `kids`, `host`, `stocking` or `experiences`.

**Add a plan:** copy a whole plan, from `- slug:` down to the line before the next `- slug:`, paste it at the end, and change it. Give it a new `slug` (lowercase words with dashes).

**Hide a plan:** add `draft: true` to it.

**Build your own itinerary** (`holidays/plan/build-your-own.html`) lets visitors pick their own stops from the business directory, the holiday events and a few extras like Santa's Workshop and the trolley. It updates itself when the directory or the events change. The extras are listed in `EXPERIENCES` in `itineraries.py`.

**Parking** prints at the bottom of every plan and every build-your-own itinerary. Edit it under `parking:` near the top of `content/itineraries.yml`.

**Santa's Workshop and trolley hours** are at the top of the same file, under `santa:` and `trolley:`. Each plan's "Your day" box uses them to show the hours for the date someone picks.

If a line has a `#` or a colon followed by a space, put the whole line in double quotes. If something's off, the Actions tab shows a red X that names the plan and the problem.

---

## Holiday Gift Guide

Every gift on the Holiday Gift Guide (`downtownkalamazoo.us/holidays/gifts.html`) lives in one file, `content/gift-guide.yml`. Each business is one block, with its gifts listed under it. The notes at the top of the file explain every field.

The business's name, link and Downtown Dollars tag come from the business directory, so you never type them in this file. Every business with a gift also gets an **In the Gift Guide** tag and a filter button in the directory while it's the holiday season.

**Change a gift:** open `content/gift-guide.yml`, choose the pencil icon, find the gift by its `name`, edit it and commit.

- `kind` is one of `unwrap`, `experience`, `eat-drink` or `gift-card`.
- `for` decides who it shows up for in the "I'm shopping for…" blank, like `for: [foodie, host]`. The choices are listed at the top of the file.
- `price` goes in quotes, like `price: "$24"`. The lowest dollar amount decides the budget blank. Leave it `""` until the business tells you.
- `only_in_kalamazoo: yes`, `gives_back: yes`, `stocking_stuffer: yes` and `age_21: yes` add tags and filters.

**Add a photo:**
1. Open `files/gifts` and choose **Add file → Upload files**. Any size is fine, including photos straight from a phone. The site resizes them.
2. Name the file simply, like `cherris-truffles.jpg`.
3. Under the gift, add:
   ```
   image: files/gifts/cherris-truffles.jpg
   image_alt: A box of nine truffles dusted with cocoa.
   ```
   The `image_alt` sentence describes the photo for people who can't see it. Always include it.
4. If the crop cuts off the product, add `photo_focus: top` or `photo_focus: bottom`.

Until a gift has a photo, its tag shows gift wrap in the business's directory pattern, with `wrap_label` written on it.

**Add a gift:** copy a whole gift, from `- name:` down to the line before the next `- name:`, paste it under the same business and change it.

**Add a business:** copy a whole business block, from `- business:` down to the line before the next `- business:`, and change it. `business:` is the end of its directory link: `directory.html#b-rustica` is `rustica`. For a business that isn't in the directory yet, use `name:` instead of `business:`.

**Sold out or not ready:** add `draft: true` to the gift. Remove the line to show it again.

**Waiting on details:** anything still in [square brackets] keeps a gift off the page, and so does a missing description. The Actions tab lists those in yellow, so you can see what's still missing. The site publishes either way.

**The order of the gifts changes every morning**, when the site rebuilds itself, so no business is always first.

**Links into the guide:** `holidays/gifts.html#foodie` opens the guide with "the foodie" already filled in. Any `for` choice works the same way, and so do `#experience`, `#stocking` and `#dollars`. Each plan's `gifts:` line in `content/itineraries.yml` uses these.

If something's off, the Actions tab shows a red X that names the business, the gift and the problem.

**After the holidays:** when `HOLIDAY_SEASON` changes to `False`, the directory's gift tags and filter go away on their own. Next fall, rename this year's file to `gift-guide-2026.yml` so it stays as a record, then start a new `content/gift-guide.yml` with this season's gifts. Photos in `files/gifts` can be reused.

---

## Downtown Dollars page

The numbers, the seasonal reminder and the video on the Downtown Dollars page (`downtownkalamazoo.us/dollars.html`) live in `content/dollars.yml`. The notes at the top of that file explain every field.

The list of businesses under **Where to spend them** comes from the business directory, so you never type it here. To add or remove a business, open `content/directory-updates.yml` and, under `update:`, add the business's id with `dd: true` (accepts them) or `dd: false` (doesn't). The page and the directory's Accepts Downtown Dollars tag update together.

**Update the program totals** (a few times a year)
1. Export the certificate and merchant reports from Conpoto.
2. Open `content/dollars.yml` and choose the pencil icon.
3. Change `through:` to the last month the numbers cover, then update `bought:`, `spent:` and `waiting:`. Write numbers with no $ or commas, like `392485`.
4. If they've changed, update `recipients:`, `half_spent_weeks:`, `businesses:`, `mall_share:`, `typical:` and the cents under `split:`.
5. Commit. Every number on the page, including the hero line and the four steps, updates from these.

**Add each month's numbers**
Under `months:`, copy the last line, paste it below itself, and change the month, businesses, bought and spent. Update `year_businesses:` too. At the start of a new year, change `year:`, delete the lines under `months:` and set `year_businesses: 0`.

**The "Spend them soon" reminder**
It shows under the page header only between `show_from` and `show_until`. Change the dates or the `text:` and commit. To turn it off early, set `show_until` to yesterday's date.

**Add the How it works video**
1. Open `files` and choose **Add file → Upload files**, then upload into a `dollars` folder: the video (an MP4 under 50 MB), a still image for before it plays (a 16:9 JPG), and the captions file (`.vtt`).
2. In `content/dollars.yml`, fill in `file:`, `poster:` and `captions:` with those paths, for example `files/dollars/how-downtown-dollars-work.mp4`.
3. Paste everything said and shown in the video under `transcript:`.
4. Commit. The video appears beside the How it works steps. It never plays on its own.

Captions and a transcript are required. If either is missing, or a file path is misspelled, the Actions tab shows a red X that says what to fix.

**Privacy:** only program-wide totals go on this page. Never add a single business's total, a ranking, a single order, or anything that could point to who bought or spent what. Keep the Conpoto exports off GitHub; they include names, emails and active certificate codes.

---

## Placemaking projects

Each project on the Placemaking page is one file in `content/placemaking`. Each file makes its own page, for example `downtownkalamazoo.us/placemaking/rose-street-plaza.html`. The same instructions are in `content/placemaking/README.md`.

**Update a project** (new funding, a construction date, a photo): open its file, choose the pencil icon, change the top section, and commit.

- `lead`: who leads it: **DEGA**, **DDA**, **DDA & DEGA** or **City**, written exactly like that
- `funding`: **Fully funded**, **Partially funded** or **Seeking funding**, written exactly like that
- `stage`: a few words, like **In design**, **Construction approved**, **Under construction** or **Complete**. Leave it blank if there's nothing to say yet.
- `where`, `timeline`, `design`: plain sentences. Blank ones are left off the page.
- `order`: where it appears on the Placemaking page. 1 comes first.
- `links`: copy a `- text:` and `url:` pair to add a link. For a PDF you uploaded to `files`, the url looks like `files/rose-street-plaza-design.pdf`.
- `image` and `image_alt`: a photo or rendering for the top of the page, uploaded to `files` (a wide JPG under 1 MB). Always describe it in `image_alt`.

Write the project description below the second `---` line, the same way as a news story.

**Add a project:** open `_TEMPLATE.md`, copy it, then choose **Add file → Create new file** in `content/placemaking`. Name it with a few words, like `exchange-alley.md`. The overview counts update on their own.

**Hide a project while you work on it:** add `draft: true` to the top section.

## Investing in downtown (private investment)

Each building or project on the Investing in downtown page (`downtownkalamazoo.us/investment.html`) is one file in `content/investment`. This page is for private investment: restorations, new buildings and other projects by owners and developers. Projects led by the City, the DDA or the DEGA go on the Projects page instead.

**Update one:** open its file, choose the pencil icon, change the top section, and commit.

- `kind`: a few words, like **New development**, **Historic restoration** or **Renovation**
- `status`: a few words, like **Site plan approved**, **Under construction**, **Planned** or **Complete**
- `where`: the address
- `summary`: one or two sentences
- `order`: where it appears on the page. 1 comes first.
- `links`: copy a `- text:` and `url:` pair to add a link. A page on this site, like `projects.html`, works too.
- `image` and `image_alt`: a photo or rendering, uploaded to `files` (a wide JPG under 1 MB). Always describe it in `image_alt`.

**Add one:** open `_TEMPLATE.md`, copy it, then choose **Add file → Create new file** in `content/investment` and name it with a few words, like `edison-lofts.md`.

**Remove one:** add `draft: true` to the top section to hide it, or delete the file.

**Projects page cards** (Arcadia Creek, Streets for All and the others) are grouped by who leads them. Each card's `lead=` in `yearround_section.py` is `'DEGA'` or `'City'`.

The Find your space box on the For businesses page counts these projects and links here.

---

## For businesses page

Everything on the For businesses page (`downtownkalamazoo.us/businesses.html`) lives in `content/business-resources.yml`. The notes at the top of that file explain each field. The file has six parts, in the order they appear on the page: `stats`, `tools`, `resources`, `develop`, `research` and `partners`.

**Change something:** open `content/business-resources.yml`, choose the pencil icon, find the entry by its name or title, edit it and commit.

**Add an organization or program:** copy a whole entry, from `- name:` down to its `checked:` line, paste it below the others and change it.
- `what` is one or two plain sentences. `for` says who it's for, if it's for a particular group.
- `cost: "Free"` adds a Free tag.
- `needs` decides which "What do you need?" buttons show it: `start`, `funding`, `advice`, `network`, `space`, `permits`, `customers` or `hiring`. Use as many as fit, like `needs: [start, advice]`.
- Leave `url: ""` blank for a group with no website. The card then shows the downtown team's email.

**Developer resources** go under `develop:` in the same format, without `needs`. **Plans and studies** go under `research:`. For a PDF you uploaded, the url looks like `files/downtown-plan-2027.pdf`.

**Stats:** every number needs a `source`. A stat waiting on a source keeps `draft: true` and stays off the page. When you find the source, fill in `source`, `source_url` and `as_of`, then delete the `draft: true` line.

**Hide something for now:** add `draft: true` to it.

**Keep it current:** each entry has a `checked:` month, like `checked: 2026-10`. Once a year, open each link, confirm the details and update the month. Entries not checked in 12 months show a yellow warning on the Actions tab. The site still publishes.

If a line has a colon followed by a space, put the whole value in double quotes. If something's off, the Actions tab shows a red X that names the entry and the problem.

---

## Switching pages on and off

Some parts of the site can be turned on or off. Their content stays in the repository either way, so nothing is lost. Open `build.py` and find these lines near the top. News is on; the other three are off for now:

```
SHOW_NEWS = True
SHOW_HISTORY = False
SHOW_ACCESS_GUIDE = False
SHOW_ACCOMMODATION = False
```

- `SHOW_NEWS`: the News & stories page and every post in `content/news`
- `SHOW_HISTORY`: the History of downtown page
- `SHOW_ACCESS_GUIDE`: the Accessible downtown guide
- `SHOW_ACCOMMODATION`: the "Need an accommodation?" box on event, plan and Visit pages

To turn one on, change `False` to `True` and commit. To turn one off, change `True` to `False`. Its menu, footer and page links come back with it.

## Facebook and Instagram

The links in the footer and on the About page come from `SOCIAL` near the top of `build.py`. Change an address there and commit. To add another account, copy a line and change the name and address.

## Season switch

When the holidays are over, open `build.py`, find `HOLIDAY_SEASON = True`, and change it to `HOLIDAY_SEASON = False`. The Holidays menu link, homepage banner and footer column go away, and the holiday pages stay online at `/holidays/`.

## Something went wrong?

Open the **Actions** tab, select the run with the red X, and read the error. It usually names the file and the line. The most common causes are a missing `---` line, a date that isn't written as `YYYY-MM-DD`, or a colon inside a title. Put the title in quotes, like `title: "Downtown: what's new"`.
