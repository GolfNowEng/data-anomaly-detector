#!/usr/bin/env python3
"""
Generate a list of LOW anomalies from the PAST only.
"""

import csv
from datetime import datetime
from collections import defaultdict
import statistics

def parse_date(date_str):
    return datetime.strptime(date_str, '%Y%m%d')

def get_day_name(date_obj):
    return date_obj.strftime('%A')

def calculate_z_score(value, mean, std_dev):
    if std_dev == 0:
        return 0
    return (value - mean) / std_dev

# Today's date
TODAY = datetime(2026, 2, 2)

# Read data
data = []
with open('ezlrounds.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        date_obj = parse_date(row['playdatekey'])
        count = int(row['count'])
        day_name = get_day_name(date_obj)
        data.append({
            'date': date_obj,
            'date_str': row['playdatekey'],
            'count': count,
            'day_name': day_name
        })

# Group by day of week
day_of_week_counts = defaultdict(list)
for entry in data:
    day_of_week_counts[entry['day_name']].append(entry['count'])

# Calculate stats
day_stats = {}
for day, counts in day_of_week_counts.items():
    day_stats[day] = {
        'mean': statistics.mean(counts),
        'stdev': statistics.stdev(counts) if len(counts) > 1 else 0,
    }

# Find LOW anomalies from the PAST only
past_low_anomalies = []

for entry in data:
    # Skip future dates
    if entry['date'] >= TODAY:
        continue

    day = entry['day_name']
    count = entry['count']
    stats = day_stats[day]
    z_score = calculate_z_score(count, stats['mean'], stats['stdev'])

    # Only include LOW anomalies (z-score < -2.5 OR count < 5000)
    if z_score < -2.5 or count < 5000:
        past_low_anomalies.append({
            **entry,
            'z_score': z_score,
            'expected': stats['mean'],
            'pct_diff': ((count - stats['mean']) / stats['mean']) * 100
        })

# Sort by date
past_low_anomalies.sort(key=lambda x: x['date'])

# Print results
print("LOW ANOMALIES FROM THE PAST (before 2026-02-02)")
print("=" * 80)
print(f"{'Date':<12} {'Day':<10} {'Count':>10} {'Expected':>10} {'Z-Score':>8} {'% Diff':>8}")
print("-" * 80)

for entry in past_low_anomalies:
    print(f"{entry['date_str']:<12} {entry['day_name']:<10} {entry['count']:>10,} "
          f"{entry['expected']:>10.0f} {entry['z_score']:>8.2f} {entry['pct_diff']:>7.1f}%")

print("\n" + "=" * 80)
print(f"Total past low anomalies: {len(past_low_anomalies)}")
print("=" * 80)

# Group by time periods for easier analysis
print("\n\nGROUPED BY YEAR/MONTH:")
print("=" * 80)
from itertools import groupby

for year_month, group in groupby(past_low_anomalies, key=lambda x: x['date_str'][:6]):
    items = list(group)
    year = year_month[:4]
    month = year_month[4:6]
    print(f"\n{year}-{month} ({len(items)} anomalies):")
    for item in items:
        print(f"  {item['date_str']} ({item['day_name']:<9}): {item['count']:>8,}")
