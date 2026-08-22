# Fixture index

| ID | File | Scenario | Finding | Expected offset | Actual | Δ |
|----|------|----------|---------|----------------:|-------:|--:|
| D0-clean | D0-clean.csv | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-xlsx | D0-clean.xlsx | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-pdf | D0-clean.pdf | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-banklayout | D0-clean-banklayout.csv | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-iso | D0-clean-iso.csv | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-dollar | D0-clean-dollar.csv | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-exceldates | D0-clean-exceldates.xlsx | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D0-clean-malformed | D0-malformed.csv | Clean control (Verified) | Verified | $497.46 | $497.46 | $0.00 |
| D1-underpayment | D1-underpayment.csv | Underpayment 8% (Overcharge) | Overcharge | $520.84 | $479.17 | $41.67 |
| D1-underpayment-xlsx | D1-underpayment.xlsx | Underpayment 8% (Overcharge) | Overcharge | $520.84 | $479.17 | $41.67 |
| D1-underpayment-pdf | D1-underpayment.pdf | Underpayment 8% (Overcharge) | Overcharge | $520.84 | $479.17 | $41.67 |
| D1-underpayment-txt | D1-underpayment.txt | Underpayment 8% (Overcharge) | Overcharge | $520.84 | $479.17 | $41.67 |
| D1-underpayment-png | D1-underpayment.png | Underpayment 8% (Overcharge) | Overcharge | $520.84 | $479.17 | $41.67 |
| D2-wrong-rate | D2-wrong-rate.csv | Interest charged at 6.49% vs 5.99% | Review | $478.18 | $478.18 | $0.00 |
| D2-wrong-rate-xlsx | D2-wrong-rate.xlsx | Interest charged at 6.49% vs 5.99% | Review | $478.18 | $478.18 | $0.00 |
| D2-wrong-rate-pdf | D2-wrong-rate.pdf | Interest charged at 6.49% vs 5.99% | Review | $478.18 | $478.18 | $0.00 |
| D3-missing-transaction | D3-missing-transaction.csv | Deposit omitted from statement | Review | $424.39 | $466.93 | $-42.54 |
| D3-missing-transaction-xlsx | D3-missing-transaction.xlsx | Deposit omitted from statement | Review | $424.39 | $466.93 | $-42.54 |
| D3-missing-transaction-pdf | D3-missing-transaction.pdf | Deposit omitted from statement | Review | $424.39 | $466.93 | $-42.54 |
| D4-duplicate-charge | D4-duplicate-charge.csv | Interest charge duplicated | Review | $465.74 | $465.74 | $0.00 |
| D4-duplicate-charge-xlsx | D4-duplicate-charge.xlsx | Interest charge duplicated | Review | $465.74 | $465.74 | $0.00 |
| D4-duplicate-charge-pdf | D4-duplicate-charge.pdf | Interest charge duplicated | Review | $465.74 | $465.74 | $0.00 |
| D5-offset-cap | D5-offset-cap.csv | Offset balance above loan balance (capped) | Verified | $6,605.12 | $6,605.12 | $0.00 |
| D5-offset-cap-xlsx | D5-offset-cap.xlsx | Offset balance above loan balance (capped) | Verified | $6,605.12 | $6,605.12 | $0.00 |
| D5-offset-cap-pdf | D5-offset-cap.pdf | Offset balance above loan balance (capped) | Verified | $6,605.12 | $6,605.12 | $0.00 |
| D6-leap-year | D6-leap-year.csv | Leap-year divisor (bank used 366) | Review | $468.26 | $466.98 | $1.28 |
| D6-leap-year-xlsx | D6-leap-year.xlsx | Leap-year divisor (bank used 366) | Review | $468.26 | $466.98 | $1.28 |
| D6-leap-year-pdf | D6-leap-year.pdf | Leap-year divisor (bank used 366) | Review | $468.26 | $466.98 | $1.28 |
| R6-multi-account | R6-multi-account.csv | Two accounts, one linked 45 days | Verified | $532.53 | $532.53 | $0.00 |

**29 statement files, 2866 transactions across all files, 9 unique ledgers.**

Each `<name>.expected.json` manifest records the user inputs and the exact outputs the tool must produce. See `../README.md` (tests) for usage.
