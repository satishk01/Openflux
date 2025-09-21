#!/usr/bin/env python3
"""
Performance testing script for OpenFlux AI Assistant
Tests memory usage, startup time, and resource consumption
"""

import psutil
import time
import sys
import os
import subprocess
import threading
from pathlib import Path
from typing import Dict, List, Tuple

class PerformanceMonitor:
    """Monitor system performance during application execution"""
    
    def __init__(self):
        self.monitoring = False
        self.measurements = []
        self.start_time = None
        self.process = None
    
    def start_monitoring(self, process_name: str = "python"):
        """Start monitoring system resources"""
        self.monitoring = True
        self.start_time = time.time()
        self.measurements = []
        
        # Find the process
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    if any('streamlit' in str(cmd).lower() for cmd in proc.info['cmdline']):
                        self.process = psutil.Process(proc.info['pid'])
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Start monitoring thread
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                measurement = {
                    'timestamp': time.time() - self.start_time,
                    'system_memory_percent': psutil.virtual_memory().percent,
                    'system_cpu_percent': psutil.cpu_percent(),
                    'available_memory_mb': psutil.virtual_memory().available / 1024 / 1024
                }
                
                if self.process and self.process.is_running():
                    try:
                        measurement.update({
                            'process_memory_mb': self.process.memory_info().rss / 1024 / 1024,
                            'process_cpu_percent': self.process.cpu_percent(),
                            'process_threads': self.process.num_threads(),
                            'process_handles': self.process.num_handles() if hasattr(self.process, 'num_handles') else 0
                        })
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                self.measurements.append(measurement)
                time.sleep(1)  # Measure every second
                
            except Exception as e:
                print(f"Monitoring error: {e}")
                break
    
    def stop_monitoring(self):
        """Stop monitoring and return results"""
        self.monitoring = False
        return self.measurements
    
    def get_summary(self) -> Dict:
        """Get performance summary"""
        if not self.measurements:
            return {}
        
        process_memory = [m.get('process_memory_mb', 0) for m in self.measurements if 'process_memory_mb' in m]
        process_cpu = [m.get('process_cpu_percent', 0) for m in self.measurements if 'process_cpu_percent' in m]
        system_memory = [m['system_memory_percent'] for m in self.measurements]
        system_cpu = [m['system_cpu_percent'] for m in self.measurements]
        
        return {
            'duration_seconds': self.measurements[-1]['timestamp'] if self.measurements else 0,
            'process_memory_mb': {
                'min': min(process_memory) if process_memory else 0,
                'max': max(process_memory) if process_memory else 0,
                'avg': sum(process_memory) / len(process_memory) if process_memory else 0
            },
            'process_cpu_percent': {
                'min': min(process_cpu) if process_cpu else 0,
                'max': max(process_cpu) if process_cpu else 0,
                'avg': sum(process_cpu) / len(process_cpu) if process_cpu else 0
            },
            'system_memory_percent': {
                'min': min(system_memory),
                'max': max(system_memory),
                'avg': sum(system_memory) / len(system_memory)
            },
            'system_cpu_percent': {
                'min': min(system_cpu),
                'max': max(system_cpu),
                'avg': sum(system_cpu) / len(system_cpu)
            },
            'total_measurements': len(self.measurements)
        }


def test_startup_time():
    """Test application startup time"""
    print("🚀 Testing Application Startup Time")
    print("-" * 40)
    
    # Test script startup
    start_time = time.time()
    
    try:
        # Import main modules to simulate startup
        sys.path.insert(0, str(Path(__file__).parent))
        
        import_start = time.time()
        from services.credentials_manager import CredentialsManager
        from services.ai_service import AIService
        from components.credentials_ui import CredentialsUI
        import_time = time.time() - import_start
        
        # Initialize services
        init_start = time.time()
        credentials_manager = CredentialsManager()
        ai_service = AIService(credentials_manager)
        init_time = time.time() - init_start
        
        total_time = time.time() - start_time
        
        print(f"✅ Module import time: {import_time:.2f} seconds")
        print(f"✅ Service initialization time: {init_time:.2f} seconds")
        print(f"✅ Total startup time: {total_time:.2f} seconds")
        
        # Evaluate startup performance
        if total_time < 2.0:
            print("🟢 Excellent startup performance")
        elif total_time < 5.0:
            print("🟡 Good startup performance")
        else:
            print("🔴 Slow startup - consider optimization")
        
        return {
            'import_time': import_time,
            'init_time': init_time,
            'total_time': total_time,
            'status': 'success'
        }
        
    except Exception as e:
        print(f"❌ Startup test failed: {e}")
        return {
            'error': str(e),
            'status': 'failed'
        }


