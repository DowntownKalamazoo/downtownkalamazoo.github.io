"""Find the K's: a holiday scavenger hunt. Shared by build.py (pages) and make_assets.py (printable signs)."""
N = 12
# Each sign also prints a short word, so people who can't scan a QR code can still collect it on the hunt page.
CODES = ['PINE', 'COCOA', 'SLED', 'MITTEN', 'GARLAND', 'SPARKLE', 'CANDLE', 'TROLLEY', 'PARADE', 'COOKIE', 'LANTERN', 'SNOWDROP']
# If there is a prize or drawing, describe it here and it appears on the hunt page. Leave blank for none.
PRIZE = ''
PATTERNS = ['squiggle', 'dots', 'speckle', 'maze', 'loops', 'dashes'] * 2


def code_hash(word):
    """A small hash so the codes aren't sitting in the page as plain text."""
    h = 5381
    for ch in word.upper():
        h = ((h * 33) ^ ord(ch)) & 0xFFFFFFFF
    return h
