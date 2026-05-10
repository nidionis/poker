#!/usr/bin/env python3
import json


def calculate_maximum_stats(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File {json_file_path} not found.")
        return
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {json_file_path}.")
        return

    if not data:
        print("No data found in JSON.")
        return

    # Initialize stats with extreme low values
    max_stats = {
        "max_net_result_bb": {"value": float('-inf'), "hand_id": None},
        "max_total_pot_bb": {"value": float('-inf'), "hand_id": None},
        "max_rake_bb": {"value": float('-inf'), "hand_id": None},
        "max_roi_pct": {"value": float('-inf'), "hand_id": None}
    }

    total_roi_sum = 0.0
    roi_count = 0

    for hand in data:
        net_result = hand.get("net_result_bb", 0.0)
        summary = hand.get("summary", {})
        total_pot = summary.get("total_pot_bb", 0.0)
        rake = summary.get("rake_bb", 0.0)
        
        # Find hero's starting stack from players_bb
        hero_name = hand.get("hero_hand", {}).get("player")
        hero_stack = 0.0
        for player in hand.get("players_bb", []):
            if player.get("name") == hero_name:
                hero_stack = player.get("stack_bb", 0.0)
                break

        # ROI Calculation: (stack + net_result_bb) * 100 / stack
        if hero_stack > 0:
            roi = ((hero_stack + net_result) * 100) / hero_stack
            total_roi_sum += roi
            roi_count += 1
            if roi > max_stats["max_roi_pct"]["value"]:
                max_stats["max_roi_pct"] = {"value": roi, "hand_id": hand.get("hand_id")}

        # Check net result
        if net_result > max_stats["max_net_result_bb"]["value"]:
            max_stats["max_net_result_bb"] = {"value": net_result, "hand_id": hand.get("hand_id")}

        # Check total pot
        if total_pot > max_stats["max_total_pot_bb"]["value"]:
            max_stats["max_total_pot_bb"] = {"value": total_pot, "hand_id": hand.get("hand_id")}

        # Check rake
        if rake > max_stats["max_rake_bb"]["value"]:
            max_stats["max_rake_bb"] = {"value": rake, "hand_id": hand.get("hand_id")}

    # Display results
    print("--- Maximum Statistics ---")
    print(
        f"Biggest Net Win: {max_stats['max_net_result_bb']['value']:.2f} BB (Hand: {max_stats['max_net_result_bb']['hand_id']})")
    print(
        f"Biggest Pot:     {max_stats['max_total_pot_bb']['value']:.2f} BB (Hand: {max_stats['max_total_pot_bb']['hand_id']})")
    print(f"Highest Rake:    {max_stats['max_rake_bb']['value']:.2f} BB (Hand: {max_stats['max_rake_bb']['hand_id']})")
    print(f"Highest ROI:     {max_stats['max_roi_pct']['value']:.2f}% (Hand: {max_stats['max_roi_pct']['hand_id']})")
    
    avg_roi = total_roi_sum / roi_count if roi_count > 0 else 0
    print(f"Average ROI:     {avg_roi:.2f}%")


if __name__ == "__main__":
    calculate_maximum_stats('poker_hands.json')