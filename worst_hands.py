#!/bin/env python3
import json
from collections import defaultdict

def main():
    try:
        with open('poker_hands.json', 'r', encoding='utf-8') as f:
            hands_data = json.load(f)
    except FileNotFoundError:
        print("Error: poker_hands.json not found. Please run parser.py first.")
        return

    # Aggregate results by simplified hand
    # { 'AA': {'total_bb': 10.5, 'count': 5}, ... }
    stats = defaultdict(lambda: {'total_bb': 0.0, 'count': 0})

    for hand in hands_data:
        hero_hand = hand.get('hero_hand')
        if not hero_hand:
            continue
        
        simplified = hero_hand.get('simplified')
        net_result = hand.get('net_result_bb', 0.0)
        
        if simplified:
            stats[simplified]['total_bb'] += net_result
            stats[simplified]['count'] += 1

    # Convert to list for sorting
    summary = []
    for hand_type, data in stats.items():
        summary.append({
            'hand': hand_type,
            'total_bb': data['total_bb'],
            'count': data['count'],
            'avg_bb': data['total_bb'] / data['count'] if data['count'] > 0 else 0
        })

    # Sort by total_bb (worst to best)
    summary.sort(key=lambda x: x['total_bb'])

    print(f"Top 20 Worst Hands (by Total BB loss):")
    print(f"{'Hand':<6} | {'Total BB':>10} | {'Count':>6} | {'Avg BB':>8}")
    print("-" * 40)
    for s in summary[:20]:
        print(f"{s['hand']:<6} | {s['total_bb']:10.2f} | {s['count']:6d} | {s['avg_bb']:8.2f}")

    print("\n" + "="*40 + "\n")

    print(f"Top 20 Best Hands (by Total BB win):")
    print(f"{'Hand':<6} | {'Total BB':>10} | {'Count':>6} | {'Avg BB':>8}")
    print("-" * 40)
    for s in reversed(summary[-20:]):
        print(f"{s['hand']:<6} | {s['total_bb']:10.2f} | {s['count']:6d} | {s['avg_bb']:8.2f}")

if __name__ == "__main__":
    main()
