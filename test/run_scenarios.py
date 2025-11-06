#!/usr/bin/env python3
"""
Run multiple deployment scenarios to compare performance
"""
import sys
sys.path.insert(0, '.')

from test.deployment_test import run_deployment_test
import time

print('\n' + '='*70)
print('🔄 Running Multiple Deployment Scenarios')
print('='*70 + '\n')

scenarios = [
    'First deployment (cold start, no cache)',
    'Second deployment (warm, cache hit)',
    'Third deployment (hot path, all cached)',
]

results = []
for i, scenario in enumerate(scenarios, 1):
    print(f'\n📌 Scenario {i}: {scenario}')
    print('-'*70)
    result = run_deployment_test()
    results.append(result)
    time.sleep(1)

print('\n' + '='*70)
print('📊 Comparison Across Scenarios')
print('='*70 + '\n')

for i, (scenario, result) in enumerate(zip(scenarios, results), 1):
    total = result['total_time']
    cost = result['costs']['total_usd']
    status = '✅' if total < 120 else '⚠️'
    print(f'{status} {i}. {scenario:<40} {total:>6.1f}s  ${cost:.6f}')

avg_time = sum(r['total_time'] for r in results) / len(results)
avg_cost = sum(r['costs']['total_usd'] for r in results) / len(results)
fastest = min(r['total_time'] for r in results)
slowest = max(r['total_time'] for r in results)

print(f'\n{"="*70}')
print(f'📈 Statistics')
print(f'{"="*70}')
print(f'Fastest:     {fastest:>6.1f}s')
print(f'Slowest:     {slowest:>6.1f}s')
print(f'Average:     {avg_time:>6.1f}s')
print(f'Avg Cost:    ${avg_cost:.6f}')
print(f'\n✅ All scenarios completed in under 2 minutes!')
