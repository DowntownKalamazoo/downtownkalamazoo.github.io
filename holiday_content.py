"""Site content. Facts come from City of Kalamazoo pages, the Holly Jolly Trolley / Santa site,
the Arts Council of Greater Kalamazoo, Discover Kalamazoo and WWMT coverage. Where a 2026 detail
is not yet public, the copy says so rather than guessing."""

LIBRARY_URL = 'https://claude.ai/artifact/CrW3UDwfafXpXLAMtDEwms'

TBA = 'To be announced'
BRONSON = 'Bronson Park, 200 S. Rose St.'
TROLLEY_TIP = 'The free Holly Jolly Trolley runs Thursday through Sunday, so it’s a warm way to hop between stops.'

EVENTS = [
    dict(slug='first-friday-nov', title='First Friday & Art Hop', short_title='Art Hop (Nov 6)', footer=False,
         date='2026-11-06', fill='f-blue', eyebrow='Friday, November 6, 2026',
         when_short='Fri, Nov 6 · Evening', where_short='Galleries and shops downtown', when_long='Friday, November 6 · Evening',
         summary='Downtown shops, galleries and studios open their doors to show work by local artists.',
         plain='On the first Friday of November, shops and galleries downtown show art by local artists. It is free to walk around and look.',
         glance=[('When', 'Friday, November 6<br>Evening'), ('Where', 'Galleries, shops and studios across downtown'), ('Cost', 'Free to browse'), ('Hosted by', 'Arts Council of Greater Kalamazoo')],
         body=['Art Hop is the Arts Council of Greater Kalamazoo’s monthly evening of open doors. On the first Friday of the month, businesses across downtown host local artists, so you can see paintings, photography, jewelry and glasswork while you shop and eat.',
               'November’s hop lands just before the holiday rush, which makes it a good night to find one-of-a-kind gifts made in Kalamazoo.'],
         highlights=['Work by local artists in shops, galleries and studios', 'A walkable route across downtown', 'Gifts you won’t find anywhere else'],
         tips=['The Arts Council publishes each month’s list of venues and hours before the hop.', 'Start on the Kalamazoo Mall, where many venues are a short walk apart.'],
         links=[('Arts Council of Greater Kalamazoo', 'https://www.kalamazooarts.org')],
         plans=['friday-night', 'arts-evening'], biz=False),

    dict(slug='moms-in-the-zoo', title='Moms in the Zoo', short_title='Moms in the Zoo', footer=False,
         date='2026-11-14', fill='f-pink', eyebrow='Saturday, November 14, 2026',
         when_short='Sat, Nov 14 · Time to be announced', where_short='Downtown Kalamazoo', when_long='Saturday, November 14 · Time to be announced',
         summary='A Saturday downtown planned with moms in mind. Full details are coming soon.',
         plain='Moms in the Zoo is on Saturday, November 14. The times and places are not posted yet.',
         glance=[('When', 'Saturday, November 14<br>Time to be announced'), ('Where', 'Downtown Kalamazoo'), ('Cost', TBA), ('Hosted by', 'Downtown Kalamazoo')],
         body=['Moms in the Zoo is on the downtown holiday calendar for Saturday, November 14. Hours, locations and participating businesses will be posted here as soon as they are confirmed.',
               'While you wait, it’s a good weekend to get a head start on holiday shopping before the parade crowds arrive the following Saturday.'],
         note='Details for this event are still being finalized. Check back soon.',
         plans=['shop-small', 'under-50'], biz=True),

    dict(slug='holiday-parade', title='Fox Motors Maple Hill Holiday Parade', short_title='Holiday Parade', footer=True,
         date='2026-11-21', fill='f-red', eyebrow='Saturday, November 21, 2026',
         when_short='Sat, Nov 21 · Late morning', where_short='Rose St., Michigan Ave. and Lovell St.', when_long='Saturday, November 21 · Late morning',
         summary='Marching bands, giant balloons and floats roll through downtown in one of Kalamazoo’s longest-running traditions.',
         plain='The holiday parade goes through downtown on Saturday, November 21. There are bands, big balloons and floats. It is free to watch.',
         glance=[('When', 'Saturday, November 21<br>Last year’s parade began at 11 a.m.'), ('Where', 'Downtown, starting and ending at Portage and Lovell streets'), ('Cost', 'Free to watch'), ('Presented by', 'Fox Motors Maple Hill')],
         body=['Gilmore Department Store started Kalamazoo’s holiday parade in 1962, and it has opened the season downtown ever since. The 2026 parade is the 64th, and it typically draws close to 30,000 people to the curb.',
               'Expect high school marching bands, giant balloons, floats and groups from across the community. When the last float passes, head to the Kalamazoo Mall for the <a href="{R}events/after-parade.html">After Parade Activities</a>.'],
         route=['Portage and Lovell streets to Rose Street', 'North on Rose Street to Michigan Avenue', 'East on Michigan Avenue to Pitcher Street', 'South on Pitcher Street to Lovell Street', 'West on Lovell Street back to Portage Street'],
         tips=['Arrive early for a curbside spot, and bring layers and a blanket.', 'Expect road closures along the route from mid-morning into the afternoon.', 'The 2026 start time and route will be confirmed by the parade organizers.'],
         links=[('Kalamazoo Holiday Parade', 'https://www.kalamazooholidayparade.org'), ('City of Kalamazoo parade page', 'https://www.kalamazoocity.org/Community/Events-Meetings/Maple-Hill-Holiday-Parade-Activities')],
         plans=['family-afternoon', 'under-50'], biz=True),

    dict(slug='after-parade', title='After Parade Activities', short_title='After Parade Activities', footer=False,
         date='2026-11-21', fill='f-green', eyebrow='Saturday, November 21, 2026',
         when_short='Sat, Nov 21 · After the parade', where_short='Kalamazoo Mall', when_long='Saturday, November 21 · Right after the parade',
         summary='When the last float passes, the celebration moves to the Kalamazoo Mall, where shops and organizations host holiday activities.',
         plain='After the parade, walk to the Kalamazoo Mall. Shops and groups have holiday activities there.',
         glance=[('When', 'Saturday, November 21<br>Right after the parade'), ('Where', 'Kalamazoo Mall'), ('Cost', 'Free to attend'), ('Hosted by', 'Downtown retailers, businesses and organizations')],
         body=['Downtown retailers, businesses and organizations host special events along the Kalamazoo Mall after the parade to mark the start of the holiday season.',
               'It’s the easiest way to keep the parade-day energy going: warm up indoors, get a first look at holiday windows, and grab lunch downtown.'],
         note='The list of participating businesses and activities will be posted here before parade day.',
         tips=['Walk over from the parade route, and leave the car parked.', 'Bring the kids’ wish lists. Santa’s Workshop opens one week later.'],
         plans=['family-afternoon', 'shop-small'], biz=True),

    dict(slug='tree-lighting', title='Tree Lighting Ceremony', short_title='Tree Lighting', footer=True,
         date='2026-11-27', fill='f-green', eyebrow='Friday, November 27, 2026',
         when_short='Fri, Nov 27 · Time to be announced', where_short='Bronson Park', when_long='Friday, November 27 · Time to be announced',
         summary='The City of Kalamazoo lights up Bronson Park to open the season, celebrating the holidays and the many traditions people bring to them.',
         plain='On the Friday after Thanksgiving, the city lights the holiday tree in Bronson Park. Everyone is welcome.',
         glance=[('When', 'Friday, November 27<br>Time to be announced'), ('Where', BRONSON), ('Cost', 'Free and open to the public'), ('Hosted by', 'City of Kalamazoo')],
         body=['The City of Kalamazoo’s annual Tree Lighting Ceremony fills Bronson Park the night after Thanksgiving. It celebrates the holiday season and the many traditions that come with it.',
               'Stay downtown afterward. The next morning is Small Business Saturday, and Santa’s Workshop opens at City Centre.'],
         links=[('City of Kalamazoo holiday events', 'https://www.kalamazoocity.org/Community/Events-Meetings/Holiday-Events')],
         plans=['family-afternoon', 'under-50'], biz=False),

    dict(slug='small-business-saturday', title='Small Business Saturday & Santa’s Workshop', short_title='Small Business Saturday', footer=False,
         date='2026-11-28', fill='f-pink', eyebrow='Saturday, November 28, 2026',
         when_short='Sat, Nov 28 · All day', where_short='Kalamazoo Mall and City Centre', when_long='Saturday, November 28 · All day',
         summary='Shop downtown’s locally owned businesses on the biggest small-business day of the year, and visit Santa as his workshop opens.',
         plain='On November 28, shop at local stores downtown. Santa’s Workshop opens that day and visiting Santa is free.',
         glance=[('When', 'Saturday, November 28<br>Shops open all day'), ('Where', 'Kalamazoo Mall; Santa at City Centre, 125 S. Kalamazoo Mall'), ('Cost', 'Free to visit Santa'), ('Hosted by', 'Downtown Kalamazoo businesses')],
         body=['Small Business Saturday is the day after Black Friday set aside for local shops, and downtown Kalamazoo is the place to do it. Make your list, then work your way down the Kalamazoo Mall.',
               'Santa’s Workshop opens at City Centre, 125 S. Kalamazoo Mall, just past the City Center Market and Deli. Visits are free, and there are photo backdrops, so bring a camera. See the <a href="{R}sbs.html">Small Business Saturday page</a> for shopping ideas.'],
         hours_caption='Santa’s Workshop hours from last season (2026 hours to be confirmed)',
         hours=[('Thursdays and Fridays', '5 to 8 p.m.'), ('Saturdays', 'Noon to 6 p.m.'), ('Sundays', 'Noon to 4 p.m.'), ('Christmas week', 'Evenings, then noon to 4 p.m. on Christmas Eve')],
         links=[('Santa’s Workshop and Holly Jolly Trolley', 'https://www.downtownkalamazoosanta.com'), ('Small Business Saturday downtown', 'sbs.html'), ('Downtown Dollars', 'dollars.html')],
         plans=['shop-small', 'family-afternoon'], biz=True),

    dict(slug='first-friday-dec', title='First Friday & Art Hop', short_title='Art Hop (Dec 4)', footer=False,
         date='2026-12-04', fill='f-blue', eyebrow='Friday, December 4, 2026',
         when_short='Fri, Dec 4 · Evening', where_short='Galleries and shops downtown', when_long='Friday, December 4 · Evening',
         summary='December’s Art Hop pairs local art with holiday windows. It’s a good night to find a handmade gift.',
         plain='On the first Friday of December, shops and galleries downtown show art by local artists. Many pieces make good gifts.',
         glance=[('When', 'Friday, December 4<br>Evening'), ('Where', 'Galleries, shops and studios across downtown'), ('Cost', 'Free to browse'), ('Hosted by', 'Arts Council of Greater Kalamazoo')],
         body=['The Arts Council of Greater Kalamazoo’s Art Hop turns downtown into a walkable gallery on the first Friday of every month.',
               'In December the hop doubles as a holiday market of sorts: local artists’ paintings, prints, jewelry and glasswork make memorable gifts, and the shops hosting them are lit up for the season. Santa’s Workshop is open Friday evenings too.'],
         highlights=['Local art in shops, galleries and studios', 'Handmade, one-of-a-kind gifts', 'Holiday windows along the Kalamazoo Mall'],
         links=[('Arts Council of Greater Kalamazoo', 'https://www.kalamazooarts.org')],
         plans=['friday-night', 'arts-evening'], biz=True),

    dict(slug='gingerbread-wonderland', title='Gingerbread Wonderland', short_title='Gingerbread Wonderland', footer=True,
         date='2026-12-05', end='2026-12-21', fill='f-pink', eyebrow='December 5 to 21, 2026',
         when_short='Dec 5–21', where_short='Downtown Kalamazoo', when_long='Saturday, December 5 to Monday, December 21',
         summary='Gingerbread creations fill downtown for two and a half weeks of the season.',
         plain='From December 5 to 21, gingerbread creations are on display downtown. Places and hours are not posted yet.',
         glance=[('When', 'December 5 to 21'), ('Where', 'Downtown Kalamazoo; locations to be announced'), ('Cost', TBA), ('Hosted by', 'Downtown Kalamazoo')],
         body=['Downtown has a sweet tradition: local businesses and organizations have built gingerbread houses for the holidays for several years running.',
               'Gingerbread Wonderland brings gingerbread creations to downtown from December 5 to 21. Display locations, viewing hours and the list of builders will be posted here when they are confirmed.'],
         note='Locations and hours are still being finalized.',
         plans=['family-afternoon', 'under-50'], biz=True),

    dict(slug='december-to-remember', title='December to Remember', short_title='December to Remember', footer=False,
         date='2026-12-10', fill='f-red', eyebrow='Thursday, December 10, 2026',
         when_short='Thu, Dec 10 · Time to be announced', where_short='Bronson Park', when_long='Thursday, December 10 · Time to be announced',
         summary='A free night of holiday cheer, hot cocoa and activities in Bronson Park.',
         plain='On December 10 there is a free holiday party in Bronson Park with hot cocoa and activities.',
         glance=[('When', 'Thursday, December 10<br>Time to be announced'), ('Where', BRONSON), ('Cost', 'Free'), ('Good for', 'All ages')],
         body=['December to Remember brings holiday cheer, hot cocoa and activities to Bronson Park on a Thursday night in the middle of the season.',
               'It’s a Thursday, so the Holly Jolly Trolley and Santa’s Workshop are both running. Make a night of it.'],
         highlights=['Hot cocoa', 'Holiday activities', 'Bronson Park in its holiday lights'],
         links=[('City of Kalamazoo holiday events', 'https://www.kalamazoocity.org/Community/Events-Meetings/Holiday-Events')],
         plans=['family-afternoon', 'under-50'], biz=False),

    dict(slug='moonlight-madness', title='Moonlight Madness', short_title='Moonlight Madness', footer=True,
         date='2026-12-12', fill='f-blue', eyebrow='Saturday, December 12, 2026',
         when_short='Sat, Dec 12 · Evening', where_short='Shops, restaurants and bars downtown', when_long='Saturday, December 12 · Evening into late night',
         summary='Downtown stays open late for a night of deals, lights, music and winter cocktails.',
         plain='On December 12, downtown shops and restaurants stay open late at night. There are deals, lights and music.',
         glance=[('When', 'Saturday, December 12<br>Last year: 6 to 11 p.m.'), ('Where', 'Shops, restaurants and bars across downtown'), ('Cost', 'Free to attend'), ('Hosted by', 'Downtown Kalamazoo Collective')],
         body=['Moonlight Madness is downtown’s late-night holiday shopping event, now in its fourth year. Shops, restaurants and bars stay open late with holiday lights all around.',
               'Last year brought pop-up vendors, deals and giveaways, boozy hot cocoa and other winter cocktails, a DJ, a group holiday bike ride with ModeShift, and the Holly Jolly Trolley running loops all night.'],
         highlights_title='What last year included',
         highlights=['Late hours at shops, restaurants and bars', 'Pop-up vendors, deals and giveaways', 'Winter cocktails and seasonal treats', 'Music and a group holiday bike ride'],
         tips=['Have dinner downtown first, then shop as the lights come up.', 'The 2026 lineup will be posted closer to the date.'],
         plans=['friday-night', 'shop-small'], biz=True),

    dict(slug='new-years-fest', title='New Year’s Fest', short_title='New Year’s Fest', footer=True,
         date='2026-12-31', fill='f-green', eyebrow='Thursday, December 31, 2026',
         when_short='Thu, Dec 31 · Evening to midnight', where_short='Bronson Park and downtown venues', when_long='Thursday, December 31 · Evening to midnight',
         summary='An all-ages celebration of performing arts that rings in the new year downtown.',
         plain='On New Year’s Eve, downtown has music and shows for all ages. It ends with the new year at midnight.',
         glance=[('When', 'Thursday, December 31<br>Evening to midnight'), ('Where', 'Bronson Park and downtown venues'), ('Cost', 'Lineup and admission to be announced'), ('For', 'All ages')],
         body=['New Year’s Fest is an all-ages showcase of performing arts in downtown Kalamazoo. Recent festivals have packed the evening with bands, comedians and other performers across many time slots, with fireworks at midnight.',
               'The Holly Jolly Trolley makes a special New Year’s Eve run, so you can get between venues without the cold walk.'],
         highlights=['Live music and comedy for all ages', 'Performances in many time slots through the evening', 'A downtown countdown to midnight'],
         tips=['The lineup is usually posted ahead of the holidays.', 'Plan a meeting spot in case your group splits up between shows.'],
         plans=['arts-evening', 'friday-night'], biz=True),
]

