# ROI Calculator
## Data-Driven Marketing

---

## CORE Team Extension ROI

### Inputs

| Input | Value | Unit |
|-------|-------|------|
| Number of devs needed | [ ] | devs |
| Time to hire in-house | [ ] | months |
| Average senior dev salary | [ ] | EUR/year |
| Recruitment cost | [ ] | EUR/dev |
| Time to productivity | [ ] | months |
| Scalac hourly rate | [ ] | EUR/h |
| Project duration | [ ] | months |

### Calculations

**In-house Cost:**
```
Hiring time cost = Devs × (Hiring time / 12) × Salary
Recruitment cost = Devs × Recruitment cost per dev
Onboarding cost = Devs × (Time to productivity / 12) × Salary × 0.5
Total in-house = Hiring time cost + Recruitment cost + Onboarding cost
```

**Scalac Cost:**
```
Monthly cost = Devs × 160h × Hourly rate
Total Scalac = Monthly cost × Project duration
```

**ROI:**
```
Savings = Total in-house - Total Scalac
ROI % = (Savings / Total Scalac) × 100
```

### Example

| Input | Value |
|-------|-------|
| Devs needed | 5 |
| Time to hire | 6 months |
| Salary | 150k EUR |
| Recruitment | 20k EUR |
| Time to productivity | 3 months |
| Scalac rate | 80 EUR/h |
| Duration | 12 months |

**Results:**
- In-house cost: 562,500 EUR
- Scalac cost: 768,000 EUR
- **Wait... Scalac is more expensive?**

**But consider:**
- Time to first dev: 2 weeks vs 6 months
- Productivity from day 1 vs 3 months
- Replacement guarantee
- Knowledge transfer
- No management overhead

**Real ROI:**
- Time saved: 5.5 months
- Revenue protected: [Value of delivering on time]
- **True ROI: [Calculate based on business value]**

---

## AI Sovereign ROI

### Inputs

| Input | Value | Unit |
|-------|-------|------|
| Current OpenAI API monthly cost | [ ] | EUR |
| Projected scale (multipier) | [ ] | x |
| AI Act non-compliance risk | [ ] | % of revenue |
| Company revenue | [ ] | EUR |
| Failed POC cost | [ ] | EUR |
| Scalac project cost | [ ] | EUR |

### Calculations

**OpenAI at Scale:**
```
Future API cost = Current cost × Scale multiplier × 12 months
```

**Compliance Risk:**
```
Risk value = Company revenue × Non-compliance risk
```

**Total Cost of Doing Nothing:**
```
Cost = Future API cost + Risk value + Failed POC cost
```

**ROI:**
```
Savings = Cost of doing nothing - Scalac cost
ROI % = (Savings / Scalac cost) × 100
```

### Example (Bank)

| Input | Value |
|-------|-------|
| OpenAI cost | 10k EUR/m |
| Scale | 10x |
| Revenue | 100M EUR |
| Non-compliance risk | 6% |
| Failed POC | 200k EUR |
| Scalac cost | 500k EUR |

**Results:**
- OpenAI at scale: 1.2M EUR/year
- Compliance risk: 6M EUR
- Cost of doing nothing: 7.4M EUR
- Scalac cost: 500k EUR
- **Savings: 6.9M EUR**
- **ROI: 1,380%**

---

## CAC Calculator

### Inputs

| Input | CORE | AI |
|-------|------|-----|
| Marketing spend | [ ] | [ ] |
| Sales spend | [ ] | [ ] |
| SDR spend | [ ] | [ ] |
| Content spend | [ ] | [ ] |
| Leads generated | [ ] | [ ] |
| Customers acquired | [ ] | [ ] |

### Calculations

```
Total spend = Marketing + Sales + SDR + Content
CAC = Total spend / Customers acquired
CAC per lead = Total spend / Leads generated
```

### Target CAC

- CORE: < 10% of first year revenue
- AI: < 20% of first year revenue (higher margin)

---

## LTV Calculator

### Inputs

| Input | Value |
|-------|-------|
| Average deal size | [ ] EUR |
| Average project duration | [ ] months |
| Gross margin | [ ] % |
| Repeat rate | [ ] % |
| Average number of projects | [ ] |

### Calculations

```
LTV = Deal size × Number of projects × Gross margin
```

### LTV:CAC Ratio

```
Ratio = LTV / CAC
```

**Healthy ratio:** > 3:1

---

## 80/20 Balance Tracker

### Quarterly Review

| Metric | CORE Target | CORE Actual | AI Target | AI Actual |
|--------|-------------|-------------|-----------|-----------|
| Pipeline | 400k PLN | [ ] | 100k PLN | [ ] |
| Revenue | 320k PLN | [ ] | 80k PLN | [ ] |
| Deals | 8 | [ ] | 2 | [ ] |
| CAC | 15k PLN | [ ] | 50k PLN | [ ] |
| Margin | 20% | [ ] | 35% | [ ] |

**Balance:**
- Pipeline: [ ]% CORE / [ ]% AI
- Revenue: [ ]% CORE / [ ]% AI

**Adjustment needed?**
- [ ] Tak - increase CORE
- [ ] Tak - increase AI
- [ ] Nie - balance OK
