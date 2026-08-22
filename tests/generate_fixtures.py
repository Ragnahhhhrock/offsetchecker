#!/usr/bin/env python3
"""
Offsetcheck synthetic statement fixture generator.

Builds synthetic bank-statement fixtures for testing the Offsetcheck auditor
(check.html). Ground truth is computed FIRST from a synthetic ledger; the
ledger is then optionally mutated (fault injection) and rendered to CSV,
XLSX, PDF, TXT and PNG statement files. Every fixture ships with an
`<id>.expected.json` manifest recording the inputs a user would enter and
the exact outputs the tool must produce.

Usage:
    python3 tests/generate_fixtures.py              # generate all fixtures
    python3 tests/generate_fixtures.py --validate   # re-parse CSVs and check manifests

All data is fictional. Bank names are invented; no real BSBs, account
numbers, or personal data are used.
"""

import argparse
import csv
import datetime as dt
import json
import random
from pathlib import Path

# ---------------------------------------------------------------- constants

RATE = 5.99                      # advertised interest rate, % p.a.
LOAN_BALANCE = 500_000.00        # loan principal, AUD
REVIEW_TOL_PCT = 1.0             # <=1% discrepancy -> Review, above -> Overcharge

BANKS = [
    ("Meridian Mutual Bank",  "062-001", "8834 2210"),
    ("Coastline Credit Union", "802-144", "5510 0973"),
    ("Wattle & Stone Bank",   "733-552", "1146 7852"),
]

DEBIT_NARRATIONS = [
    "WOOLWORTHS 2432 MARRICKVILLE", "COLES 0881 DULWICH HILL", "BP PETROL 5821",
    "TRANSPORT NSW OPAL", "AGL ENERGY 88412093", "TELSTRA MOBILE 0441",
    "NETFLIX.COM 866-579", "CHEMIST WAREHOUSE 3310", "BUNNINGS 4180",
    "AMPOL FOODARY 2291", "UBER TRIP", "ORIGIN ENERGY GAS", "KMART 1155",
    "SPOTLIGHT 0208", "OFFICEWORKS 0242", "ALD I STORES 4412",
]
CREDIT_NARRATIONS = [
    "SALARY HAYMARKET DESIGN PTY", "TRANSFER FROM SAVINGS", "REFUND AGL ENERGY",
    "MEDICARE REBATE", "INTEREST PAID", "DEPOSIT BRANCH 0621",
]
MORTGAGE_NARR = "LOAN REPAYMENT 552018"
INTEREST_NARR = "INTEREST CHARGED"

FINDING_VERIFIED = "Verified"
FINDING_REVIEW = "Review"
FINDING_OVERCHARGE = "Overcharge"


# ---------------------------------------------------------------- helpers

def daterange(start: dt.date, days: int):
    return [start + dt.timedelta(days=i) for i in range(days)]


def r2(x: float) -> float:
    return round(x + 1e-9, 2)


def money(x: float) -> str:
    return f"{x:,.2f}"


# ---------------------------------------------------------------- ledger

