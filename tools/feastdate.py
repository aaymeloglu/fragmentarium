#!/usr/bin/env python3
"""Turn a medieval feast-day date into a calendar date.

    uv run python tools/feastdate.py 1454 "Montag vor Jacobi"
    uv run python tools/feastdate.py 1446 "Samstag vor Judica"
    uv run python tools/feastdate.py 1451 "Eritag nach Assumptio"
    uv run python tools/feastdate.py 1601 Ostern --calendar gregorian

A dating clause names a weekday before or after a feast ("an Montag vor Sannt Jacobs tag"), or
the feast itself. "vor" means the last such weekday strictly before the feast, "nach" the first
strictly after, as in Grotefend. Movable feasts are counted from Easter; fixed feasts are those
common to the German-speaking dioceses (a local feast or a diocesan variant is not covered: check
Grotefend for the diocese). The calendar defaults to Julian before 1583, the year Tyrol and the
Habsburg lands changed, and Gregorian from 1584; give --calendar for 1583 or for other places.
Prints the date with its weekday and the feast's own date. Standard library only.
"""
import argparse
import re
import sys

WEEKDAYS = {  # 0 = Sunday
    0: ("sonntag", "suntag", "sontag", "dominica", "sunday"),
    1: ("montag", "mentag", "mantag", "feria ii", "feria 2", "monday"),
    2: ("dienstag", "eritag", "ertag", "erchtag", "erichtag", "feria iii", "feria 3", "tuesday"),
    3: ("mittwoch", "mitwoch", "mittichen", "feria iv", "feria 4", "wednesday"),
    4: ("donnerstag", "pfinztag", "pfinstag", "phintztag", "feria v", "feria 5", "thursday"),
    5: ("freitag", "freytag", "feria vi", "feria 6", "friday"),
    6: ("samstag", "sambstag", "samztag", "sonnabend", "sabbato", "saturday"),
}
NAMES = ("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")

MOVABLE = {  # days from Easter Sunday
    "septuagesima": -63, "sexagesima": -56, "estomihi": -49, "quinquagesima": -49,
    "aschermittwoch": -46, "cinerum": -46, "invocavit": -42, "reminiscere": -35, "oculi": -28,
    "laetare": -21, "letare": -21, "judica": -14, "iudica": -14, "palmsonntag": -7, "palmarum": -7,
    "karfreitag": -2, "ostern": 0, "pascha": 0, "easter": 0, "quasimodogeniti": 7, "quasimodo": 7,
    "misericordia": 14, "jubilate": 21, "iubilate": 21, "cantate": 28, "rogate": 35,
    "auffahrt": 39, "himmelfahrt christi": 39, "ascensio": 39, "exaudi": 42, "pfingsten": 49,
    "pentecostes": 49, "trinitatis": 56, "fronleichnam": 60, "corpus christi": 60,
}
FIXED = {  # (month, day)
    "neujahr": (1, 1), "circumcisio": (1, 1), "epiphania": (1, 6), "dreikönig": (1, 6),
    "pauli bekehrung": (1, 25), "conversio pauli": (1, 25), "lichtmess": (2, 2), "purificatio": (2, 2),
    "petri stuhlfeier": (2, 22), "cathedra petri": (2, 22), "matthie": (2, 24), "matthias": (2, 24),
    "annuntiatio": (3, 25), "verkündigung": (3, 25), "georgi": (4, 23), "georgii": (4, 23),
    "marci": (4, 25), "philippi et jacobi": (5, 1), "kreuzauffindung": (5, 3), "inventio crucis": (5, 3),
    "veit": (6, 15), "viti": (6, 15), "johannis baptiste": (6, 24), "sunnwenden": (6, 24),
    "petri et pauli": (6, 29), "ulrich": (7, 4), "udalrici": (7, 4), "maria magdalena": (7, 22),
    "jacobi": (7, 25), "jacobs": (7, 25), "anne": (7, 26), "petri kettenfeier": (8, 1),
    "ad vincula": (8, 1), "laurentii": (8, 10), "laurenzen": (8, 10), "assumptio": (8, 15),
    "assumpcionis": (8, 15), "assumptionis": (8, 15), "himmelfahrt mariae": (8, 15),
    "bartholomei": (8, 24), "bartlme": (8, 24), "egidii": (9, 1), "gilgen": (9, 1),
    "nativitas mariae": (9, 8), "mariä geburt": (9, 8), "exaltatio crucis": (9, 14),
    "kreuzerhöhung": (9, 14), "matthei": (9, 21), "michaelis": (9, 29), "michels": (9, 29),
    "galli": (10, 16), "lucae": (10, 18), "simonis et jude": (10, 28), "allerheiligen": (11, 1),
    "omnium sanctorum": (11, 1), "allerseelen": (11, 2), "leonhardi": (11, 6), "martini": (11, 11),
    "martins": (11, 11), "elisabeth": (11, 19), "kathrein": (11, 25), "katharine": (11, 25),
    "andree": (11, 30), "andreas": (11, 30), "nicolai": (12, 6), "conceptio mariae": (12, 8),
    "lucie": (12, 13), "thome": (12, 21), "thomae": (12, 21), "weihnachten": (12, 25),
    "nativitas domini": (12, 25), "stephani": (12, 26), "johannis evangeliste": (12, 27),
    "kindleintag": (12, 28), "innocentum": (12, 28), "silvestri": (12, 31),
}


