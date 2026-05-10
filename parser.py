#!/bin/env python3
# !/bin/env python3
import os
import re
import json
import argparse
from typing import List, Dict, Optional


class Hand:
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.bb_value = self._extract_bb_value()
        self.data = self._parse()

    def _rank_value(self, rank_char: str) -> int:
        ranks = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13,
                 'A': 14}
        return ranks.get(rank_char, 0)

    def _analyze_board(self, hero_cards: List[str], board: List[str]) -> Dict:
        """Analyzes the board for draws and made hands."""
        if not board:
            return {}

        hero_ranks = [self._rank_value(c[0]) for c in hero_cards]
        hero_suits = [c[1] for c in hero_cards]
        board_ranks = [self._rank_value(c[0]) for c in board]
        board_suits = [c[1] for c in board]

        # Sort board ranks for comparison
        board_ranks.sort(reverse=True)

        # Check for flush draws (simplified)
        suits_on_board = {s: board_suits.count(s) for s in set(board_suits)}
        has_flush_draw = any(count >= 2 and hero_suits.count(s) >= 1 for s, count in suits_on_board.items())

        # Simple made hand logic
        made_hand = "high_card"
        if len(set(hero_ranks + board_ranks)) < len(hero_ranks + board_ranks):
            # Potential pairs or sets
            if len(set(hero_ranks)) == 1 and hero_ranks[0] in board_ranks:
                made_hand = "set"
            elif any(r in board_ranks for r in hero_ranks):
                # Determine Pair Type
                match_rank = next((r for r in hero_ranks if r in board_ranks), None)
                if match_rank == board_ranks[0]:
                    made_hand = "top_pair"
                elif len(board_ranks) > 1 and match_rank == board_ranks[1]:
                    made_hand = "second_pair"
                else:
                    made_hand = "third_or_lower_pair"

        return {
            "flush_draw": has_flush_draw,
            "made_hand": made_hand
        }

    def _extract_bb_value(self) -> float:
        match = re.search(r"Holdem no limit \(([\d\.]+)€\/([\d\.]+)€\)", self.raw_text)
        return float(match.group(2)) if match else 1.0

    def _parse(self) -> Dict:
        players = self._extract_players()
        hero_hand = self._extract_hero_hand()
        summary = self._extract_summary()

        # Calculate result (winnings - investments)
        hero_name = "timeWaster"
        invested = 0.0
        winnings = 0.0

        # Extract investments
        # Blinds and Antes
        blind_matches = re.findall(rf"{hero_name} posts (?:small blind|big blind|ante) ([\d\.]+)€", self.raw_text)
        for amount in blind_matches:
            invested += float(amount)

        # Pre-flop and Post-flop actions
        # "raises 0.03€ to 0.05€" -> we take the first amount 0.03€ as the additional investment
        # "calls 0.02€"
        # "bets 0.04€"
        action_matches = re.findall(rf"{hero_name} (?:calls|bets|raises) ([\d\.]+)€", self.raw_text)
        for amount in action_matches:
            invested += float(amount)

        # Extract winnings
        # "timeWaster collected 0.07€ from pot"
        win_match = re.search(rf"{hero_name} collected ([\d\.]+)€ from pot", self.raw_text)
        if win_match:
            winnings = float(win_match.group(1))

        board_analysis = {}
        if hero_hand and summary['board']['flop']:
            board_analysis = self._analyze_board(hero_hand['raw_cards'], summary['board']['flop'])

        return {
            "hand_id": self._extract_hand_id(),
            "timestamp": self._extract_timestamp(),
            "table": self._extract_table(),
            "players_bb": [{"name": p['name'], "stack_bb": p['stack'] / self.bb_value} for p in players],
            "hero_hand": hero_hand,
            "summary": summary,
            "board_analysis": board_analysis,
            "net_result_bb": (winnings - invested) / self.bb_value
        }

    def _extract_hand_id(self) -> str:
        match = re.search(r"HandId: #([A-Za-z0-9-]+)", self.raw_text)
        if match:
            return match.group(1)
        # Fallback if HandId: was consumed by split
        match = re.search(r"^ #([A-Za-z0-9-]+)", self.raw_text)
        return match.group(1) if match else "unknown"

    def _extract_timestamp(self) -> str:
        match = re.search(r"- (\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2} UTC)", self.raw_text)
        return match.group(1) if match else "unknown"

    def _extract_table(self) -> str:
        match = re.search(r"Table: '([^']+)'", self.raw_text)
        return match.group(1) if match else "unknown"

    def _extract_players(self) -> List[Dict]:
        players = []
        # Only look for players in the initial section, before actions start
        initial_section = self.raw_text.split("***")[0]
        player_lines = re.findall(r"Seat \d+: (.+) \((\d+\.?\d*)€\)", initial_section)
        for name, stack in player_lines:
            players.append({"name": name, "stack": float(stack)})
        return players

    def _simplify_hand(self, cards: List[str]) -> Dict:
        parsed_cards = []
        for card in cards:
            parsed_cards.append({"rank": card[0], "suit": card[1], "value": self._rank_value(card[0])})
        parsed_cards.sort(key=lambda x: x['value'], reverse=True)
        return {
            "raw_cards": cards,
            "simplified": f"{parsed_cards[0]['rank']}{parsed_cards[1]['rank']}{'s' if parsed_cards[0]['suit'] == parsed_cards[1]['suit'] else 'o'}"
        }

    def _extract_hero_hand(self) -> Optional[Dict]:
        match = re.search(r"Dealt to (\w+) \[(.*?)\]", self.raw_text)
        if match:
            return {"player": match.group(1), **self._simplify_hand(match.group(2).split())}
        return None

    def _extract_summary(self) -> Dict:
        pot_match = re.search(r"Total pot (\d+\.?\d*)€", self.raw_text)
        rake_match = re.search(r"Rake (\d+\.?\d*)€", self.raw_text)
        board_match = re.search(r"Board: \[(.*?)\]", self.raw_text)

        board = board_match.group(1).split() if board_match else []

        return {
            "total_pot_bb": (float(pot_match.group(1)) / self.bb_value) if pot_match else 0.0,
            "rake_bb": (float(rake_match.group(1)) / self.bb_value) if rake_match else 0.0,
            "board": {
                "flop": board[0:3] if len(board) >= 3 else [],
                "turn": board[3] if len(board) >= 4 else None,
                "river": board[4] if len(board) >= 5 else None
            }
        }

    def to_dict(self) -> Dict:
        return self.data


def parse_directory(directory: str) -> List[Dict]:
    parsed_hands = []
    if not os.path.isdir(directory):
        print(f"Directory not found: {directory}")
        return []

    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                # Split hands using a more robust regex that handles different game types
                hands_raw = re.split(r"Winamax Poker - (?:CashGame|Short Track) - HandId:", content)
                for hand_text in hands_raw:
                    if hand_text.strip():
                        hand = Hand(hand_text)
                        parsed_hands.append(hand.to_dict())
    return parsed_hands


def main():
    parser = argparse.ArgumentParser(description="Parse poker hand history files.")
    parser.add_argument("directories", nargs="+", help="Directories containing hand history .txt files")
    parser.add_argument("--output", default="poker_hands.json", help="Output JSON file path")

    args = parser.parse_args()
    all_data = []

    for directory in args.directories:
        print(f"Processing directory: {directory}")
        all_data.extend(parse_directory(directory))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=4)

    print(f"Successfully saved {len(all_data)} hands to {args.output}")


if __name__ == "__main__":
    main()