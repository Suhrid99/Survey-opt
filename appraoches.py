import pandas as pd
import numpy as np
from math import ceil
import random
import warnings
warnings.filterwarnings('ignore')

BUFFER = 1.35
TIME_BUDGET = 480
TARGET = 200
N_SIMULATIONS = 1000

df = pd.read_csv('fake_category_data.csv')
df['expected_time'] = df['incidence_rate'] * df['category_length_seconds']
naive_total = int(df.apply(lambda r: ceil(TARGET / r['incidence_rate']), axis=1).sum())

def smart_greedy(df, buffer=BUFFER):
    df = df.copy().sort_values('incidence_rate', ascending=True).reset_index(drop=True)
    structures = []
    for _, row in df.iterrows():
        cat = {'id': row['category_id'], 'name': row['category_name'],
               'incidence': row['incidence_rate'], 'length': row['category_length_seconds'],
               'expected_time': row['expected_time']}
        best_structure, best_score = None, float('inf')
        for structure in structures:
            current_time = sum(c['expected_time'] for c in structure['categories'])
            if current_time + cat['expected_time'] <= TIME_BUDGET:
                current_min = min(c['incidence'] for c in structure['categories'])
                score = current_min - min(current_min, cat['incidence'])
                if score < best_score:
                    best_score, best_structure = score, structure
        if best_structure:
            best_structure['categories'].append(cat)
        else:
            structures.append({'categories': [cat]})
    for s in structures:
        s['respondents'] = ceil(TARGET / min(c['incidence'] for c in s['categories']) * buffer)
    return structures, sum(s['respondents'] for s in structures)

def incidence_banding(df, bands=[(0, 0.3), (0.3, 0.5), (0.5, 0.7), (0.7, 1.0)], buffer=BUFFER):
    df = df.copy()
    structures = []
    for low, high in bands:
        band_df = df[(df['incidence_rate'] >= low) & (df['incidence_rate'] < high)]
        if band_df.empty:
            continue
        band_df = band_df.sort_values('expected_time', ascending=False)
        current_cats, current_time = [], 0
        for _, row in band_df.iterrows():
            cat = {'id': row['category_id'], 'name': row['category_name'],
                   'incidence': row['incidence_rate'], 'length': row['category_length_seconds'],
                   'expected_time': row['expected_time']}
            if current_time + cat['expected_time'] <= TIME_BUDGET:
                current_cats.append(cat)
                current_time += cat['expected_time']
            else:
                if current_cats:
                    structures.append({'categories': current_cats.copy(),
                                       'respondents': ceil(TARGET / min(c['incidence'] for c in current_cats) * buffer)})
                current_cats, current_time = [cat], cat['expected_time']
        if current_cats:
            structures.append({'categories': current_cats.copy(),
                               'respondents': ceil(TARGET / min(c['incidence'] for c in current_cats) * buffer)})
    return structures, sum(s['respondents'] for s in structures)

def simulated_annealing(df, n_iterations=500, buffer=BUFFER):
    categories = [{'id': r['category_id'], 'name': r['category_name'], 'incidence': r['incidence_rate'],
                   'length': r['category_length_seconds'], 'expected_time': r['expected_time']} 
                  for _, r in df.iterrows()]
    
    def calculate_cost(structures):
        return sum(ceil(TARGET / min(c['incidence'] for c in s['categories']) * buffer) for s in structures)
    
    def build_structures(cat_order):
        structures, current_cats, current_time = [], [], 0
        for cat in cat_order:
            if current_time + cat['expected_time'] <= TIME_BUDGET:
                current_cats.append(cat)
                current_time += cat['expected_time']
            else:
                if current_cats:
                    structures.append({'categories': current_cats.copy()})
                current_cats, current_time = [cat], cat['expected_time']
        if current_cats:
            structures.append({'categories': current_cats.copy()})
        return structures
    
    best_order = sorted(categories, key=lambda x: x['incidence'])
    best_structures = build_structures(best_order)
    best_cost = calculate_cost(best_structures)
    current_order, current_cost = best_order.copy(), best_cost
    
    for i in range(n_iterations):
        temp = 1.0 - (i / n_iterations)
        new_order = current_order.copy()
        idx1, idx2 = random.sample(range(len(new_order)), 2)
        new_order[idx1], new_order[idx2] = new_order[idx2], new_order[idx1]
        new_structures = build_structures(new_order)
        new_cost = calculate_cost(new_structures)
        if new_cost < current_cost or random.random() < temp * 0.3:
            current_order, current_cost = new_order, new_cost
            if new_cost < best_cost:
                best_cost, best_structures, best_order = new_cost, new_structures, new_order
    
    for s in best_structures:
        s['respondents'] = ceil(TARGET / min(c['incidence'] for c in s['categories']) * buffer)
    return best_structures, best_cost

def validate(structures, df, n_sims=N_SIMULATIONS):
    all_cat_ids = set(df['category_id'].tolist())
    success_count, total_times = 0, []
    for _ in range(n_sims):
        qualified = {cid: 0 for cid in all_cat_ids}
        total_time, total_resp = 0, 0
        for s in structures:
            for _ in range(s['respondents']):
                resp_time = 0
                for cat in s['categories']:
                    if random.random() < cat['incidence']:
                        qualified[cat['id']] += 1
                        resp_time += cat['length']
                total_time += resp_time
                total_resp += 1
        if total_resp > 0:
            total_times.append(total_time / total_resp)
        if all(qualified.get(cid, 0) >= TARGET for cid in all_cat_ids):
            success_count += 1
    return success_count / n_sims, np.mean(total_times) if total_times else 0

s1, c1 = smart_greedy(df)
s2, c2 = incidence_banding(df)
s3, c3 = simulated_annealing(df)

sr1, mt1 = validate(s1, df)
sr2, mt2 = validate(s2, df)
sr3, mt3 = validate(s3, df)

results = pd.DataFrame({
    'Approach': ['Smart Greedy', 'Incidence Banding', 'Simulated Annealing', 'Naive'],
    'Cost': [c1, c2, c3, naive_total],
    'Success': [f"{sr1:.1%}", f"{sr2:.1%}", f"{sr3:.1%}", "-"],
    'Time': [f"{mt1:.1f}s", f"{mt2:.1f}s", f"{mt3:.1f}s", "-"],
    'Savings': [f"{(1-c1/naive_total)*100:.1f}%", f"{(1-c2/naive_total)*100:.1f}%", 
                f"{(1-c3/naive_total)*100:.1f}%", "0%"]
}).sort_values('Cost').reset_index(drop=True)

print(results.to_string(index=False))
