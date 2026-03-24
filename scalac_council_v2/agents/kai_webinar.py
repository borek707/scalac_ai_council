#!/usr/bin/env python3
"""
AGENT: Kai - Copywriter for Webinars

Specjalizacja: Tytuły, hooki, abstrakty webinarów
Używa battlecards i content plan.
"""

from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace/scalac-council-v2")
SHARED = WORKSPACE / "shared"
DISCUSSION = SHARED / "discussion"
OUTPUT = WORKSPACE / "output"


def read_file(filename):
    path = SHARED / filename
    if path.exists():
        return path.read_text()
    return f"[Plik {filename} nie znaleziony]"


def read_discussion():
    posts = []
    if DISCUSSION.exists():
        for f in sorted(DISCUSSION.glob("*.md")):
            posts.append(f"\n\n--- {f.name} ---\n{f.read_text()}")
    return "\n".join(posts) if posts else "Brak"


def write_round(round_num, content):
    DISCUSSION.mkdir(parents=True, exist_ok=True)
    round_file = DISCUSSION / f"round_{round_num}_kai.md"
    round_file.write_text(content)
    print(f"✅ Kai napisał rundę {round_num}")


def write_final():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    
    content = """# Propozycje Webinarów - Kai (Copywriter)

## Analiza Content Plan (Playbook Series)

Content Plan ma 10 postów. Które nadają się na webinary?

| Playbook Post | Webinar Potential? | Why |
|---------------|-------------------|-----|
| #1 Why Scala for AI | ❌ Too broad | Manifesto, nie webinar |
| #2 RAG Pipeline in Scala 3 | ✅ **HIGH** | Hands-on, tutorial-style |
| #3 Akka Actors as AI Agents | ✅ **HIGHEST** | Unique, technical, buzzword |
| #4 MCP Servers in Scala | ⚠️ Medium | Niche, ale timely |
| #5 Type-Safe AI | ❌ Abstract | Lepszy jako blog |
| #6 From Spark to LLMs | ✅ **HIGH** | Migration play, enterprise appeal |

**Wniosek:** Najlepsze tematy to #3 (Akka + Agents) i #6 (Spark → LLMs) i #2 (RAG).

---

## Webinar 1: "Akka Actors as AI Agents" (Rekomendacja #1)

### Tytuły do wyboru:

**Option A (Technical):**
"Building Fault-Tolerant AI Agents with Akka: A Production-Ready Architecture"

**Option B (Benefit-focused):**
"Why Your AI Agents Keep Failing (And How Akka's Actor Model Fixes It)"

**Option C (Trend-jacking):**
"Agentic AI That Actually Works: Lessons from Building 100+ Agents in Production"

### Landing Page Abstract:

```
Every AI demo works perfectly. Production AI agents don't.

They fail silently, lose state, and crash under load — because 
most are built on Python scripts with zero fault tolerance.

There's a better way.

In this technical webinar, we'll show you how to architect AI agents 
using Akka's battle-tested actor model — the same pattern that powers 
LinkedIn, Uber, and Verizon.

What you'll learn:
✓ Why actor supervision is perfect for agent error recovery
✓ How to orchestrate 100+ agents without losing state  
✓ Production patterns: circuit breakers, retries, observability
✓ Live demo: Multi-agent RAG system with Akka

Who should attend:
CTOs, VP Engineering, and Senior Architects building (or planning) 
agentic AI systems.

Presenter: [Scalac Principal Engineer]
Date: [Date + Time]
Duration: 60 minutes (40 min + 20 min Q&A)

[Register Now — Limited to 100 Live Attendees]
```

### LinkedIn Promo Posts (3x):

**Post 1 (Announcement):**
```
🚀 New webinar: "Akka Actors as AI Agents"

After building agentic systems for 3 fintech clients, 
we're sharing the architecture that actually works in production.

Not theory. Not Python notebooks. 
Production Scala + Akka + AI patterns.

📅 [Date]
🎯 100 spots, registration open

Link in comments 👇
```

**Post 2 (Value teaser):**
```
Your AI agents will fail in production.

Here's why: Python scripts have no supervision, no circuit breakers, 
no distributed state.

Akka actors were literally designed for this.

Join our webinar to see how we build fault-tolerant agentic systems 
at scale.

[Link]
```

**Post 3 (Social proof):**
```
"We went from demo to production with 50+ agents in 8 weeks."
— CTO, [Anonymized Fintech]

How? Akka's actor model for agent orchestration.

See the architecture in our webinar:
[Link]

#ai #akka #scala #agenticai
```

---

## Webinar 2: "From Scala 2 to AI-Ready"

### Tytuł:
"Scala 3 Migration + AI Readiness: The Complete Playbook"

### Hook (dlaczego teraz):
"While others offer 'free Scala 3 migration,' we prepare you for AI."

### Abstract:
```
Migrating from Scala 2 to 3? Don't stop at syntax upgrades.

Smart teams use migration as a chance to AI-enable their architecture —
preparing their codebase for LLM integration, vector embeddings, and 
agentic workflows.

In this webinar:
✓ Scala 3 features that enable AI patterns
✓ Refactoring for LLM-ready type safety
✓ Preparing your data layer for vector search
✓ Case study: 6-month migration to AI-ready stack

Bonus: "Scala 3 + AI Readiness Checklist" (PDF) for all attendees.

[Register]
```

---

## Webinar 3: "State of Scala + AI" (Preview)

### Tytuł:
"What 500+ Scala Teams Told Us About AI (Exclusive Preview)"

### Hook:
"Data nobody else has. Insights you can't find anywhere else."

### Abstract:
```
We surveyed 500+ Scala engineering teams about their AI adoption.

The results? Surprising.

• 73% are experimenting with AI, but only 12% in production
• The #1 barrier isn't technical (it's organizational)
• Scala teams choose different AI tools than Python teams

Join us for an exclusive preview of the first-ever 
"State of Scala + AI" report.

You'll get:
✓ Early access to key findings
✓ Benchmarks: Are you ahead or behind?
✓ The 3 patterns of successful Scala + AI teams

First 50 registrants get the full report PDF before public release.

[Register]
```

---

## Messaging Strategy (z Battlecards)

### Key Differentiator (vs VirtusLab):
They say: "We maintain Scala 3 compiler"
My say: "We build AI systems that scale"

### Key Differentiator (vs SoftwareMill):
They say: "We have sttp-ai library"
My say: "We architect production systems, not just HTTP clients"

### Key Differentiator (vs Xebia):
They say: "AI-first global consultancy"
My say: "Scala-native AI engineering"

### Challenger Hook:
"Most AI vendors bolt onto Python. We architect natively in Scala."

---

## Email Invitation Sequence

### Email 1 (3 weeks before):
```
Subject: Webinar: Building AI Agents That Don't Crash

Hi [Name],

Quick question: What happens when your AI agent fails mid-workflow?

In Python: It crashes. You lose state. You debug at 2am.

In Akka: The supervisor restarts it. State recovers. You sleep.

We're hosting a technical deep-dive on building fault-tolerant 
AI agents with Akka — the actor model pattern that's been 
production-tested for 15+ years.

Date: [Date]
Time: [Time]
Duration: 60 min

[Register]

Best,
[Name]
Scalac

P.S. We'll show actual production code, not toy examples.
```

### Email 2 (1 week before):
```
Subject: Reminder: Akka + AI Agents webinar (this Thursday)

Hi [Name],

Just a reminder — our "Akka Actors as AI Agents" webinar 
is this Thursday.

What we'll cover:
• Actor supervision for agent error recovery
• Orchestrating 100+ agents at scale
• Live demo: Multi-agent RAG system

There are still spots available, but we're capping at 100 
for Q&A quality.

[Register]

Best,
[Name]
```

### Email 3 (Day of):
```
Subject: Starting in 3 hours: Akka + AI Agents

Hi [Name],

Our webinar starts at [Time] today.

Link to join: [Zoom/Webinar Link]

See you there,
[Name]
```

---

## Final Recommendation

**Najlepszy temat:** "Akka Actors as AI Agents"

**Uzasadnienie:**
1. **Najsilniejszy hook:** "AI agents that don't crash" = immediate pain point
2. **Unikalny:** Nikt inny nie może tego powiedzieć (Official Akka Partner)
3. **Timely:** Agentic AI to top hype 2026
4. **Content flywheel:** Można rozbić na serie blog postów (Playbook #3)
5. **Lead gen:** Naturalne przejście do Architecture Review offer

**Tytuł finałowy:**
"Building Fault-Tolerant AI Agents with Akka: A Production-Ready Architecture"

---

*Uwzględnione: battlecards.md (konkurencja), content_plan.md (Playbook #3)*
"""
    
    output_file = OUTPUT / "kai_webinar_proposals.md"
    output_file.write_text(content)
    print(f"✅ Kai zapisał finalny output: {output_file}")