def jdn(y, m, d, gregorian):
    a = (14 - m) // 12
    yy, mm = y + 4800 - a, m + 12 * a - 3
    n = d + (153 * mm + 2) // 5 + 365 * yy + yy // 4
    return n - yy // 100 + yy // 400 - 32045 if gregorian else n - 32083


def from_jdn(n, gregorian):
    if gregorian:
        a = n + 32044
        b = (4 * a + 3) // 146097
        c = a - 146097 * b // 4
    else:
        b, c = 0, n + 32082
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153
    return 100 * b + d - 4800 + m // 10, m + 3 - 12 * (m // 10), e - (153 * m + 2) // 5 + 1


def weekday(n):
    return (n + 1) % 7


def easter(y, gregorian):
    if not gregorian:
        d = (19 * (y % 19) + 15) % 30
        e = (2 * (y % 4) + 4 * (y % 7) - d + 34) % 7
        return (d + e + 114) // 31, (d + e + 114) % 31 + 1
    a, b, c = y % 19, y // 100, y % 100
    h = (19 * a + b - b // 4 - (b - (b + 8) // 25 + 1) // 3 + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * (b % 4) + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    return (h + l - 7 * m + 114) // 31, (h + l - 7 * m + 114) % 31 + 1


def norm(text):
    text = re.sub(r"\b(sant|sannt|sankt|st\.?|des|der|heiligen|zwelfpoten|tag|tags|unser|unnser|lieben|frawen|frauen|an|am)\b", " ", text.lower())
    return re.sub(r"\s+", " ", text).strip()


def feast(name, year, gregorian):
    """JDN of the named feast in `year`."""
    key = norm(name)
    for table in (MOVABLE, FIXED):
        for k in sorted(table, key=len, reverse=True):
            if re.search(r"\b" + re.escape(k), key):
                if table is MOVABLE:
                    m, d = easter(year, gregorian)
                    return jdn(year, m, d, gregorian) + MOVABLE[k], k
                m, d = FIXED[k]
                return jdn(year, m, d, gregorian), k
    raise ValueError(f"unknown feast: {name!r} (see Grotefend; add it to FIXED or MOVABLE)")


def resolve(year, expr, gregorian=None):
    """(JDN of the date, JDN of the feast, feast key, calendar) for an expression such as 'Montag vor Jacobi'."""
    if gregorian is None:
        gregorian = year >= 1584
    text = expr.lower().strip()
    match = re.match(r"(.+?)\s+(vor|nach|post|ante)\s+(.+)", text)
    if not match:
        n, key = feast(text, year, gregorian)
        return n, n, key, gregorian
    day, rel, rest = match.groups()
    day = re.sub(r"^(an|am|des|dem)\s+", "", day.strip())
    wanted = next((w for w, names in WEEKDAYS.items() if any(day.strip().startswith(x) for x in names)), None)
    if wanted is None:
        raise ValueError(f"unknown weekday: {day!r}")
    f, key = feast(rest, year, gregorian)
    step = -1 if rel in ("vor", "ante") else 1
    n = f + step
    while weekday(n) != wanted:
        n += step
    return n, f, key, gregorian


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("year", type=int)
    ap.add_argument("expr", help='e.g. "Montag vor Jacobi", "Samstag vor Judica", "Martini"')
    ap.add_argument("--calendar", choices=("julian", "gregorian"))
    a = ap.parse_args(argv)
    if a.calendar is None and a.year == 1583:
        print("warning: 1583 is the changeover year; give --calendar", file=sys.stderr)
    greg = None if a.calendar is None else a.calendar == "gregorian"
    try:
        n, f, key, greg = resolve(a.year, a.expr, greg)
    except ValueError as e:
        sys.exit(str(e))
    cal = "Gregorian" if greg else "Julian"
    y, m, d = from_jdn(n, greg)
    fy, fm, fd = from_jdn(f, greg)
    print(f"{y}-{m:02d}-{d:02d} ({NAMES[weekday(n)]}, {cal}); feast '{key}' on "
          f"{fy}-{fm:02d}-{fd:02d} ({NAMES[weekday(f)]})")


if __name__ == "__main__":
    main()
