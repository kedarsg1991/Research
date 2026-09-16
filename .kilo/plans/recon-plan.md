# Recon — Bank & Invoice Reconciliation CLI for Freelancers

## Overview
A local CLI tool that imports bank statements and invoices, auto-matches payments to invoices by amount + date, flags unmatched transactions, categorizes expenses, and generates tax-ready reports. Everything runs offline on the user's machine — no server, no domain, no database.

## Target
- **Revenue goal**: $30/day (~₹3,000/day) = $900/month
- **Path**: ~47 paying users at $19/month, or ~75 at $12/month
- **Timeline**: Build MVP in 24 hours, launch immediately

## Constraints
- Zero upfront cost (no domain, no hosting, no database server)
- CLI/desktop format (not web app)
- User cannot write code — agent handles all implementation
- Online-only customer acquisition (no face-to-face)
- Freemium model (Option A: free tier with feature limits)

## Tech Stack
- **Language**: Python 3.x — gentlest learning curve, dominant in data/CSV processing
- **CLI Framework**: Click — decorator-based, beautiful `--help` output
- **Data Processing**: pandas — CSV handling, date parsing
- **Storage**: SQLite — local file database (zero infra, comes built into Python)
- **Payments**: Gumroad — handles payment processing + license key delivery (10% transaction fee)

## Product Name
**Recon** — short, memorable, evokes "reconciliation" without being clunky.

## Freemium Model

| Feature | Free | Pro ($19/mo or $199/yr) |
|---------|------|------------------------|
| Bank accounts | 1 | Unlimited |
| Invoice matching | Basic | Advanced (configurable date tolerance) |
| Reports | Text only | CSV + PDF export |
| Tax categorization | 5 common categories | All categories + custom |
| Support | Community | Priority email |

## Architecture

### Data Flow
1. User imports bank CSV + invoice CSV
2. Data stored in local SQLite database (`recon.db`)
3. Reconciliation engine matches payments to invoices by amount + date proximity (default ±3 days)
4. Unmatched transactions flagged for review
5. Reports generated as text, CSV, or PDF

### File Structure
```
recon/
├── recon.py              # Main CLI application (~400 lines)
├── requirements.txt      # Dependencies (click, pandas)
├── sample_bank.csv       # Test data
├── sample_invoices.csv   # Test data
├── README.md             # Usage instructions
├── PRODUCT.md            # Gumroad listing copy
└── LICENSES.md           # Free vs Pro feature gating
```

### CLI Commands
- `recon import <bank.csv> <invoices.csv>` — Import data
- `recon reconcile [--tolerance N]` — Match payments to invoices
- `recon report [--output file]` — Generate summary + export
- `recon summary` — Quick one-line overview
- `recon clear` — Reset database
- `recon activate <KEY>` — Unlock Pro features via license key

## Implementation Phases

### Phase 1: Core CLI (Hours 1-6)
- Create project structure
- Build Click CLI skeleton with all commands
- Implement SQLite database layer (bank_transactions, invoices, reconciliations tables)
- CSV import with column mapping and validation
- Basic reconciliation engine (amount + date matching)

### Phase 2: Features (Hours 7-12)
- Expense categorization (auto-detect by description keywords)
- Report generation (summary, category breakdown, unmatched items)
- CSV export
- License key activation system (free vs Pro gating)

### Phase 3: Polish (Hours 13-18)
- Beautiful `--help` text and error messages
- Multi-bank account support
- PDF report export (tax-ready format)
- Sample data for testing

### Phase 4: Launch (Hours 19-24)
- Create Gumroad product page
- Write PRODUCT.md listing copy
- Prepare Product Hunt launch post
- Create Reddit and Twitter distribution plan
- Test with sample data end-to-end

## Customer Acquisition (Online, Zero Cost)

### Phase 1: Product Hunt (Launch Day)
- Freelancers actively browse PH
- Well-timed launch = 200-500 visitors in 24 hours
- Even 5% conversion = 10-25 first paying users

### Phase 2: Reddit (Week 1)
- r/freelance, r/Entrepreneur, r/accounting, r/smallbusiness
- Post: "I built a CLI that reconciles bank statements with invoices in 10 minutes"
- Communities respond to builder stories, not ads

### Phase 3: Twitter/X (Ongoing)
- Freelancers vent about bookkeeping constantly
- Reply to those tweets with the tool
- Build in public — this is how indie founders find first users

### Phase 4: SEO (Months 1-3)
- Target: "how to reconcile freelance income", "expense tracking for freelancers", "tax deductions freelancer tool"
- Low competition, high intent keywords
- Simple blog posts ranking for 10+ keywords = steady user stream

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Low conversion from free to paid | Make Pro features genuinely valuable (PDF tax reports, multi-account) |
| Competition from established tools | Focus on freelancers specifically — generic tools don't understand freelance workflows |
| User acquisition slow | Start with Reddit/Twitter immediately, not wait for perfect product |
| License key cracking | Use offline validation with encrypted tokens; accept this risk for MVP |

## Validation Plan

1. **Test with sample data**: Run `recon import`, `recon reconcile`, `recon report` with provided CSVs
2. **Verify matching accuracy**: All 6 paid invoices should match to bank transactions
3. **Verify unmatched detection**: INV-1007 (PQR, $3,500, Unpaid) should appear as unmatched
4. **Verify category breakdown**: Software, Food, Income, Travel categories should be detected
5. **Verify Pro gating**: Free user sees limited features; Pro user sees all

## Open Questions
- [x] Product name: Recon
- [x] Freemium model: Option A (free tier with feature limits)
- [x] Payment processor: Gumroad
- [ ] Target pricing: $19/mo vs $199/yr vs other — recommend $19/mo with annual discount
- [ ] PDF library: reportlab (free) or fpdf2 (free) — recommend fpdf2