def build_ledger(seed: int, start: dt.date, days: int = 90,
                 opening: float = 21_450.00, interest_rate: float = RATE,
                 big_credit: tuple | None = None) -> dict:
    """Build a synthetic 90-day ledger.

    Transaction categories: 'offset' (moves the offset balance),
    'mortgage' (loan repayment), 'interest' (interest charge), 'fee'.
    Amounts are signed: credits positive, debits negative.
    `big_credit`: optional (day_offset, amount) one-off credit (D5 cap test).
    """
    rng = random.Random(seed)
    txns = []

    for i, day in enumerate(daterange(start, days)):
        # fortnightly salary, starting day 1
        if i % 14 == 1:
            txns.append(dict(date=day, desc=CREDIT_NARRATIONS[0],
                             amount=4_250.00, category="offset"))
        # fortnightly mortgage repayment, starting day 3
        if i % 14 == 3:
            txns.append(dict(date=day, desc=MORTGAGE_NARR,
                             amount=-2_850.00, category="mortgage"))
        # monthly interest charge on the loan (every 30 days, from day 29)
        if i % 30 == 29:
            charge = r2(LOAN_BALANCE * interest_rate / 100 / 365 * 30)
            txns.append(dict(date=day, desc=INTEREST_NARR,
                             amount=-charge, category="interest"))
        # one-off large credit for the offset-cap scenario
        if big_credit and i == big_credit[0]:
            txns.append(dict(date=day, desc="ESTATE DISTRIBUTION FINAL",
                             amount=big_credit[1], category="offset"))
        # everyday spending: ~65% of days get 1-2 debits
        if rng.random() < 0.65:
            for _ in range(rng.choice([1, 1, 2])):
                txns.append(dict(date=day, desc=rng.choice(DEBIT_NARRATIONS),
                                 amount=-r2(rng.uniform(8, 320)),
                                 category="offset"))
        # occasional extra credits
        if rng.random() < 0.07:
            txns.append(dict(date=day,
                             desc=rng.choice(CREDIT_NARRATIONS[1:]),
                             amount=r2(rng.uniform(40, 900)),
                             category="offset"))

    txns.sort(key=lambda t: (t["date"], 0 if t["amount"] > 0 else 1))
    return dict(opening=opening, start=start, days=days, txns=txns)


# ---------------------------------------------------------------- ground truth

def daily_balances(ledger: dict) -> dict:
    """Closing offset balance for each day of the period."""
    by_date = {}
    for t in ledger["txns"]:
        if t["category"] == "offset":
            by_date[t["date"]] = by_date.get(t["date"], 0.0) + t["amount"]
    balances = {}
    bal = ledger["opening"]
    for day in daterange(ledger["start"], ledger["days"]):
        bal += by_date.get(day, 0.0)
        balances[day] = r2(bal)
    return balances


def calc_offset(balances: dict, rate: float, loan: float,
                leap_aware: bool = False) -> float:
    """Expected offset benefit: sum over days of min(balance, loan) * rate/day.

    Mirrors check.html: daily rate = rate / 100 / 365, benefit capped at the
    amount still owing. leap_aware=True models a bank that divides by 366 in
    a leap year (used to derive the *actual* credit for fixture D6).
    """
    total = 0.0
    for day, bal in balances.items():
        divisor = 366 if (leap_aware and _is_leap(day.year)) else 365
        total += min(max(bal, 0.0), loan) * rate / 100 / divisor
    return r2(total)


def _is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def classify(difference: float, expected: float) -> str:
    """Finding tier from signed difference (expected - actual)."""
    if abs(difference) < 0.01:
        return FINDING_VERIFIED
    pct = difference / expected * 100 if expected > 0 else 0.0
    if difference > 0 and pct > REVIEW_TOL_PCT:
        return FINDING_OVERCHARGE
    return FINDING_REVIEW


# ---------------------------------------------------------------- renderers

def _fmt_date(d: dt.date, style: str) -> str:
    return {"dmy": d.strftime("%d/%m/%Y"), "iso": d.isoformat(),
            "dmony": d.strftime("%d %b %Y")}[style]


def _fmt_amount(x: float, style: str) -> str:
    if style == "dollar":
        return f"-${abs(x):,.2f}" if x < 0 else f"${x:,.2f}"
    return f"{x:.2f}"


def render_csv_v1(path: Path, ledger: dict, txns: list, date_style="dmy",
                  money_style="plain", malformed=False):
    """Simple layout: Date,Description,Amount (signed)."""
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Description", "Amount"])
        for i, t in enumerate(txns):
            row = [_fmt_date(t["date"], date_style), t["desc"],
                   _fmt_amount(t["amount"], money_style)]
            if malformed and i == 10:
                w.writerow([])                       # stray blank line
            if malformed and i == 20:
                w.writerow(["# end of export"])      # comment line
            if malformed and i == 30:
                w.writerow(["--", "--"])             # ragged junk row
            w.writerow(row)


