# Poker Hand Analysis Project

This project provides tools to analyze poker hand history data, specifically calculating the performance (Big Blind profit/loss) of different hand types.
It uses winamax hands logs

## Project Structure

*   `parser.py`: The script responsible for parsing raw poker hand logs into structured data.
*   `worst_hands.py`: An analysis script that aggregates data from `poker_hands.json` and outputs performance statistics.

## Getting Started

### Prerequisites

*   **Python 3.14.3** or higher.
*   Ensure your environment is set up with the necessary virtual environment:
```shell script
source .venv/bin/activate
```


### How to Run

1.  **Parse Hand Histories**:
    Run the parser to generate the processed data file from your raw hand logs.
```shell script
python parser.py
```

    *Note: This will generate or update `poker_hands.json`.*

2.  **Analyze Results**:
    Once the JSON file is ready, use the `worst_hands.py` script to view performance metrics. This script calculates the total and average Big Blind (BB) results for different hand types and displays the top 20 best and worst performers.
```shell script
python worst_hands.py
```


## Functionality

The `worst_hands.py` script performs the following operations:
*   Reads `poker_hands.json`.
*   Groups performance metrics by hand type (e.g., 'AA', '72o').
*   Calculates total BB, hand counts, and average BB per hand.
*   Sorts and prints the "Top 20 Worst Hands" (by total BB loss).
*   Sorts and prints the "Top 20 Best Hands" (by total BB win).

## Troubleshooting

*   **FileNotFoundError**: If you encounter a `FileNotFoundError` when running `worst_hands.py`, ensure that you have run `parser.py` first to generate the required `poker_hands.json` file.