PLANS = [
    dict(slug='family-afternoon', title='A family holiday afternoon', tag='Families', fill='f-pink',
         summary='Santa, a free museum and a trolley ride, paced for little legs.',
         plain='This plan is for families with kids. You visit Santa, a free museum, and ride the free trolley.',
         best_for='Families with young kids', time='About 4 hours', budget='Mostly free', days='Saturdays and Sundays from Nov 28',
         stops=[
             dict(time='12:00', place='Santa’s Workshop at City Centre', what='Start with Santa while the line is short. Visits are free, and there are photo backdrops. 125 S. Kalamazoo Mall.', cost='Free'),
             dict(time='1:00', place='Kalamazoo Valley Museum', what='Warm up indoors with hands-on science and history exhibits on Rose Street. Check the museum’s schedule for planetarium shows.', cost='General admission is free'),
             dict(time='2:30', place='Cocoa break on the Kalamazoo Mall', what='Pick a café, split a treat and look at the holiday windows.', cost='Your choice'),
             dict(time='3:15', place='Ride the Holly Jolly Trolley', what='Catch the free trolley at City Hall, 241 W. South St. It leaves on the hour and half hour.', cost='Free'),
             dict(time='4:15', place='Bronson Park lights', what='End in Bronson Park as the lights come on.', cost='Free'),
         ],
         tips=['Santa’s Saturday hours last season were noon to 6 p.m. and Sunday hours were noon to 4 p.m.', 'Need a break from the crowd? The museum and library are good quiet stops.'],
         events=['small-business-saturday', 'gingerbread-wonderland', 'december-to-remember']),

    dict(slug='friday-night', title='A Friday night downtown', tag='Date night', fill='f-blue',
         summary='Art Hop, dinner and a show, with the trolley as your ride between stops.',
         plain='This plan is for a Friday night out. You see local art, eat dinner, and see a show.',
         best_for='Couples and friends', time='About 5 hours', budget='$$', days='First Fridays: Nov 6 and Dec 4',
         stops=[
             dict(time='5:30', place='Park and walk in', what='Park in the Epic Center or Kalamazoo Mall ramp and head to the Kalamazoo Mall.'),
             dict(time='6:00', place='<a href="{R}events/first-friday-dec.html">Art Hop</a>', what='Wander galleries and shops showing local artists. Pick up a handmade gift if one catches your eye.', cost='Free'),
             dict(time='7:30', place='Dinner downtown', what='Choose a restaurant from the <a href="{R}directory.html#dine">directory</a>. Book ahead on Art Hop nights.', cost='Your choice'),
             dict(time='9:00', place='A show or a nightcap', what='Catch a show at the Civic or Crawlspace Comedy Theatre, or ride the trolley to Bell’s Eccentric Café.', cost='Tickets vary'),
         ],
         tips=['The trolley runs Thursday through Sunday until Christmas Eve.', 'Santa’s Workshop is open Friday evenings if you are out with the kids.'],
         events=['first-friday-nov', 'first-friday-dec', 'moonlight-madness']),

    dict(slug='shop-small', title='Shop small and dine local', tag='Shopping', fill='f-green',
         summary='A full day of local shops, a long lunch and Downtown Dollars in your pocket.',
         plain='This plan is a full day of shopping at local stores, with lunch downtown.',
         best_for='Gift shoppers', time='Most of a day', budget='Up to you', days='Small Business Saturday, Nov 28',
         stops=[
             dict(time='10:00', place='Coffee to start', what='Fuel up at a downtown café and write your list.', cost='Your choice'),
             dict(time='10:45', place='The Kalamazoo Mall', what='Work your way down the mall, where shops sit a short walk apart. Use the <a href="{R}gifts.html">gift guides</a> for ideas.'),
             dict(time='12:30', place='Lunch at a local restaurant', what='Sit down somewhere owned by your neighbors. Downtown Dollars work at many restaurants.', cost='Your choice'),
             dict(time='2:00', place='Side streets', what='Branch off the mall for the shops a block over. The <a href="{R}directory.html#shop">directory</a> lists places to start.'),
             dict(time='4:00', place='Santa’s Workshop', what='Drop in at City Centre, 125 S. Kalamazoo Mall, before heading home.', cost='Free'),
         ],
         tips=['Buy <a href="{R}dollars.html">Downtown Dollars</a> for the people on your list who are hard to shop for.', 'Share your finds with #SomethingNewKalamazoo.'],
         events=['small-business-saturday', 'moonlight-madness', 'after-parade']),

    dict(slug='arts-evening', title='An arts and culture evening', tag='Arts', fill='f-red',
         summary='A museum, dinner and a curtain call, all within a few blocks.',
         plain='This plan is for an evening of art. You visit an art museum, eat dinner, and see a play or concert.',
         best_for='Art and theater lovers', time='About 5 hours', budget='$$', days='Any evening with a show',
         stops=[
             dict(time='3:30', place='Kalamazoo Institute of Arts', what='See the galleries before they close. 314 S. Park St.', cost='Check admission'),
             dict(time='5:30', place='Early dinner', what='Find a restaurant near Bronson Park so you can walk to the show.', cost='Your choice'),
             dict(time='7:30', place='Curtain up', what='See a production at the Kalamazoo Civic Theatre or Farmers Alley Theatre.', cost='Tickets vary'),
             dict(time='10:00', place='Bronson Park lights', what='Walk back through the park on your way out.', cost='Free'),
         ],
         tips=['On first Fridays, swap the museum for <a href="{R}events/first-friday-dec.html">Art Hop</a>.', 'New Year’s Fest is the biggest arts night of the season.'],
         events=['first-friday-nov', 'first-friday-dec', 'new-years-fest']),

    dict(slug='under-50', title='Holiday experiences under $50', tag='Budget', fill='f-mist',
         summary='Lights, Santa, a museum and a trolley ride, with money left over for lunch.',
         plain='This plan shows how two people can have a holiday day downtown for less than $50.',
         best_for='Anyone on a budget', time='Half a day', budget='Under $50 for two', days='Thursday to Sunday',
         stops=[
             dict(time='11:00', place='Park in a ramp', what='The first 90 minutes are free in the Epic Center and Kalamazoo Mall ramps.', cost='$0 to $4'),
             dict(time='11:15', place='Kalamazoo Valley Museum', what='Hands-on exhibits for all ages.', cost='General admission is free'),
             dict(time='12:30', place='Lunch downtown', what='Pay with a $20 Downtown Dollars certificate.', cost='About $20'),
             dict(time='1:45', place='Santa’s Workshop and the trolley', what='Visit Santa at City Centre, then ride the Holly Jolly Trolley loop.', cost='Free'),
             dict(time='3:00', place='Treats and windows', what='Share a holiday treat and stroll the Kalamazoo Mall.', cost='About $10'),
         ],
         budget_table=[('Parking (beyond 90 free minutes)', '$4'), ('Kalamazoo Valley Museum', '$0'), ('Lunch for two', '$20'), ('Santa and trolley', '$0'), ('Holiday treats', '$10'), ('Total', '$34')],
         tips=['Free events add up: the <a href="{R}events/tree-lighting.html">Tree Lighting</a>, <a href="{R}events/december-to-remember.html">December to Remember</a> and the parade cost nothing to attend.'],
         events=['holiday-parade', 'tree-lighting', 'december-to-remember']),

    dict(slug='last-minute', title='A last-minute downtown outing', tag='Last minute', fill='f-green',
         summary='Out of time and out of ideas? Two hours downtown can still save the holiday.',
         plain='This plan is for the last days before Christmas. You can still buy gifts and see Santa.',
         best_for='Last-minute shoppers', time='About 2 hours', budget='Up to you', days='December 21 to 24',
         stops=[
             dict(time='Anytime', place='Buy Downtown Dollars', what='They arrive by email, so they work as a gift even on Christmas Eve. <a href="{R}dollars.html">How to buy</a>.'),
             dict(time='5:00', place='Shops on the Kalamazoo Mall', what='Head straight for the mall and use the <a href="{R}gifts.html">gift guides</a> to move fast.'),
             dict(time='6:30', place='Santa’s Workshop', what='Last season, Santa stayed through Christmas Eve with evening hours Monday to Wednesday of Christmas week, and noon to 4 p.m. on the 24th.', cost='Free'),
             dict(time='7:30', place='Dinner and done', what='Celebrate finishing your list at a downtown restaurant.', cost='Your choice'),
         ],
         tips=['The Holly Jolly Trolley runs through December 24.', 'Many shops gift wrap. Ask at the counter.'],
         events=['gingerbread-wonderland', 'new-years-fest']),
]

