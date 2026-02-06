# Survey Structure Optimization

This project answers one question:

> How do I get 200 qualified respondents per category without accidentally surveying the entire country?

The naive approach runs each category independently. That looks harmless until it quietly asks for **40,916 respondents**. At that point it stops being a survey and starts being population research.

Instead, I group categories into shared survey structures so a single respondent can qualify for multiple categories in one session. Same guarantees, less duplication, and far fewer "why is this so expensive" conversations.

Each structure’s cost is driven by its **lowest-incidence category**. One rare category can blow up the entire group, so I handle low-incidence (expensive) categories first and place them where they increase cost the least.

---

## Approach

I tested three strategies for grouping categories under a **480s time budget** while guaranteeing **200 qualified respondents per category**.

### Smart Greedy  
Sort categories by lowest incidence and place each where it causes the smallest increase in total respondents.  
Low-incidence categories are the real cost drivers, so dealing with them first minimizes waste.

### Simulated Annealing  
Start with a sensible ordering and randomly swap categories, occasionally accepting worse moves to escape local minima.  
More exploratory, but in practice it slightly underperforms the greedy approach.

### Incidence Banding  
Bucket categories into fixed incidence ranges and pack within bands.  
Simple and interpretable, but rigid bands leave savings on the table.

---

## Validation

All solutions are validated using **1,000 Monte Carlo simulations** to ensure:

- Every category reaches **200 qualified respondents**
- Average interview time stays under **480 seconds**
- Delivery is stable under random qualification noise

A **1.35 buffer** is applied so randomness does not cause under-delivery.

---

## EDA Summary [eda.py](https://github.com/Suhrid99/Survey-opt/blob/main/eda.py)

1. **The cost distribution is extreme** — Fertility/IVF (5% incidence) needs 2,000 respondents alone. The bottom 10 categories need more respondents than the top 50 combined.

2. **Incidence and survey length are independent** (r = -0.05) — I assumed niche categories would have longer surveys. They don't. This means we can group purely by incidence without worrying about time conflicts.

3. **Multiple structures are unavoidable** — Total expected time (~3,500s) far exceeds the 480s budget. This confirmed the need for multiple survey structures, not one mega-survey.

4. **Low-incidence categories are cost-expensive but time-cheap** — Fertility/IVF costs 2,000 respondents but only ~15s expected time. High-incidence categories (Kitchenware, Breakfast) are the opposite: ~120s time, ~250 respondents. This tradeoff meant I could pack many low-incidence categories together without hitting the time limit.

5. **Problem is dominated by outliers** — Optimizing for the bottom 15 low-incidence categories specifically (processing them first) beats generic optimization approaches.

---

## Results

| Approach            | Cost  | Success | Time   | Savings |
|---------------------|------:|:-------:|:------:|:-------:|
| Smart Greedy        | 6,955 | 100%    | 459.5s | 83.0%   |
| Simulated Annealing | 7,014 | 100%    | 448.0s | 82.9%   |
| Incidence Banding   | 7,921 | 100%    | 397.4s | 80.6%   |
| Naive               | 40,916|   –     |   –    | 0%      |

---

