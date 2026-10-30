"""Hidden finds behind the turnable corners. Each is a short, verified fact or a real downtown business."""
import html
import directory_page

E = html.escape
BIZ = {b['name']: b for b in directory_page.BIZ}


def biz(name, kicker='A local find'):
    b = BIZ[name]
    return dict(kicker=kicker, title=b['name'], text=b['desc'], link=(f'directory.html#b-{b["id"]}', 'See it in the directory'))


def fact(title, text, link=None, kicker='Did you know?'):
    return dict(kicker=kicker, title=title, text=text, link=link)


MALL = fact('America’s first pedestrian mall',
            'The Kalamazoo Mall opened on August 19, 1959, as the nation’s first pedestrian shopping mall. It is still the heart of downtown.',
            ('directory.html#shop', 'Shop the Kalamazoo Mall'))
BRONSON = fact('A town called Bronson',
               'Titus Bronson settled here in 1829 and laid out the Village of Bronson. It was renamed Kalamazoo in 1836, and Bronson Park still carries his name.',
               ('events/tree-lighting.html', 'See the Tree Lighting in Bronson Park'))
PARADE = fact('A tradition since 1962',
              'Gilmore Department Store started Kalamazoo’s holiday parade in 1962. Today it draws close to 30,000 people to the curb.',
              ('events/holiday-parade.html', 'Parade details'))
TROLLEY = fact('Room for 24',
               'The free Holly Jolly Trolley seats 24 and leaves City Hall on the hour and half hour. On busy nights, catch it at the start of the loop.',
               ('visit.html', 'Trolley and parking details'), kicker='Insider tip')

# Corner cards in page heroes, keyed by page path
PAGE_SECRETS = {
    'events.html': fact('Dozens of shows, one night',
                        'Recent New Year’s Fests have filled the evening with bands, comedians and other performers across many time slots, ending with fireworks at midnight.',
                        ('events/new-years-fest.html', 'New Year’s Fest')),
    'plan.html': fact('Where Bell’s began pouring',
                      'Bell’s Eccentric Café on East Kalamazoo Avenue was the first Michigan brewery to open its own pub on site.',
                      ('directory.html#b-bell-s-eccentric-cafe', 'See it in the directory')),
    'directory.html': fact('Studios in an old factory',
                           'More than 20 artists and makers work inside the Park Trades Center on West Kalamazoo Avenue: glassblowers, blacksmiths, painters and printmakers. Many open their doors on Art Hop nights.',
                           ('directory.html#b-park-trades-center', 'See the Park Trades Center')),
    'gifts.html': fact('A pizza you can mail',
                       'Bimbo’s Pizza ships its thin-crust pizza nationwide, so a downtown gift can reach someone who moved away.',
                       ('directory.html#b-bimbo-s-pizza', 'See Bimbo’s in the directory'), kicker='Gift idea'),
    'sbs.html': biz('The Aroma Labs', kicker='Gift idea'),
    'dollars.html': fact('Not just shops',
                         'Downtown Dollars also work at participating salons, cafés, restaurants and entertainment venues, and you can show them right from your phone.',
                         ('directory.html#dollars', 'See who takes them'), kicker='Insider tip'),
    'visit.html': BRONSON,
    'businesses.html': fact('Patterns made for downtown',
                            'The Downtown Kalamazoo brand launched with its own library of patterns. Businesses may use them, and other patterns and photos too, as long as the K and logotype stay readable.',
                            None, kicker='Brand tip'),
    'accessibility.html': fact('Curb cuts, made in Kalamazoo',
                               'In the 1940s Kalamazoo installed curb cuts as a pilot project, introduced by veteran and lawyer Jack H. Fischer to help veterans with disabilities get to work.',
                               None),
    'submit-event.html': fact('Today’s new idea, tomorrow’s tradition',
                              'Moonlight Madness began in 2023. Now in its fourth year, it keeps downtown open until 11 p.m. Your event could be the next one people look forward to.',
                              ('events/moonlight-madness.html', 'Moonlight Madness'), kicker='Psst'),
    # events
    'events/first-friday-nov.html': fact('51 stops in one night',
                                         'One Art Hop back in 2011 had 51 stops, most of them downtown, with live music at Terrapin and the public library.', None),
    'events/moms-in-the-zoo.html': fact('An easy gift',
                                        'Downtown Dollars come in $5, $10 and $20 and stay good for five years, so they make an easy gift for the moms on your list.',
                                        ('dollars.html', 'Downtown Dollars'), kicker='Gift idea'),
    'events/holiday-parade.html': PARADE,
    'events/after-parade.html': MALL,
    'events/tree-lighting.html': BRONSON,
    'events/small-business-saturday.html': biz('Kalamazoo Candle Company', kicker='Make it yourself'),
    'events/first-friday-dec.html': fact('Studios in an old factory',
                                         'Glassblowers, blacksmiths, painters and printmakers work inside the Park Trades Center. Many open their doors on Art Hop nights.',
                                         ('directory.html#b-park-trades-center', 'See the Park Trades Center')),
    'events/gingerbread-wonderland.html': fact('Built by downtown',
                                               'Downtown businesses have a sweet streak: in 2023, Community Homeworks held its third annual Homes for the Holidays gingerbread house contest, with entries from local shops and restaurants.', None),
    'events/december-to-remember.html': fact('Make it a Thursday',
                                             'Last season, Santa’s Workshop was open Thursday evenings from 5 to 8 p.m., and the free trolley ran Thursdays too.',
                                             ('events/small-business-saturday.html', 'Santa’s Workshop'), kicker='Insider tip'),
    'events/moonlight-madness.html': fact('Bring your bike',
                                          'Last year’s Moonlight Madness included a group holiday bike ride with ModeShift, rolling through the lights.', None),
    'events/new-years-fest.html': fact('Pick your shows',
                                       'Recent festivals have packed the evening with bands, comedians and performers in many time slots. Plan a meeting spot in case your group splits up.', None, kicker='Insider tip'),
    # plans: a bonus stop
    'plan/family-afternoon.html': biz('Pop City Popcorn', kicker='Bonus stop'),
    'plan/friday-night.html': biz('Crawlspace Comedy Theatre', kicker='Bonus stop'),
    'plan/shop-small.html': biz('Kalamazoo Candle Company', kicker='Bonus stop'),
    'plan/arts-evening.html': biz('Kalamazoo Book Arts Center', kicker='Bonus stop'),
    'plan/under-50.html': biz('Rocket Fizz', kicker='Bonus stop'),
    'plan/last-minute.html': biz('Mason Jar Plant Shop', kicker='Bonus stop'),
}