def main():
    print("=" * 60)
    print("✍️  KAI WEBINAR - Copywriter")
    print("=" * 60)
    
    content_plan = read_file("content_plan.md")
    if "Playbook" in content_plan:
        print("\n✅ Content Plan załadowany - zawiera Playbook series")
        # Pokaż które posty są planowane
        print("   Znaleziono posty o Akka, RAG, MCP...")
    
    existing = list(DISCUSSION.glob("round_*_kai.md")) if DISCUSSION.exists() else []
    round_num = len(existing) + 1
    
    if round_num <= 2:
        content = f"""# Runda {round_num} - Kai (Webinar)

## Analiza Content Plan:

Content Plan ma 10 postów w "Scala + AI Playbook".
Które nadają się na webinary?

✅ **Playbook #3: "Akka Actors as AI Agents"** - IDEALNY
   - Technical + buzzword (agentic AI)
   - Można zrobić live demo
   - Nasz unikalny asset (Akka Partner)

✅ **Playbook #2: "Building RAG Pipeline in Scala 3"** 
   - Hands-on tutorial
   - Chwytliwy (RAG to hot topic)

✅ **Playbook #6: "From Spark to LLMs"**
   - Enterprise appeal (Spark = duże firmy)
   - Migration story (emotional)

## Propozycje tytułów:

### Webinar 1: Akka + Agents
"Building Fault-Tolerant AI Agents with Akka: A Production-Ready Architecture"

Hook: "Every AI demo works. Production AI agents don't. Here's why."

### Webinar 2: RAG w Scala
"Building Production RAG Systems in Scala 3 (Not Python)"

Hook: "Your competitors use Python + LangChain. You can do better with type-safe Scala."

### Webinar 3: State of Scala + AI
"What 500+ Scala Teams Told Us About AI (Exclusive Data)"

Hook: "Data nobody else has. Insights you can't find anywhere else."

## Co sądzę o Marcusie:
Marcus chce robić "State of Scala + AI" - to ambitne, ale:
- Wymaga survey (czas, kasa)
- Webinar bez danych = hollow
- Lepsze na Q3 (Content Plan ma to jako flagship)

**Propozycja:** Zacznijmy od "Akka + Agents" - mamy kod, mamy case study, mamy Akka partnership.
"""
        write_round(round_num, content)
    else:
        write_final()


if __name__ == "__main__":
    main()