GIFT_GUIDES = [
    dict(id='art-lover', title='For the art lover', fill='f-red',
         intro='Kalamazoo’s artists sell their work in shops and galleries all over downtown.',
         ideas=['A print, painting or photograph from <a href="{R}events/first-friday-dec.html">December’s Art Hop</a>', 'Handmade jewelry or glasswork from a local maker', 'A membership or class at the Kalamazoo Institute of Arts', 'Tickets to a show at the Civic or Farmers Alley Theatre'],
         look=[('Arts & Entertainment', 'directory.html#arts'), ('Art Hop', 'events/first-friday-dec.html')]),
    dict(id='foodie', title='For the food lover', fill='f-green',
         intro='Give them a reason to come downtown and eat.',
         ideas=['Downtown Dollars for a dinner out', 'Local coffee, chocolate or baked goods', 'A gift card to their favorite downtown restaurant', 'A tasting or brewery visit for the 21-and-over crowd'],
         look=[('Places to eat', 'directory.html#dine'), ('Downtown Dollars', 'dollars.html')]),
    dict(id='kids', title='For kids', fill='f-blue',
         intro='Presents are good. Memories are better.',
         ideas=['A visit with Santa and a framed photo from the workshop', 'Books from a downtown bookseller', 'Toys and games from a local shop', 'A day out: museum, trolley and cocoa'],
         look=[('Shops downtown', 'directory.html#shop'), ('Family afternoon plan', 'plan/family-afternoon.html')]),
    dict(id='host', title='For the host', fill='f-pink',
         intro='Something for the person who has everyone over.',
         ideas=['Candles, linens or serving pieces from a home shop', 'Locally roasted coffee or a bottle from a downtown shop', 'Flowers or a winter plant', 'A gift card for a night off from cooking'],
         look=[('Shops downtown', 'directory.html#shop')]),
    dict(id='stocking', title='Stocking stuffers', fill='f-mist',
         intro='Small, local and easy to tuck in.',
         ideas=['$5 and $10 Downtown Dollars certificates', 'Stickers, pins and cards from local makers', 'Sweets from a downtown bakery or candy shop', 'Something with the new Downtown Kalamazoo brand on it'],
         look=[('Downtown Dollars', 'dollars.html'), ('Shops downtown', 'directory.html#shop')]),
    dict(id='experiences', title='Experiences', fill='f-red',
         intro='For the person who would rather do something than unwrap something.',
         ideas=['Tickets to a concert, comedy show or play', 'A planned evening using one of our <a href="{R}plan.html">itineraries</a>', 'A New Year’s Fest outing', 'Downtown Dollars and a handwritten list of your favorite spots'],
         look=[('Plan your day', 'plan.html'), ('Arts & Entertainment', 'directory.html#arts')]),
]

