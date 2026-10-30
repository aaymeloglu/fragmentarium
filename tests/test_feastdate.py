"""Feast-day dating, checked against dates printed in editions."""
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("feastdate", ROOT / "tools/feastdate.py")
fd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fd)


def date(year, expr, gregorian=None):
    n, _, _, greg = fd.resolve(year, expr, gregorian)
    return fd.from_jdn(n, greg)


def test_dates_printed_in_editions():
    # Chmel, Regesta Friderici III, Anhang 65: Wien, Samstag vor Judica 1446 = 2 April 1446
    assert date(1446, "Samstag vor Judica") == (1446, 4, 2)
    # Chmel, Materialien I/2, CLXXIV: Innsbruck, Eritag nach Assumptionis 1451 = 17 August 1451
    assert date(1451, "Eritag nach unnser lieben frawen tag Assumpcionis") == (1451, 8, 17)
    # Stams Frg. 199: Montag vor Sannt Jacobs tag 1454 = 22 July 1454
    assert date(1454, "an Montag vor Sannt Jacobs tag") == (1454, 7, 22)


def test_easter_both_calendars_and_default_switch():
    assert fd.easter(1601, True) == (4, 22)
    assert fd.easter(1446, False) == (4, 17)
    assert date(1601, "Ostern") == (1601, 4, 22)  # Gregorian by default after 1583
    assert date(1500, "Ostern") == (1500, 4, 19)  # Julian by default before


def test_vor_and_nach_are_strict_and_names_match_whole_words():
    # Jacobi 1454 fell on a Thursday; Donnerstag vor Jacobi is a week earlier, not the feast itself
    assert date(1454, "Jacobi") == (1454, 7, 25)
    assert date(1454, "Donnerstag vor Jacobi") == (1454, 7, 18)
    assert date(1454, "Donnerstag nach Jacobi") == (1454, 8, 1)
    assert fd.feast("Philippi et Jacobi", 1454, False)[1] == "philippi et jacobi"
    try:
        fd.feast("Johannes", 1454, False)  # must not match "anne" inside the name
        assert False
    except ValueError:
        pass


def test_julian_round_trip():
    for n in range(2200000, 2300000, 997):
        for greg in (False, True):
            assert fd.jdn(*fd.from_jdn(n, greg), greg) == n