def render_csv_v2(path: Path, ledger: dict, txns: list, date_style="dmy"):
    """Bank layout: Date,Narration,Debit,Credit,Balance (running)."""
    bal = ledger["opening"]
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Date", "Narration", "Debit", "Credit", "Balance"])
        for t in txns:
            if t["category"] == "offset":
                bal = r2(bal + t["amount"])
                debit = f"{-t['amount']:.2f}" if t["amount"] < 0 else ""
                credit = f"{t['amount']:.2f}" if t["amount"] > 0 else ""
                w.writerow([_fmt_date(t["date"], date_style), t["desc"],
                            debit, credit, f"{bal:.2f}"])
            else:  # loan-side rows: shown for reference, no offset balance
                w.writerow([_fmt_date(t["date"], date_style), t["desc"],
                            f"{-t['amount']:.2f}" if t["amount"] < 0 else "",
                            f"{t['amount']:.2f}" if t["amount"] > 0 else "", ""])


def render_xlsx(path: Path, ledger: dict, txns: list, excel_dates=False):
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Statement"
    ws.append(["Date", "Description", "Amount"])
    for t in txns:
        d = dt.datetime(t["date"].year, t["date"].month,
                        t["date"].day) if excel_dates else _fmt_date(t["date"], "dmy")
        ws.append([d, t["desc"], t["amount"]])
    if excel_dates:
        for row in ws.iter_rows(min_row=2, min_col=1, max_col=1):
            row[0].number_format = "DD/MM/YYYY"
    wb.save(path)


def _statement_lines(ledger: dict, txns: list, bank: tuple, meta: dict):
    """Plain-text statement body shared by the TXT and PNG renderers."""
    name, bsb, acct = bank
    start = ledger["start"]
    end = start + dt.timedelta(days=ledger["days"] - 1)
    L = []
    L.append(name.upper())
    L.append("OFFSET ACCOUNT STATEMENT")
    L.append(f"Account: {bsb} {acct}")
    L.append(f"Period: {_fmt_date(start, 'dmy')} - {_fmt_date(end, 'dmy')}")
    L.append(f"Opening balance: ${money(ledger['opening'])}")
    L.append("")
    bal = ledger["opening"]
    for t in txns:
        amt = money(abs(t["amount"]))
        amt = f"{'CR' if t['amount'] > 0 else 'DR'} {amt}"
        line = f"{_fmt_date(t['date'], 'dmy')}  {t['desc'][:34]:<34} {amt:>14}"
        if t["category"] == "offset":
            bal = r2(bal + t["amount"])
            line += f"   bal {money(bal):>12}"
        L.append(line)
    L.append("")
    L.append(f"Closing balance: ${money(bal)}")
    if "interest_total" in meta:
        L.append(f"Total interest charged: ${money(meta['interest_total'])}")
    if "offset_credited" in meta:
        L.append(f"Offset benefit credited: ${money(meta['offset_credited'])}")
    return L


def render_txt(path: Path, ledger: dict, txns: list, bank: tuple, meta: dict):
    path.write_text("\n".join(_statement_lines(ledger, txns, bank, meta)) + "\n")


def render_png(path: Path, ledger: dict, txns: list, bank: tuple, meta: dict):
    """Render the statement as a 'scanned' PNG image."""
    from PIL import Image, ImageDraw, ImageFont
    lines = _statement_lines(ledger, txns, bank, meta)
    font = ImageFont.truetype(
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 16)
    w, h = 1000, 40 + 24 * len(lines)
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        d.text((20, 20 + 24 * i), line, fill="#111111", font=font)
    img.save(path)


