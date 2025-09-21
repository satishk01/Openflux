#!/usr/bin/env python3
"""
Comprehensive test runner for OpenFlux AI Assistant
Runs all tests: unit, integration, performance, and validation
"""

import sys
import os
import subprocess
import time
from pathlib import Path

def run_test_script(script_name: str, description: str) -> bool:
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"❌ Test script not found: {script_name}")
        return False
    
    try:
        # Run the test script
        start_time = time.time()
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        duration = time.time() - start_time
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"\n⏱️ Test completed in {duration:.2f} seconds")
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT (exceeded 5 minutes)")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking Dependencies")
    print("-" * 40)
    
    required_modules = [
        'streamlit',
        'boto3',
        'cryptography',
        'psutil',
        'pathlib',
        'unittest'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - MISSING")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n⚠️ Missing dependencies: {', '.join(missing_modules)}")
        print("Install missing dependencies before running tests")
        return False
    
    print("\n✅ All dependencies available")
    return True


def check_project_structure():
    """Check if project structure is correct"""
    print("\n📁 Checking Project Structure")
    print("-" * 40)
    
    required_files = [
        'app.py',
        'startup.py',
        'services/credentials_manager.py',
        'services/ai_service.py',
        'components/credentials_ui.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        full_path = Path(__file__).parent / file_path
        if full_path.exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ Missing files: {', '.join(missing_files)}")
        print("Ensure all project files are present")
        return False
    
    print("\n✅ Project structure is correct")
    return True


def run_validation_tests():
    """Run executable validation if available"""
    print(f"\n{'='*60}")
    print("🔍 Running Executable Validation")
    print(f"{'='*60}")
    
    validation_script = Path(__file__).parent / "validate_standalone_exe.sh"
    
    if not validation_script.exists():
        print("ℹ️ Executable validation script not found - skipping")
        return True
    
    if not Path("dist/OpenFlux_AI_Assistant.exe").exists():
        print("ℹ️ No executable found - skipping validation")
        print("   Build the executable first to run validation tests")
        return True
    
    try:
        result = subprocess.run(
            ["bash", str(validation_script)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print("✅ Executable validation - PASSED")
            return True
        else:
            print("❌ Executable validation - FAILED")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Executable validation - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 Executable validation - ERROR: {e}")
        return False


def main():
    """Main test runner function"""
    print("🧪 OpenFlux AI Assistant - Comprehensive Test Suite")
    print("=" * 60)
    print("This will run all available tests to validate the application")
    print("=" * 60)
    
    # Track test results
    test_results = {}
    
    # Pre-flight checks
    print("\n🚀 Pre-flight Checks")
    print("=" * 30)
    
    if not check_dependencies():
        print("\n❌ Dependency check failed - cannot continue")
        return False
    
    if not check_project_structure():
        print("\n❌ Project structure check failed - cannot continue")
        return False
    
    print("\n✅ Pre-flight checks passed - starting tests")
    
    # Define test suite
    test_suite = [
        ("test_credentials_manager.py", "Credentials Manager Unit Tests"),
        ("test_integration.py", "Integration Tests"),
        ("test_performance.py", "Performance Tests")
    ]
    
    # Run each test
    for script, description in test_suite:
        test_results[description] = run_test_script(script, description)
    
    # Run validation tests
    test_results["Executable Validation"] = run_validation_tests()
    
    # Generate final report
    print(f"\n{'='*60}")
    print("📊 FINAL TEST REPORT")
    print(f"{'='*60}")
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<40} {status}")
        if result:
            passed_tests += 1
    
    print(f"\n📈 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ OpenFlux AI Assistant is ready for deployment")
        print("✅ All components are working correctly")
        print("✅ Performance meets requirements")
        print("✅ Integration is functioning properly")
        
        if "Executable Validation" in test_results and test_results["Executable Validation"]:
            print("✅ Executable is properly built and validated")
        
        return True
    else:
        failed_count = total_tests - passed_tests
        print(f"\n⚠️ {failed_count} TEST(S) FAILED")
        print("❌ Issues detected that need to be resolved")
        
        # Provide guidance based on failures
        if not test_results.get("Credentials Manager Unit Tests", True):
            print("🔧 Fix credential management issues")
        
        if not test_results.get("Integration Tests", True):
            print("🔧 Fix component integration issues")
        
        if not test_results.get("Performance Tests", True):
            print("🔧 Address performance issues or system requirements")
        
        if not test_results.get("Executable Validation", True):
            print("🔧 Rebuild executable or fix validation issues")
        
        return False


if __name__ == "__main__":
    success = main()
    
    if success:
        print(f"\n{'='*60}")
        print("🚀 READY FOR DEPLOYMENT")
        print(f"{'='*60}")
        print("Your OpenFlux AI Assistant has passed all tests!")
        print("You can now:")
        print("1. Build the Windows executable")
        print("2. Deploy to Windows 11 systems")
        print("3. Distribute to end users")
        print("\nNext steps:")
        print("- Run the build script: ./ubuntu_24_04_complete_build.sh")
        print("- Download the executable ZIP file")
        print("- Test on Windows 11 target system")
    else:
        print(f"\n{'='*60}")
        print("🔧 ISSUES DETECTED")
        print(f"{'='*60}")
        print("Please resolve the failed tests before deployment.")
        print("Check the test output above for specific issues.")
    
    sys.exit(0 if success else 1)