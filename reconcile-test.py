#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from datetime import datetime
from tokenize import String

total = 0.0
count = 0
transactions = {}
skipped_lines = 0
no_txn_id = 0

with open("payments.jsonl") as f:
    for line in f:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            skipped_lines += 1
            print(repr(line))
            continue
        if event.get("txn_id") is None:
            no_txn_id += 1
            continue
        if event.get("txn_id") not in transactions:
            transactions[event.get("txn_id")] = event
        else:
            new_time_str = event.get("ts")
            old_time_str = transactions[event.get("txn_id")].get("ts")

            new_time = datetime.fromisoformat(new_time_str)
            old_time = datetime.fromisoformat(old_time_str)

            if new_time > old_time:
                transactions[event.get("txn_id")] = event

for row in transactions.values():
    clean = 0
    if type(row.get("amount")) is str:
        text = row.get("amount")
        clean = text.replace(",", "")
    else: clean = row.get("amount")
    if row.get("status") == "success":
        total += float(clean)
        count += 1
        


print(f"Skipped Lines: {skipped_lines}")
print(f"Lines with no txn Id: {no_txn_id}")
print(len(transactions))

with open("expected.txt") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    print(f"Your code: KOYA-{round(total)}")