def test_memory_usage():
    """Test memory usage patterns"""
    print("\n💾 Testing Memory Usage")
    print("-" * 40)
    
    try:
        # Get baseline memory
        baseline_memory = psutil.virtual_memory()
        print(f"📊 System baseline memory: {baseline_memory.percent}% used")
        print(f"📊 Available memory: {baseline_memory.available / 1024 / 1024:.0f} MB")
        
        # Test credential manager memory usage
        sys.path.insert(0, str(Path(__file__).parent))
        from services.credentials_manager import CredentialsManager
        
        credentials_manager = CredentialsManager()
        
        # Simulate credential operations
        test_access_key = "AKIAIOSFODNN7EXAMPLE"
        test_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        
        # Test encryption/decryption cycles
        memory_before = psutil.virtual_memory().available
        
        for i in range(100):  # Simulate multiple credential operations
            credentials_manager.store_credentials(test_access_key, test_secret_key)
            status = credentials_manager.get_credentials_status()
            credentials_manager.clear_credentials()
        
        memory_after = psutil.virtual_memory().available
        memory_diff = (memory_before - memory_after) / 1024 / 1024
        
        print(f"✅ Memory usage after 100 credential cycles: {memory_diff:.2f} MB")
        
        if memory_diff < 10:
            print("🟢 Excellent memory management")
        elif memory_diff < 50:
            print("🟡 Good memory management")
        else:
            print("🔴 Potential memory leak detected")
        
        # Test current memory requirements
        current_memory = psutil.virtual_memory()
        if current_memory.available < 1024 * 1024 * 1024:  # Less than 1GB available
            print("⚠️ Warning: Low available memory may affect performance")
        
        return {
            'baseline_memory_percent': baseline_memory.percent,
            'available_memory_mb': baseline_memory.available / 1024 / 1024,
            'memory_diff_mb': memory_diff,
            'status': 'success'
        }
        
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return {
            'error': str(e),
            'status': 'failed'
        }


def test_encryption_performance():
    """Test encryption/decryption performance"""
    print("\n🔐 Testing Encryption Performance")
    print("-" * 40)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent))
        from services.credentials_manager import CredentialsManager
        
        credentials_manager = CredentialsManager()
        test_access_key = "AKIAIOSFODNN7EXAMPLE"
        test_secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
        
        # Test encryption performance
        encrypt_times = []
        decrypt_times = []
        
        for i in range(50):
            # Test encryption
            start_time = time.time()
            credentials_manager.store_credentials(test_access_key, test_secret_key)
            encrypt_time = time.time() - start_time
            encrypt_times.append(encrypt_time)
            
            # Test decryption (via status check)
            start_time = time.time()
            status = credentials_manager.get_credentials_status()
            decrypt_time = time.time() - start_time
            decrypt_times.append(decrypt_time)
            
            credentials_manager.clear_credentials()
        
        avg_encrypt_time = sum(encrypt_times) / len(encrypt_times)
        avg_decrypt_time = sum(decrypt_times) / len(decrypt_times)
        
        print(f"✅ Average encryption time: {avg_encrypt_time * 1000:.2f} ms")
        print(f"✅ Average decryption time: {avg_decrypt_time * 1000:.2f} ms")
        
        if avg_encrypt_time < 0.01 and avg_decrypt_time < 0.01:
            print("🟢 Excellent encryption performance")
        elif avg_encrypt_time < 0.05 and avg_decrypt_time < 0.05:
            print("🟡 Good encryption performance")
        else:
            print("🔴 Slow encryption - may impact user experience")
        
        return {
            'avg_encrypt_time_ms': avg_encrypt_time * 1000,
            'avg_decrypt_time_ms': avg_decrypt_time * 1000,
            'status': 'success'
        }
        
    except Exception as e:
        print(f"❌ Encryption performance test failed: {e}")
        return {
            'error': str(e),
            'status': 'failed'
        }


