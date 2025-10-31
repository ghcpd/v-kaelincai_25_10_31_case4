"""
Test Suite for Optimized Data Processing System - IMPROVED/HARDENED IMPLEMENTATION

This test suite verifies that all flaky behaviors have been mitigated:
- Runs each test multiple times (default: 20 iterations)
- Expects consistent outputs across all runs
- Measures stability rates (should be 100%)
- Validates deterministic behavior
"""

import json
import time
import sys
import os
from collections import defaultdict
from typing import Dict, List, Any
import hashlib

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from optimized_code import OptimizedDataProcessor, process_batch


class StabilityValidator:
    """Validates stability and consistency of test runs"""
    
    def __init__(self, num_iterations: int = 20, seed: int = 42):
        self.num_iterations = num_iterations
        self.seed = seed
        self.results = defaultdict(list)
        
    def run_test_multiple_times(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a single test case multiple times and verify consistency
        """
        test_id = test_case['test_id']
        input_data = test_case['input']
        
        outputs = []
        timings = []
        errors = []
        
        for iteration in range(self.num_iterations):
            # Create new processor with same seed for deterministic behavior
            processor = OptimizedDataProcessor(seed=self.seed)
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
        
        # Determine if test passed (should be 100% stable)
        test_passed = unique_outputs == 1 and len(errors) == 0
        
        return {
            'test_id': test_id,
            'test_name': test_case['name'],
            'iterations': self.num_iterations,
            'unique_outputs': unique_outputs,
            'stability_rate': stability_rate,
            'is_stable': unique_outputs == 1,
            'test_passed': test_passed,
            'avg_timing': avg_timing,
            'timing_variance': timing_variance,
            'error_count': len(errors),
            'errors': list(set(errors))
        }
    
    def _hash_result(self, result: Dict[str, Any]) -> str:
        """Create deterministic hash of result (excluding timing fields)"""
        # Remove timing and timestamp fields for comparison
        filtered_result = {k: v for k, v in result.items() 
                          if k not in ['processing_time', 'timestamp']}
        
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


def run_all_tests(test_data_path: str = None, num_iterations: int = 20, seed: int = 42) -> Dict[str, Any]:
    """
    Run all test cases and verify stability
    """
    if test_data_path is None:
        # Try to find test_data.json in parent directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        test_data_path = os.path.join(os.path.dirname(current_dir), 'test_data.json')
    
    print(f"Loading test data from: {test_data_path}")
    test_cases = load_test_data(test_data_path)
    
    validator = StabilityValidator(num_iterations=num_iterations, seed=seed)
    
    all_results = []
    
    print(f"\n{'='*80}")
    print(f"RUNNING STABILITY TEST SUITE - OPTIMIZED (HARDENED) IMPLEMENTATION")
    print(f"{'='*80}\n")
    print(f"Number of test cases: {len(test_cases)}")
    print(f"Iterations per test: {num_iterations}")
    print(f"Random seed: {seed}\n")
    
    for idx, test_case in enumerate(test_cases, 1):
        print(f"Running Test {idx}/{len(test_cases)}: {test_case['name']}...")
        print(f"  Previous flaky behavior: {test_case['flaky_behavior_type']}")
        
        result = validator.run_test_multiple_times(test_case)
        all_results.append(result)
        
        if result['test_passed']:
            print(f"  ✓ PASSED - Stability: {result['stability_rate']:.2%} "
                  f"(1 unique output across {num_iterations} runs)")
        else:
            print(f"  ✗ FAILED - Stability: {result['stability_rate']:.2%} "
                  f"({result['unique_outputs']} unique outputs)")
            if result['errors']:
                print(f"    Errors: {', '.join(result['errors'][:3])}")
        
        print()
    
    # Summary statistics
    passed_tests = sum(1 for r in all_results if r['test_passed'])
    failed_tests = len(all_results) - passed_tests
    avg_stability = sum(r['stability_rate'] for r in all_results) / len(all_results)
    
    summary = {
        'total_tests': len(test_cases),
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'average_stability_rate': avg_stability,
        'iterations_per_test': num_iterations,
        'seed': seed,
        'test_results': all_results
    }
    
    print(f"{'='*80}")
    print(f"TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total tests: {summary['total_tests']}")
    print(f"Passed tests: {passed_tests} ({passed_tests/len(all_results):.2%})")
    print(f"Failed tests: {failed_tests} ({failed_tests/len(all_results):.2%})")
    print(f"Average stability rate: {avg_stability:.2%}")
    
    if avg_stability == 1.0:
        print(f"\n🎉 ALL TESTS ACHIEVED 100% STABILITY!")
        print(f"All flaky behaviors have been successfully mitigated.")
    else:
        print(f"\n⚠ Some tests still exhibit flaky behavior")
    
    print(f"{'='*80}\n")
    
    return summary


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run stability tests on optimized implementation')
    parser.add_argument('--iterations', type=int, default=20,
                       help='Number of iterations per test (default: 20)')
    parser.add_argument('--test-data', type=str, default=None,
                       help='Path to test_data.json file')
    parser.add_argument('--seed', type=int, default=42,
                       help='Random seed for deterministic behavior (default: 42)')
    
    args = parser.parse_args()
    
    results = run_all_tests(test_data_path=args.test_data, 
                           num_iterations=args.iterations,
                           seed=args.seed)
    
    # Save results to JSON
    output_file = 'results_optimized.json'
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results['failed_tests'] == 0 else 1)
