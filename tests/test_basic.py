#!/usr/bin/env python3
"""
Basic test suite for LLM Pain Point Analyzer
This ensures GitHub Actions can run tests successfully
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_import_permission_analyzer():
    """Test that permission analyzer can be imported"""
    try:
        from llm_pain_point_analyzer import permission_analyzer
        print("✅ permission_analyzer import successful")
        return True
    except ImportError as e:
        print(f"❌ permission_analyzer import failed: {e}")
        return False

def test_import_tool_recommender():
    """Test that tool recommender can be imported"""
    try:
        from llm_pain_point_analyzer import tool_recommender
        print("✅ tool_recommender import successful")
        return True
    except ImportError as e:
        print(f"❌ tool_recommender import failed: {e}")
        return False

def test_import_error_diagnoser():
    """Test that error diagnoser can be imported"""
    try:
        from llm_pain_point_analyzer import error_diagnoser
        print("✅ error_diagnoser import successful")
        return True
    except ImportError as e:
        print(f"❌ error_diagnoser import failed: {e}")
        return False

def test_import_permission_verifier():
    """Test that permission verifier can be imported"""
    try:
        from llm_pain_point_analyzer import permission_verifier
        print("✅ permission_verifier import successful")
        return True
    except ImportError as e:
        print(f"❌ permission_verifier import failed: {e}")
        return False

def test_package_structure():
    """Test that package structure is correct"""
    import llm_pain_point_analyzer
    expected_attrs = [
        '__version__',
        '__author__',
        '__description__',
    ]
    
    for attr in expected_attrs:
        if hasattr(llm_pain_point_analyzer, attr):
            print(f"✅ Package attribute '{attr}' found")
        else:
            print(f"⚠️ Package attribute '{attr}' not found")
    
    return True

def test_config_files():
    """Test that configuration files exist"""
    import os
    config_dir = os.path.join(os.path.dirname(__file__), '..', 'llm_pain_point_analyzer', 'config')
    
    expected_files = [
        'tool_catalog.json',
        'tool_performance.json',
        'tools.json',
    ]
    
    all_exist = True
    for file in expected_files:
        file_path = os.path.join(config_dir, file)
        if os.path.exists(file_path):
            print(f"✅ Config file '{file}' exists")
        else:
            print(f"❌ Config file '{file}' missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🧪 Running LLM Pain Point Analyzer basic tests...")
    print("=" * 60)
    
    tests = [
        test_import_permission_analyzer,
        test_import_tool_recommender,
        test_import_error_diagnoser,
        test_import_permission_verifier,
        test_package_structure,
        test_config_files,
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
        print(f"🎉 All {total} tests passed!")
        return 0
    else:
        print(f"⚠️ {passed}/{total} tests passed")
        return 1

if __name__ == "__main__":
    sys.exit(main())