"""
Flaky Data Processing System - ORIGINAL (FAULTY) IMPLEMENTATION

This implementation intentionally exhibits multiple types of flaky behavior:
1. Race conditions in concurrent processing
2. Timing-dependent logic with sleep-based synchronization
3. Shared mutable state without proper locking
4. Unseeded random number generation
5. Simulated external service with variable latency

These flaky behaviors will cause inconsistent results across repeated runs.
"""

import time
import random
import json
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

# Shared mutable state WITHOUT proper synchronization (FLAKY!)
global_request_counter = 0
shared_cache = {}


class FlakyDataProcessor:
    """Data processor with intentional flaky behaviors"""
    
    def __init__(self):
        # NO random seed - causes nondeterministic behavior
        self.processing_times = []
        
    def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function with multiple flaky behaviors
        """
        global global_request_counter
        
        start_time = time.time()
        
        try:
            # Validate input (basic validation)
            if not isinstance(request_data, dict):
                return self._error_response("Invalid request format")
            
            user_id = request_data.get('user_id')
            items = request_data.get('items')
            priority = request_data.get('priority', 1)
            
            # FLAKY: Race condition on global counter (no locking)
            old_counter = global_request_counter
            time.sleep(random.uniform(0.001, 0.01))  # Simulate processing delay
            global_request_counter = old_counter + 1
            request_number = global_request_counter
            
            # Handle malformed inputs
            if user_id is None or not isinstance(items, list):
                return self._error_response("ValidationError")
            
            # Handle empty items
            if len(items) == 0:
                return {
                    'status': 'success',
                    'result': {
                        'processed_items': 0,
                        'total_value': 0
                    },
                    'processing_time': time.time() - start_time,
                    'request_id': request_number
                }
            
            # FLAKY: Random sampling without seed
            if request_data.get('random_sampling'):
                sample_size = request_data.get('sample_size', 3)
                items = random.sample(items, min(sample_size, len(items)))
            
            # FLAKY: Timing-dependent logic
            if request_data.get('requires_timing'):
                # This will fail intermittently based on system load
                time.sleep(0.05)
                current_time = time.time()
                if int(current_time * 1000) % 2 == 0:  # Unpredictable timing check
                    pass
                else:
                    # Sometimes fails based on timing
                    if random.random() > 0.5:
                        return self._error_response("TimingError")
            
            # FLAKY: Shared cache without synchronization
            if request_data.get('use_shared_cache'):
                cache_ops = request_data.get('concurrent_cache_ops', 1)
                cache_hits = 0
                
                for item in items:
                    # Race condition: read-modify-write without lock
                    if item in shared_cache:
                        cache_hits += 1
                        value = shared_cache[item]
                        time.sleep(0.001)  # Increase race window
                        shared_cache[item] = value + 1
                    else:
                        shared_cache[item] = 1
                
                return {
                    'status': 'success',
                    'result': {
                        'processed_items': len(items),
                        'cache_hits': cache_hits
                    },
                    'processing_time': time.time() - start_time,
                    'request_id': request_number
                }
            
            # FLAKY: External service simulation with variable latency
            if request_data.get('external_service_call'):
                validation_result = self._call_external_service_flaky(items)
                if not validation_result:
                    return self._error_response("ExternalServiceError")
                
                return {
                    'status': 'success',
                    'result': {
                        'processed_items': len(items),
                        'external_validated': True
                    },
                    'processing_time': time.time() - start_time,
                    'request_id': request_number
                }
            
            # Process concurrent requests (exposes race conditions)
            if request_data.get('concurrent_requests'):
                num_concurrent = request_data['concurrent_requests']
                threads = []
                
                for i in range(num_concurrent):
                    t = threading.Thread(target=self._concurrent_worker, args=(i,))
                    threads.append(t)
                    t.start()
                
                for t in threads:
                    t.join()
                
                return {
                    'status': 'success',
                    'result': {
                        'processed_items': len(items),
                        'request_number': global_request_counter
                    },
                    'processing_time': time.time() - start_time,
                    'request_id': request_number
                }
            
            # Normal processing
            total_value = self._calculate_value(items)
            
            return {
                'status': 'success',
                'result': {
                    'processed_items': len(items),
                    'total_value': total_value
                },
                'processing_time': time.time() - start_time,
                'request_id': request_number
            }
            
        except Exception as e:
            return self._error_response(str(e))
    
    def _concurrent_worker(self, worker_id: int):
        """Worker thread that increments global counter (race condition!)"""
        global global_request_counter
        
        # FLAKY: Race condition
        temp = global_request_counter
        time.sleep(random.uniform(0.001, 0.005))  # Increase race window
        global_request_counter = temp + 1
    
    def _call_external_service_flaky(self, items: List[str]) -> bool:
        """
        Simulate external service with variable latency and occasional failures
        FLAKY: Returns inconsistent results
        """
        # Random delay simulating network latency
        delay = random.uniform(0.01, 0.1)
        time.sleep(delay)
        
        # FLAKY: Randomly fail based on timing
        if time.time() % 1 < 0.4:  # Timing-dependent failure
            return False
        
        return True
    
    def _calculate_value(self, items: List[str]) -> int:
        """Calculate total value of items"""
        # Simple deterministic calculation
        return len(items) * 50
    
    def _error_response(self, error_msg: str) -> Dict[str, Any]:
        """Generate error response"""
        return {
            'status': 'error',
            'error_type': error_msg,
            'timestamp': datetime.now().isoformat()
        }
    
    def reset_state(self):
        """Reset global state (for testing)"""
        global global_request_counter, shared_cache
        global_request_counter = 0
        shared_cache = {}


def process_batch(requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process a batch of requests
    FLAKY: Results vary due to shared state and race conditions
    """
    processor = FlakyDataProcessor()
    results = []
    
    for request in requests:
        result = processor.process_request(request)
        results.append(result)
    
    return results


if __name__ == "__main__":
    # Example usage
    processor = FlakyDataProcessor()
    
    test_request = {
        "user_id": "user_001",
        "items": ["apple", "banana", "cherry"],
        "priority": 1,
        "timestamp": "2025-10-31T10:00:00Z"
    }
    
    # Run the same request multiple times - will show inconsistent results
    print("Running same request 5 times (demonstrating flakiness):")
    for i in range(5):
        result = processor.process_request(test_request)
        print(f"Run {i+1}: request_id={result.get('request_id')}")
    
    processor.reset_state()