def render_pdf(path: Path, ledger: dict, txns: list, bank: tuple, meta: dict):
    """Text-based PDF statement with bank letterhead and summary box."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer,
                                    Table, TableStyle)
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

    name, bsb, acct = bank
    start = ledger["start"]
    end = start + dt.timedelta(days=ledger["days"] - 1)
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=16)
    doc = SimpleDocTemplate(str(path), pagesize=A4,
                            leftMargin=18 * mm, rightMargin=18 * mm)
    story = [
        Paragraph(name, h1),
        Paragraph("Offset Account Statement", styles["Heading2"]),
        Paragraph(f"Account: {bsb} {acct} &nbsp;&nbsp;|&nbsp;&nbsp; "
                  f"Period: {_fmt_date(start, 'dmy')} – {_fmt_date(end, 'dmy')}",
                  styles["Normal"]),
        Paragraph(f"Opening balance: ${money(ledger['opening'])}",
                  styles["Normal"]),
        Spacer(1, 6 * mm),
    ]
    data = [["Date", "Description", "Debit", "Credit", "Balance"]]
    bal = ledger["opening"]
    for t in txns:
        if t["category"] == "offset":
            bal = r2(bal + t["amount"])
            data.append([_fmt_date(t["date"], "dmy"), t["desc"][:38],
                         money(-t["amount"]) if t["amount"] < 0 else "",
                         money(t["amount"]) if t["amount"] > 0 else "",
                         money(bal)])
        else:
            data.append([_fmt_date(t["date"], "dmy"), t["desc"][:38],
                         money(-t["amount"]) if t["amount"] < 0 else "",
                         money(t["amount"]) if t["amount"] > 0 else "", ""])
    tbl = Table(data, repeatRows=1,
                colWidths=[24 * mm, 74 * mm, 24 * mm, 24 * mm, 26 * mm])
    tbl.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 8),
        ("FONT", (0, 1), (-1, -1), "Courier", 7),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F2F4F7")),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#D0D5DD")),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.white, colors.HexColor("#FCFCFD")]),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5 * mm))
    story.append(Paragraph(f"Closing balance: ${money(bal)}",
                           styles["Heading3"]))
    if "interest_total" in meta:
        story.append(Paragraph(
            f"Total interest charged this period: "
            f"${money(meta['interest_total'])}", styles["Normal"]))
    if "offset_credited" in meta:
        story.append(Paragraph(
            f"Offset benefit credited this period: "
            f"${money(meta['offset_credited'])}", styles["Normal"]))
    doc.build(story)


# ---------------------------------------------------------------- scenarios

START_2026 = dt.date(2026, 3, 1)
START_LEAP = dt.date(2028, 1, 15)   # 90-day period spanning Feb 2028 (leap)


def _expected_from(txns, ledger, rate=RATE, loan=LOAN_BALANCE):
    """What the tool must compute from the rendered statement."""
    rendered = dict(ledger, txns=txns)
    balances = daily_balances(rendered)
    return calc_offset(balances, rate, loan), balances


def make_scenarios():
    """Each entry: id, title, ledger, rendered txns, actual offset, meta,
    faults, notes, finding override."""
    S = []

    # D0 — clean control
    led = build_ledger(1001, START_2026)
    exp, _ = _expected_from(led["txns"], led)
    S.append(dict(id="D0-clean", title="Clean control (Verified)",
                  ledger=led, txns=led["txns"], actual=exp, faults=[],
                  notes="Actual offset credit equals expected exactly."))

    # D1 — underpayment: bank credits 92% of expected
    led = build_ledger(1002, START_2026)
    exp, _ = _expected_from(led["txns"], led)
    S.append(dict(id="D1-underpayment", title="Underpayment 8% (Overcharge)",
                  ledger=led, txns=led["txns"], actual=r2(exp * 0.92),
                  faults=[dict(type="underpayment", factor=0.92)],
                  notes="Bank credits 92% of the expected offset benefit; "
                        "letter of demand must carry the exact shortfall."))

    # D2 — interest charged at 6.49% instead of 5.99%
    led = build_ledger(1003, START_2026, interest_rate=6.49)
    exp, _ = _expected_from(led["txns"], led, rate=RATE)
    true_interest = r2(LOAN_BALANCE * RATE / 100 / 365 * 30 * 3)
    stmt_interest = r2(LOAN_BALANCE * 6.49 / 100 / 365 * 30 * 3)
    S.append(dict(id="D2-wrong-rate", title="Interest charged at 6.49% vs 5.99%",
                  ledger=led, txns=led["txns"], actual=exp,
                  faults=[dict(type="wrong_rate", charged=6.49, entered=RATE,
                               excess_interest=r2(stmt_interest - true_interest))],
                  notes="Offset credit is correct, but the three interest "
                        "charges are calculated at 6.49% p.a. Tool must flag "
                        "excess interest of the manifest amount.",
                  finding_override=FINDING_REVIEW))

    # D3 — one deposit missing from the statement
    led = build_ledger(1004, START_2026)
    salaries = [t for t in led["txns"] if t["desc"] == CREDIT_NARRATIONS[0]]
    dep = salaries[2]  # mid-period salary credit goes missing
    txns = [t for t in led["txns"] if t is not dep]
    exp_rendered, _ = _expected_from(txns, led)
    exp_true, _ = _expected_from(led["txns"], led)
    S.append(dict(id="D3-missing-transaction",
                  title="Deposit omitted from statement",
                  ledger=led, txns=txns, actual=exp_true,
                  faults=[dict(type="missing_transaction",
                               date=dep["date"].isoformat(), desc=dep["desc"],
                               amount=dep["amount"])],
                  notes=f"Deposit of ${money(dep['amount'])} on "
                        f"{_fmt_date(dep['date'], 'dmy')} omitted. Rebuilt "
                        f"closing balance must break by exactly that amount.",
                  finding_override=FINDING_REVIEW,
                  expected_offset_override=exp_rendered))

    # D4 — one interest charge duplicated
    led = build_ledger(1005, START_2026)
    idx = next(i for i, t in enumerate(led["txns"])
               if t["category"] == "interest")
    dup = dict(led["txns"][idx])
    txns = led["txns"][:idx + 1] + [dup] + led["txns"][idx + 1:]
    exp, _ = _expected_from(txns, led)
    S.append(dict(id="D4-duplicate-charge",
                  title="Interest charge duplicated",
                  ledger=led, txns=txns, actual=exp,
                  faults=[dict(type="duplicate_transaction",
                               date=dup["date"].isoformat(), desc=dup["desc"],
                               amount=dup["amount"])],
                  notes="Statement contains one interest charge twice; the "
                        "bank summary line still shows the true total. Tool "
                        "must surface the count/total mismatch.",
                  finding_override=FINDING_REVIEW))

    # D5 — offset balance exceeds loan balance (benefit must cap)
    led = build_ledger(1006, START_2026, big_credit=(10, 620_000.00))
    exp, balances = _expected_from(led["txns"], led)
    capped_days = sum(1 for b in balances.values() if b > LOAN_BALANCE)
    S.append(dict(id="D5-offset-cap",
                  title="Offset balance above loan balance (capped)",
                  ledger=led, txns=led["txns"], actual=exp,
                  faults=[],
                  notes=f"$620,000 credit on day 10 pushes the offset balance "
                        f"above the $500,000 loan for {capped_days} days. "
                        f"Benefit must be capped at the amount owing.",
                  capped_days=capped_days))

    # D6 — leap year: bank divided by 366 in 2028, tool expects /365
    led = build_ledger(1007, START_LEAP)
    exp, balances = _expected_from(led["txns"], led)
    actual = calc_offset(balances, RATE, LOAN_BALANCE, leap_aware=True)
    S.append(dict(id="D6-leap-year",
                  title="Leap-year divisor (bank used 366)",
                  ledger=led, txns=led["txns"], actual=actual,
                  faults=[dict(type="leap_year_divisor", bank_divisor=366)],
                  notes="Period spans Feb 2028. Bank credited using a 366-day "
                        "divisor; expected uses 365. Small systematic "
                        "shortfall -> Review tier."))

    return S


# ---------------------------------------------------------------- manifests

def build_manifest(scn, fmt, filename, layout=None):
    led, txns = scn["ledger"], scn["txns"]
    start = led["start"]
    end = start + dt.timedelta(days=led["days"] - 1)
    interest = [t for t in txns if t["category"] == "interest"]
    mortgage = [t for t in txns if t["category"] == "mortgage"]
    expected = scn.get("expected_offset_override")
    if expected is None:
        expected, balances = _expected_from(txns, led)
    else:
        _, balances = _expected_from(txns, led)
    actual = scn["actual"]
    diff = r2(expected - actual)
    pct = r2(diff / expected * 100) if expected > 0 else 0.0
    finding = scn.get("finding_override") or classify(diff, expected)
    closing = r2(led["opening"] + sum(t["amount"] for t in txns
                                      if t["category"] == "offset"))
    letter = None
    if finding == FINDING_OVERCHARGE:
        letter = dict(expectedOffset=expected, actualOffset=actual,
                      shortfall=diff, rate=RATE,
                      periodStart=start.isoformat(), periodEnd=end.isoformat())
    man = dict(
        id=scn["id"] if fmt == "primary" else f"{scn['id']}-{fmt}",
        scenario=scn["title"], file=filename, layout=layout or fmt,
        bank=dict(name=BANKS[0][0], bsb=BANKS[0][1], account=BANKS[0][2]),
        period=dict(start=start.isoformat(), end=end.isoformat(),
                    days=led["days"]),
        inputs=dict(interestRate=RATE, loanBalance=LOAN_BALANCE,
                    actualOffsetCredited=actual),
        expected=dict(transactionCount=len(txns),
                      interestTxCount=len(interest),
                      mortgageTxCount=len(mortgage),
                      totalInterestPaid=r2(sum(-t["amount"] for t in interest)),
                      openingBalance=led["opening"],
                      closingBalance=closing,
                      expectedOffset=expected, actualOffset=actual,
                      difference=diff, discrepancyPct=pct, finding=finding,
                      letterOfDemand=letter),
        faults=scn["faults"], notes=scn["notes"],
    )
    if "capped_days" in scn:
        man["expected"]["cappedDays"] = scn["capped_days"]
    return man


def meta_for(scn):
    interest = r2(sum(-t["amount"] for t in scn["txns"]
                      if t["category"] == "interest"))
    # D4: summary line shows the bank's TRUE total (one charge, not two)
    if scn["id"] == "D4-duplicate-charge":
        dup = scn["faults"][0]["amount"]
        interest = r2(interest + dup)
    return dict(interest_total=interest,
                offset_credited=scn["actual"])


# ---------------------------------------------------------------- multi-account

def build_multi_account(outdir: Path):
    """R6: one CSV, two accounts; savings account linked only for days 0-44."""
    led_a = build_ledger(2001, START_2026, opening=18_300.00)
    led_b = build_ledger(2002, START_2026, opening=9_750.00)
    for t in led_b["txns"]:
        t["category"] = "offset"
    bal_a, bal_b = daily_balances(led_a), daily_balances(led_b)
    combined = {d: bal_a[d] + (bal_b[d] if (d - START_2026).days < 45 else 0.0)
                for d in bal_a}
    expected = calc_offset(combined, RATE, LOAN_BALANCE)
    fname = "R6-multi-account.csv"
    with open(outdir / fname, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Account", "Date", "Description", "Amount"])
        for label, led in (("OFFSET 062-001 8834 2210", led_a),
                           ("SAVINGS 062-001 1102 4455", led_b)):
            for t in led["txns"]:
                w.writerow([label, _fmt_date(t["date"], "dmy"),
                            t["desc"], f"{t['amount']:.2f}"])
    man = dict(
        id="R6-multi-account", scenario="Two accounts, one linked 45 days",
        file=fname, layout="multi-account",
        bank=dict(name=BANKS[1][0], bsb=BANKS[1][1], account=BANKS[1][2]),
        period=dict(start=START_2026.isoformat(),
                    end=(START_2026 + dt.timedelta(days=89)).isoformat(),
                    days=90),
        inputs=dict(interestRate=RATE, loanBalance=LOAN_BALANCE,
                    actualOffsetCredited=expected),
        expected=dict(
            transactionCount=len(led_a["txns"]) + len(led_b["txns"]),
            expectedOffset=expected, actualOffset=expected,
            difference=0.0, discrepancyPct=0.0, finding=FINDING_VERIFIED,
            letterOfDemand=None),
        faults=[],
        notes="Savings account must be date-limited to the first 45 days "
              "(or unticked). Only the linked balance offsets interest on a "
              "given day.",
    )
    (outdir / "R6-multi-account.csv.expected.json").write_text(
        json.dumps(man, indent=2))
    return man


# ---------------------------------------------------------------- assembly

def generate(outdir: Path):
    outdir.mkdir(parents=True, exist_ok=True)
    manifests = []
    scenarios = make_scenarios()
    totals = dict(files=0, txns=0, ledgers=len(scenarios) + 2)

    for scn in scenarios:
        led, txns, meta = scn["ledger"], scn["txns"], meta_for(scn)
        bank = BANKS[0]
        # primary trio: CSV (simple, dmy), XLSX, PDF
        jobs = [("csv", f"{scn['id']}.csv",
                 lambda p: render_csv_v1(p, led, txns), "primary", "simple"),
                ("xlsx", f"{scn['id']}.xlsx",
                 lambda p: render_xlsx(p, led, txns), "xlsx", "simple"),
                ("pdf", f"{scn['id']}.pdf",
                 lambda p: render_pdf(p, led, txns, bank, meta), "pdf", None)]
        # extra renderings for selected scenarios
        if scn["id"] == "D0-clean":
            jobs += [
                ("banklayout", "D0-clean-banklayout.csv",
                 lambda p: render_csv_v2(p, led, txns), "banklayout", "bank"),
                ("iso", "D0-clean-iso.csv",
                 lambda p: render_csv_v1(p, led, txns, date_style="iso"),
                 "iso", "simple-iso"),
                ("dollar", "D0-clean-dollar.csv",
                 lambda p: render_csv_v1(p, led, txns, money_style="dollar"),
                 "dollar", "simple-dollar"),
                ("exceldates", "D0-clean-exceldates.xlsx",
                 lambda p: render_xlsx(p, led, txns, excel_dates=True),
                 "exceldates", "simple-exceldates"),
                ("malformed", "D0-malformed.csv",
                 lambda p: render_csv_v1(p, led, txns, malformed=True),
                 "malformed", "simple-malformed"),
            ]
        if scn["id"] == "D1-underpayment":
            jobs += [
                ("txt", "D1-underpayment.txt",
                 lambda p: render_txt(p, led, txns, bank, meta), "txt", None),
                ("png", "D1-underpayment.png",
                 lambda p: render_png(p, led, txns, bank, meta), "png", None),
            ]
        for fmt, fname, fn, man_fmt, layout in jobs:
            fn(outdir / fname)
            man = build_manifest(scn, man_fmt, fname, layout)
            if layout == "simple-malformed":
                man["notes"] += (" File deliberately contains a blank line "
                                 "(row 11), a comment line (row 21) and a "
                                 "ragged junk row (row 31).")
                man["expected"]["malformedLines"] = 3
            (outdir / f"{fname}.expected.json").write_text(
                json.dumps(man, indent=2))
            manifests.append(man)
            totals["files"] += 1
            totals["txns"] += len(txns)

    manifests.append(build_multi_account(outdir))
    totals["files"] += 1
    totals["txns"] += manifests[-1]["expected"]["transactionCount"]

    write_index(outdir, manifests, totals)
    print(f"Generated {totals['files']} statement files "
          f"({totals['txns']} transactions across files, "
          f"{totals['ledgers']} unique ledgers) in {outdir}")


def write_index(outdir: Path, manifests: list, totals: dict):
    lines = ["# Fixture index", "",
             "| ID | File | Scenario | Finding | Expected offset | Actual | Δ |",
             "|----|------|----------|---------|----------------:|-------:|--:|"]
    for m in manifests:
        e = m["expected"]
        lines.append(
            f"| {m['id']} | {m['file']} | {m['scenario']} | {e['finding']} "
            f"| ${money(e['expectedOffset'])} | ${money(e['actualOffset'])} "
            f"| ${money(e['difference'])} |")
    lines += ["",
              f"**{totals['files']} statement files, "
              f"{totals['txns']} transactions across all files, "
              f"{totals['ledgers']} unique ledgers.**", "",
              "Each `<name>.expected.json` manifest records the user inputs "
              "and the exact outputs the tool must produce. See "
              "`../README.md` (tests) for usage."]
    (outdir / "INDEX.md").write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------- validation

def _parse_simple_csv(path: Path):
    """Re-parse a simple-layout CSV; returns (rows, malformed_line_count)."""
    rows, malformed = [], 0
    with open(path) as f:
        for i, rec in enumerate(csv.reader(f)):
            if i == 0:
                continue
            if not rec or (rec[0] or "").startswith("#"):
                malformed += 1
                continue
            if len(rec) < 3:
                malformed += 1
                continue
            raw = rec[2].replace("$", "").replace(",", "").strip()
            neg = raw.startswith("-")
            try:
                amt = float(raw.lstrip("-"))
            except ValueError:
                malformed += 1
                continue
            rows.append((rec[0], rec[1], -amt if neg else amt))
    return rows, malformed


def _parse_csv_date(s: str) -> dt.date:
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(s.strip(), fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unparseable date: {s!r}")


def _categorise(desc: str) -> str:
    if INTEREST_NARR in desc.upper():
        return "interest"
    if MORTGAGE_NARR in desc.upper():
        return "mortgage"
    return "offset"


def validate(outdir: Path) -> int:
    """Re-parse simple-layout CSV fixtures and recompute ground truth."""
    failures = 0
    for man_path in sorted(outdir.glob("*.expected.json")):
        man = json.loads(man_path.read_text())
        if not (man.get("layout") or "").startswith("simple") \
                or not man["file"].endswith(".csv"):
            continue
        rows, malformed = _parse_simple_csv(outdir / man["file"])
        e = man["expected"]
        start = dt.date.fromisoformat(man["period"]["start"])
        txns = [dict(date=_parse_csv_date(r[0]), desc=r[1], amount=r[2],
                     category=_categorise(r[1])) for r in rows]
        # recompute expected offset from what a parser would see
        led = dict(opening=man["expected"]["openingBalance"],
                   start=start, days=man["period"]["days"], txns=txns)
        recomputed = calc_offset(daily_balances(led),
                                 man["inputs"]["interestRate"],
                                 man["inputs"]["loanBalance"])
        expected_rows = e["transactionCount"]
        ok = recomputed == e["expectedOffset"] and len(rows) == expected_rows
        if man.get("layout") == "simple-malformed":
            ok = ok and malformed == e["malformedLines"]
        status = "OK " if ok else "FAIL"
        if not ok:
            failures += 1
        print(f"[{status}] {man['id']:<28} rows={len(rows):>3} "
              f"expectedOffset=${money(recomputed)} "
              f"(manifest ${money(e['expectedOffset'])})")
    print(f"\nValidation complete: {failures} failure(s)")
    return failures


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(Path(__file__).parent / "fixtures"))
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()
    outdir = Path(args.out)
    if args.validate:
        raise SystemExit(1 if validate(outdir) else 0)
    generate(outdir)


if __name__ == "__main__":
    main()
