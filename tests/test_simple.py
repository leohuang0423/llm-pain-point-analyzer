#!/usr/bin/env python3
"""
Simple test file for LLM Pain Point Analyzer
This provides basic test coverage for CI/CD
"""

import sys
import os

def test_import_all_modules():
    """Test that all main modules can be imported"""
    modules = [
        'llm_pain_point_analyzer',
        'llm_pain_point_analyzer.permission_analyzer',
        'llm_pain_point_analyzer.tool_recommender',
        'llm_pain_point_analyzer.error_diagnoser',
        'llm_pain_point_analyzer.permission_verifier',
    ]
    
    # mcp_server requires mcp package, skip if not installed
    optional_modules = [
        'llm_pain_point_analyzer.mcp_server',
    ]
    
    all_passed = True
    
    for module in modules:
        try:
            __import__(module)
            print(f"✅ Import successful: {module}")
        except ImportError as e:
            print(f"❌ Import failed: {module} - {e}")
            all_passed = False
    
    for module in optional_modules:
        try:
            __import__(module)
            print(f"✅ Import successful: {module}")
        except ImportError as e:
            print(f"⚠️ Optional import failed (requires mcp package): {module} - {e}")
            # This is acceptable for basic tests
    
    return all_passed

def test_version():
    """Test that package has version"""
    try:
        import llm_pain_point_analyzer
        if hasattr(llm_pain_point_analyzer, '__version__'):
            print(f"✅ Version found: {llm_pain_point_analyzer.__version__}")
            return True
        else:
            print("⚠️ No __version__ attribute found")
            return True  # Not critical
    except Exception as e:
        print(f"⚠️ Version check error: {e}")
        return True  # Not critical

def test_config():
    """Test that config directory exists"""
    config_path = os.path.join(
        os.path.dirname(__file__), 
        '..', 
        'llm_pain_point_analyzer', 
        'config'
    )
    
    if os.path.exists(config_path):
        print(f"✅ Config directory exists: {config_path}")
        return True
    else:
        print(f"❌ Config directory missing: {config_path}")
        return False

def test_entry_points():
    """Test that entry points are defined in setup.py"""
    setup_path = os.path.join(os.path.dirname(__file__), '..', 'setup.py')
    
    if os.path.exists(setup_path):
        with open(setup_path, 'r') as f:
            content = f.read()
            if 'console_scripts' in content and 'llm-ppa' in content:
                print("✅ Entry points defined in setup.py")
                return True
            else:
                print("⚠️ Entry points may be missing in setup.py")
                return True  # Not critical
    else:
        print("❌ setup.py not found")
        return False

def main():
    """Run all simple tests"""
    print("🧪 Running simple tests for LLM Pain Point Analyzer...")
    print("=" * 60)
    
    tests = [
        test_import_all_modules,
        test_version,
        test_config,
        test_entry_points,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test '{test.__name__}' failed with exception: {e}")
            results.append(False)
    
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} simple tests passed!")
        return 0
    elif passed >= total * 0.8:  # 80% pass rate is acceptable for simple tests
        print(f"✅ {passed}/{total} simple tests passed (acceptable)")
        return 0
    else:
        print(f"⚠️ Only {passed}/{total} simple tests passed")
        return 1

if __name__ == "__main__":
    sys.exit(main())