def test_system_requirements():
    """Test if system meets requirements"""
    print("\n🖥️ Testing System Requirements")
    print("-" * 40)
    
    # Check RAM
    memory = psutil.virtual_memory()
    total_ram_gb = memory.total / 1024 / 1024 / 1024
    
    print(f"📊 Total RAM: {total_ram_gb:.1f} GB")
    
    if total_ram_gb >= 16:
        print("🟢 Excellent RAM (16GB+)")
        ram_status = "excellent"
    elif total_ram_gb >= 8:
        print("🟡 Adequate RAM (8GB+)")
        ram_status = "adequate"
    else:
        print("🔴 Insufficient RAM (less than 8GB)")
        ram_status = "insufficient"
    
    # Check CPU
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    
    print(f"🔧 CPU cores: {cpu_count}")
    if cpu_freq:
        print(f"🔧 CPU frequency: {cpu_freq.current:.0f} MHz")
    
    if cpu_count >= 4:
        print("🟢 Good CPU (4+ cores)")
        cpu_status = "good"
    elif cpu_count >= 2:
        print("🟡 Adequate CPU (2+ cores)")
        cpu_status = "adequate"
    else:
        print("🔴 Limited CPU (less than 2 cores)")
        cpu_status = "limited"
    
    # Check disk space
    disk = psutil.disk_usage('/')
    free_space_gb = disk.free / 1024 / 1024 / 1024
    
    print(f"💾 Free disk space: {free_space_gb:.1f} GB")
    
    if free_space_gb >= 10:
        print("🟢 Sufficient disk space")
        disk_status = "sufficient"
    elif free_space_gb >= 5:
        print("🟡 Limited disk space")
        disk_status = "limited"
    else:
        print("🔴 Insufficient disk space")
        disk_status = "insufficient"
    
    # Overall assessment
    print("\n📋 Overall System Assessment:")
    if ram_status == "excellent" and cpu_status == "good" and disk_status == "sufficient":
        print("🟢 System exceeds requirements - excellent performance expected")
        overall = "excellent"
    elif ram_status in ["excellent", "adequate"] and cpu_status in ["good", "adequate"] and disk_status in ["sufficient", "limited"]:
        print("🟡 System meets requirements - good performance expected")
        overall = "good"
    else:
        print("🔴 System may not meet requirements - performance issues possible")
        overall = "poor"
    
    return {
        'total_ram_gb': total_ram_gb,
        'ram_status': ram_status,
        'cpu_count': cpu_count,
        'cpu_status': cpu_status,
        'free_space_gb': free_space_gb,
        'disk_status': disk_status,
        'overall_status': overall
    }


def run_performance_tests():
    """Run all performance tests"""
    print("🧪 OpenFlux AI Assistant - Performance Testing")
    print("=" * 60)
    
    results = {}
    
    # Run individual tests
    results['startup'] = test_startup_time()
    results['memory'] = test_memory_usage()
    results['encryption'] = test_encryption_performance()
    results['system'] = test_system_requirements()
    
    # Generate summary report
    print("\n📊 Performance Test Summary")
    print("=" * 60)
    
    # Startup performance
    if results['startup']['status'] == 'success':
        startup_time = results['startup']['total_time']
        if startup_time < 2.0:
            print("🟢 Startup Performance: Excellent")
        elif startup_time < 5.0:
            print("🟡 Startup Performance: Good")
        else:
            print("🔴 Startup Performance: Needs Improvement")
    else:
        print("❌ Startup Performance: Test Failed")
    
    # Memory performance
    if results['memory']['status'] == 'success':
        memory_diff = results['memory']['memory_diff_mb']
        if memory_diff < 10:
            print("🟢 Memory Management: Excellent")
        elif memory_diff < 50:
            print("🟡 Memory Management: Good")
        else:
            print("🔴 Memory Management: Needs Improvement")
    else:
        print("❌ Memory Management: Test Failed")
    
    # Encryption performance
    if results['encryption']['status'] == 'success':
        encrypt_time = results['encryption']['avg_encrypt_time_ms']
        if encrypt_time < 10:
            print("🟢 Encryption Performance: Excellent")
        elif encrypt_time < 50:
            print("🟡 Encryption Performance: Good")
        else:
            print("🔴 Encryption Performance: Needs Improvement")
    else:
        print("❌ Encryption Performance: Test Failed")
    
    # System requirements
    overall_status = results['system']['overall_status']
    if overall_status == 'excellent':
        print("🟢 System Requirements: Exceeded")
    elif overall_status == 'good':
        print("🟡 System Requirements: Met")
    else:
        print("🔴 System Requirements: Not Met")
    
    print("\n" + "=" * 60)
    
    # Overall assessment
    success_count = sum(1 for test in results.values() if test.get('status') == 'success')
    total_tests = len([test for test in results.values() if 'status' in test])
    
    if success_count == total_tests:
        print("✅ All performance tests passed!")
        if overall_status == 'excellent':
            print("🎉 System is optimally configured for OpenFlux AI Assistant")
        else:
            print("👍 System is ready for OpenFlux AI Assistant")
        return True
    else:
        print(f"⚠️ {total_tests - success_count} performance test(s) failed")
        print("💡 Consider system upgrades or optimizations")
        return False


if __name__ == "__main__":
    success = run_performance_tests()
    sys.exit(0 if success else 1)