HOME_HERO = MALL
PILLAR_SECRETS = [
    biz("Uncle Buddy's Toy Stash"),
    fact('Downtown stays up late', 'On Friday, December 11, shops, restaurants and bars stay open from 6 to 11 p.m. for Moonlight Madness: deals, lights and music.',
         ('events/moonlight-madness.html', 'Moonlight Madness'), kicker='Mark your calendar'),
    PARADE,
    TROLLEY,
]

GUIDE_PICKS = {
    'art-lover': 'Glass Art Kalamazoo',
    'foodie': 'Sarkozy Bakery',
    'kids': "Uncle Buddy's Toy Stash",
    'host': 'Mason Jar Plant Shop',
    'stocking': 'Pop City Popcorn',
    'experiences': 'Climb Kalamazoo',
}

TEASERS = ['Psst.', 'Look closer.', 'Peek around.', 'Curious?', 'Wait, there’s more.', 'Turn me.']


# ---------- Serendipity: a single pool of finds that turn up in random places ----------
import re as _re


def _slug(s):
    return _re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')[:40]


GENERAL = [
    MALL, BRONSON, PARADE, TROLLEY,
    PAGE_SECRETS['directory.html'], PAGE_SECRETS['plan.html'], PAGE_SECRETS['gifts.html'],
    PAGE_SECRETS['businesses.html'], PAGE_SECRETS['accessibility.html'], PAGE_SECRETS['submit-event.html'],
    PAGE_SECRETS['events/first-friday-nov.html'], PAGE_SECRETS['events/gingerbread-wonderland.html'],
    PAGE_SECRETS['events/moonlight-madness.html'],
    biz("Uncle Buddy's Toy Stash"), biz('The Aroma Labs'), biz('Kalamazoo Candle Company'), biz('Pop City Popcorn'),
    biz('Crawlspace Comedy Theatre'), biz('Kalamazoo Book Arts Center'), biz('Rocket Fizz'), biz('Mason Jar Plant Shop'),
    biz('Glass Art Kalamazoo'), biz('Climb Kalamazoo'), biz('Sarkozy Bakery'), biz('Kalamazoo Spice and Tea Merchants'),
]
POOL = {}
for _f in GENERAL + list(PAGE_SECRETS.values()):
    _id = _slug(_f['title'])
    if _id not in POOL:
        POOL[_id] = dict(k=_f['kicker'], t=_f['title'], x=_f['text'], l=list(_f['link']) if _f.get('link') else None)
PAGE_PICKS = {path: [_slug(f['title'])] for path, f in PAGE_SECRETS.items()}