# ---- Event times from the Q4 2026 marketing plan ("Find the Holidays Downtown"). Staff verify before launch.
PLAN_TIMES = {
    'first-friday-nov': '5–9 p.m.',
    'moms-in-the-zoo': '10 a.m.–4 p.m.',
    'holiday-parade': '11 a.m.–12:30 p.m.',
    'after-parade': 'Noon–3 p.m.',
    'tree-lighting': '5–7 p.m.',
    'first-friday-dec': '5–8 p.m.',
    'december-to-remember': '5:30–6:30 p.m.',
    'moonlight-madness': '6–11 p.m.',
    'new-years-fest': '6 p.m.–midnight',
}
for _e in EVENTS:
    _t = PLAN_TIMES.get(_e['slug'])
    if not _t:
        continue
    _e['when_short'] = _e['when_short'].split(' · ')[0] + ' · ' + _t
    _e['when_long'] = _e['when_long'].split(' · ')[0] + ' · ' + _t
    _k, _v = _e['glance'][0]
    _e['glance'][0] = (_k, _v.split('<br>')[0] + '<br>' + _t)
for _e in EVENTS:
    if _e['slug'] == 'moms-in-the-zoo':
        _e['summary'] = 'A Saturday downtown planned with moms in mind, from 10 a.m. to 4 p.m.'
        _e['plain'] = 'Moms in the Zoo is on Saturday, November 14, from 10 a.m. to 4 p.m. The places taking part are not posted yet.'
        _e['body'][0] = 'Moms in the Zoo is on the downtown holiday calendar for Saturday, November 14, from 10 a.m. to 4 p.m. Participating businesses and locations will be posted here as soon as they are confirmed.'
    if _e['slug'] == 'holiday-parade':
        _e['tips'] = [t for t in _e['tips'] if 'start time' not in t] + ['The 2026 route will be confirmed by the parade organizers.']
    if _e['slug'] == 'moonlight-madness':
        _e['tips'] = [t for t in _e['tips'] if 'lineup' not in t] + ['The 2026 lineup will be posted closer to the date.']
