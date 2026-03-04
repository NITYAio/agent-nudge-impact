# X Thread — Agent Nudge Experiment Results

<!-- Fill in [BRACKETS] with actual results after running experiment -->

---

**Tweet 1 (Hook):**
I tested whether AI shopping agents — the ones now buying things inside ChatGPT and Perplexity — can be tricked by the same dark patterns that manipulate human shoppers.

Simple things: "Best Seller" badges. Fake urgency. Pre-selected defaults.

The results are alarming. 🧵

---

**Tweet 2 (Setup):**
I built a realistic product comparison page with 4 fictional headphones. One is objectively best (best specs, mid-price). One is objectively worst (worst specs, HIGHEST price).

The editorial review explicitly recommends the best and warns against the worst.

No ambiguity. Clear data.

---

**Tweet 3 (Method):**
Then I created 5 manipulated variants. Each changes ONE thing to nudge agents toward the worst product:

• Pre-selected checkbox
• Listed first instead of last
• "Most Popular" badge
• "Only 2 left! 15 viewing!"
• Fake ~~$349~~ $199 "43% OFF"

Same page. Same specs. Same review.

---

**Tweet 4 (Control baseline):**
Control results (clean page, no manipulation):

[X]% of the time, agents correctly picked the best product.

Good — they CAN read specs and make rational recommendations.

Now watch what happens with one small change…

---

**Tweet 5 (Worst manipulation):**
[MANIPULATION TYPE] nudge results:

[X]% of runs, agents recommended the WORST product — the one with the worst specs at the highest price.

[Include specific example of agent reasoning that was influenced]

---

**Tweet 6 (Heatmap):**
Full results across all 4 agents × 5 manipulations:

[Insert heatmap image]

[Key finding: which manipulation was most effective, which agent most susceptible]

---

**Tweet 7 (Why it matters):**
These aren't exotic attacks. I used a "Best Seller" badge and a pre-selected checkbox.

The same elements on every Amazon, Booking.com, and Shopify page.

And agents that are RIGHT NOW making purchase recommendations for millions of people fell for them.

---

**Tweet 8 (Corroboration):**
This matches independent research:

• MIT/Dartmouth: LLM agents accept defaults up to 100% of time regardless of quality
• Microsoft: First-proposal bias gives 10-30x advantage to speed over quality in marketplace simulations
• Root cause: RLHF training creates structural sycophancy

---

**Tweet 9 (Scale):**
McKinsey projects $3-5T in agent-mediated commerce by 2030.

Visa expects millions using agents to buy by holiday 2026.

ChatGPT Instant Checkout is live with 1M+ Shopify merchants TODAY.

We're handing purchasing power to systems that can be steered by a CSS class.

---

**Tweet 10 (What's missing):**
The payments infrastructure is being built fast — Visa, Mastercard, Stripe, Google all racing.

What NOBODY is building: the quality layer that ensures agent purchases are actually good.

Who watches the agent? Who catches the manipulation? Who resolves disputes when purchases fail?

---

**Tweet 11 (CTA):**
Full methodology, all test pages, raw data, and analysis scripts are open-source:

[GitHub repo link]

Replicate it. Test other agents. Test other manipulations. The more data we have, the harder this problem is to ignore.

---

**Tweet 12 (Blog link):**
Full writeup with detailed results, agent-by-agent breakdown, and what would actually fix this:

[Blog post link]
