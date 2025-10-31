"""
Test Suite for Flaky Data Processing System - ORIGINAL (FAULTY) IMPLEMENTATION

This test suite is designed to expose flaky behavior by:
- Running each test multiple times (default: 20 iterations)
- Detecting inconsistent outputs across runs
- Measuring stability rates and variance
- Testing concurrent scenarios that expose race conditions
"""

import json
import time
import sys
import os
from collections import defaultdict
from typing import Dict, List, Any, Tuple
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from original_code import FlakyDataProcessor, process_batch


class FlakinessDetector:
    """Detects and measures flaky behavior in test runs"""
    
    def __init__(self, num_iterations: int = 20):
        self.num_iterations = num_iterations
        self.results = defaultdict(list)
        
    def run_test_multiple_times(self, test_case: Dict[str, Any], processor: FlakyDataProcessor) -> Dict[str, Any]:
        """
        Run a single test case multiple times and measure consistency
        """
        test_id = test_case['test_id']
        input_data = test_case['input']
        
        outputs = []
        timings = []
        errors = []
        
        for iteration in range(self.num_iterations):
            processor.reset_state()
            start_time = time.time()
            
            try:
                result = processor.process_request(input_data.copy())
                elapsed = time.time() - start_time
                
                # Create deterministic hash of result for comparison
                result_hash = self._hash_result(result)
                outputs.append(result_hash)
                timings.append(elapsed)
                
                self.results[test_id].append({
                    'iteration': iteration,
                    'result': result,
                    'result_hash': result_hash,
                    'timing': elapsed,
                    'status': result.get('status', 'unknown')
                })
                
            except Exception as e:
                errors.append(str(e))
                self.results[test_id].append({
                    'iteration': iteration,
                    'error': str(e),
                    'timing': time.time() - start_time
                })
        
        # Calculate metrics
        unique_outputs = len(set(outputs))
        stability_rate = 1.0 if unique_outputs == 1 else (self.num_iterations - unique_outputs + 1) / self.num_iterations
        avg_timing = sum(timings) / len(timings) if timings else 0
        timing_variance = self._calculate_variance(timings)
        
        return {
            'test_id': test_id,
            'test_name': test_case['name'],
            'iterations': self.num_iterations,
            'unique_outputs': unique_outputs,
            'stability_rate': stability_rate,
            'is_stable': unique_outputs == 1,
            'avg_timing': avg_timing,
            'timing_variance': timing_variance,
            'error_count': len(errors),
            'errors': list(set(errors))
        }
    
    def _hash_result(self, result: Dict[str, Any]) -> str:
        """Create deterministic hash of result (excluding timing fields)"""
        # Remove timing and timestamp fields for comparison
        filtered_result = {k: v for k, v in result.items() 
                          if k not in ['processing_time', 'timestamp', 'request_id']}
        
        result_str = json.dumps(filtered_result, sort_keys=True)
        return hashlib.md5(result_str.encode()).hexdigest()
    
    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance of a list of values"""
        if not values:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5  # Return standard deviation


def load_test_data(file_path: str) -> List[Dict[str, Any]]:
    """Load test cases from JSON file"""
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data['test_cases']


def run_all_tests(test_data_path: str = None, num_iterations: int = 20) -> Dict[str, Any]:
    """
    Run all test cases and collect flakiness metrics
    """
    if test_data_path is None:
        # Try to find test_data.json in parent directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(os.path.dirname(current_dir), 'test_data.json')
    
    print(f"Loading test data from: {test_data_path}")
    test_cases = load_test_data(test_data_path)
    
    processor = FlakyDataProcessor()
    detector = FlakinessDetector(num_iterations=num_iterations)
    
    all_results = []
    
    print(f"\n{'='*80}")
    print(f"RUNNING FLAKY BEHAVIOR TEST SUITE - ORIGINAL (FAULTY) IMPLEMENTATION")
    print(f"{'='*80}\n")
    print(f"Number of test cases: {len(test_cases)}")
    print(f"Iterations per test: {num_iterations}\n")
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"Running Test {idx}/{len(test_cases)}: {test_case['name']}...")
        print(f"  Expected flaky behavior: {test_case['flaky_behavior_type']}")
        
        result = detector.run_test_multiple_times(test_case, processor)
        all_results.append(result)
        
        print(f"  ✓ Completed - Stability: {result['stability_rate']:.2%} "
              f"({result['unique_outputs']} unique outputs)")
        
        if not result['is_stable']:
            print(f"  ⚠ FLAKINESS DETECTED: {result['unique_outputs']} different outputs across {num_iterations} runs")
        
        print()
    
    # Summary statistics
    stable_tests = sum(1 for r in all_results if r['is_stable'])
    flaky_tests = len(all_results) - stable_tests
    avg_stability = sum(r['stability_rate'] for r in all_results) / len(all_results)
    
    summary = {
        'total_tests': len(test_cases),
        'stable_tests': stable_tests,
        'flaky_tests': flaky_tests,
        'average_stability_rate': avg_stability,
        'iterations_per_test': num_iterations,
        'test_results': all_results
    }
    
    print(f"{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Stable tests: {stable_tests} ({stable_tests/len(all_results):.2%})")
    print(f"Flaky tests: {flaky_tests} ({flaky_tests/len(all_results):.2%})")
    print(f"Average stability rate: {avg_stability:.2%}")
    print(f"{'='*80}\n")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run flaky behavior tests')
    parser.add_argument('--iterations', type=int, default=20,
                       help='Number of iterations per test (default: 20)')
    parser.add_argument('--test-data', type=str, default=None,
                       help='Path to test_data.json file')
    
    args = parser.parse_args()
    
    results = run_all_tests(test_data_path=args.test_data, num_iterations=args.iterations)
    
    # Save results to JSON
    output_file = 'results_original.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")
