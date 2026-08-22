# Tests — synthetic statement fixtures

Ground-truth-first fixtures for testing the Offsetcheck auditor (`check.html`).

## Layout

- `generate_fixtures.py` — the generator. Builds synthetic ledgers, computes
  ground truth (daily balances, expected offset via the daily-balance method,
  rate ÷ 365, capped at the loan balance), injects controlled faults, and
  renders statements to CSV, XLSX, PDF, TXT and PNG.
- `fixtures/` — 29 statement files (2,866 transactions across files, 9 unique
  ledgers), each paired with a `<file>.expected.json` manifest.
- `fixtures/INDEX.md` — one-line summary of every fixture and its expected
  finding.

## Usage

```bash
python3 tests/generate_fixtures.py              # regenerate fixtures/
python3 tests/generate_fixtures.py --validate   # re-parse CSVs, recompute ground truth
```

`--validate` re-parses every simple-layout CSV and independently recomputes
the expected offset benefit and transaction count, failing if the rendered
file no longer matches its manifest. Run it after touching the generator.

## Scenarios

| ID | Scenario | Expected finding |
|----|----------|------------------|
| D0 | Clean control | Verified |
| D1 | Bank credits 92% of expected offset | Overcharge (+ letter of demand figures) |
| D2 | Interest charged at 6.49% vs 5.99% entered | Review (excess interest quantified) |
| D3 | Salary deposit omitted from statement | Review (balance break = deposit amount) |
| D4 | Interest charge duplicated (summary shows true total) | Review (count/total mismatch) |
| D5 | Offset balance above loan balance | Verified (benefit capped at amount owing) |
| D6 | Bank used a 366-day divisor in leap-year 2028 | Review (systematic shortfall) |
| R6 | Two accounts; savings linked only for first 45 days | Verified (with date-limiting) |

Format/robustness variants: bank-layout CSV (Debit/Credit/Balance), ISO and
DD/MM/YYYY dates, `$`-and-comma amounts, Excel serial dates, malformed CSV
(blank/comment/ragged lines), TXT and PNG renderings of the D1 ledger.

## Conventions

- All data is fictional. Banks: Meridian Mutual Bank, Coastline Credit Union,
  Wattle & Stone Bank. No real BSBs, account numbers, or personal data.
- Manifests record the user inputs (`interestRate`, `loanBalance`,
  `actualOffsetCredited`) and the exact expected outputs: transaction counts,
  interest totals, expected/actual offset, difference, discrepancy %, finding
  tier, and — for Overcharge — the letter-of-demand figures.
- Finding tiers follow the brand style guide: Verified / Review / Overcharge
  (Review tolerance: discrepancy ≤ 1% of expected).
- Seeds are fixed; regeneration is byte-stable except where a renderer
  embeds no timestamps (PDF metadata may vary).
