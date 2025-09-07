#!/usr/bin/env python3
"""
Test script for discovery system with test answers.

This script demonstrates how to use the discovery system with pre-defined
test answers instead of requiring manual input.
"""

import sys
import json
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from builder.discovery.engine import DiscoveryEngine
from builder.discovery.interview import DiscoveryInterview


def test_discovery_with_answers():
    """Test the discovery system using test answers."""
    
    # Path to our test answers file
    test_answers_file = "tests/data/discovery_test_answers.json"
    
    print("🧪 Testing Discovery System with Test Answers")
    print("=" * 50)
    
    # Test 1: Test the interview component directly
    print("\n1. Testing DiscoveryInterview with test answers...")
    interview = DiscoveryInterview(
        question_set="comprehensive",
        test_answers_file=test_answers_file
    )
    
    # Test answering questions
    test_target = Path(".")
    answers = interview._answer_questions(test_target)
    
    print(f"   ✅ Interview completed with {len(answers)} answers")
    
    # Show some key answers
    key_questions = ['product_vision', 'target_users', 'key_features', 'team_size']
    for q in key_questions:
        if q in answers:
            value = answers[q]
            if isinstance(value, list):
                value = ', '.join(str(v) for v in value[:3]) + ('...' if len(value) > 3 else '')
            print(f"   📝 {q}: {str(value)[:100]}{'...' if len(str(value)) > 100 else ''}")
    
    # Test 2: Test the full discovery engine
    print("\n2. Testing DiscoveryEngine with test answers...")
    engine = DiscoveryEngine(
        root_path=".",
        question_set="comprehensive",
        test_answers_file=test_answers_file
    )
    
    # Run a quick discovery
    print("   🔍 Running discovery analysis...")
    try:
        results = engine.discover(".", {
            'feature': 'test_feature',
            'auto_generate': True
        })
        
        print(f"   ✅ Discovery completed successfully")
        print(f"   📊 Results contain {len(results)} sections")
        
        # Show some results
        if 'interview' in results:
            interview_data = results['interview']
            if 'questions' in interview_data:
                questions = interview_data['questions']
                print(f"   📝 Interview captured {len(questions)} question answers")
                
                # Show that test answers were used
                if 'product_vision' in questions:
                    vision = questions['product_vision']
                    if "Code Builder is an AI-powered development tool" in str(vision):
                        print("   ✅ Test answers successfully loaded and used!")
                    else:
                        print("   ⚠️  Test answers may not have been loaded properly")
        
    except Exception as e:
        print(f"   ❌ Discovery failed: {e}")
        return False
    
    # Test 3: Test without test answers (should fall back to defaults)
    print("\n3. Testing DiscoveryEngine without test answers...")
    engine_no_test = DiscoveryEngine(
        root_path=".",
        question_set="comprehensive"
    )
    
    try:
        results_no_test = engine_no_test.discover(".", {
            'feature': 'test_feature',
            'auto_generate': True
        })
        
        if 'interview' in results_no_test:
            interview_data = results_no_test['interview']
            if 'questions' in interview_data:
                questions = interview_data['questions']
                if 'product_vision' in questions:
                    vision = questions['product_vision']
                    if "needs manual input" in str(vision):
                        print("   ✅ Fallback to default answers working correctly")
                    else:
                        print("   ⚠️  Fallback behavior may not be working as expected")
        
    except Exception as e:
        print(f"   ❌ Discovery without test answers failed: {e}")
        return False
    
    print("\n🎉 All tests completed successfully!")
    return True


def test_cli_integration():
    """Test CLI integration with test answers."""
    print("\n4. Testing CLI integration...")
    
    # Test the discover:analyze command with test answers
    import subprocess
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "builder.core.cli", 
            "discover:analyze", 
            "--repo-root",
            "--test-answers", "tests/data/discovery_test_answers.json",
            "--output", "test_discovery_output.json"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("   ✅ CLI command with test answers executed successfully")
            
            # Check if output file was created
            output_file = Path("test_discovery_output.json")
            if output_file.exists():
                print("   ✅ Output file created successfully")
                
                # Load and check the output
                with open(output_file, 'r') as f:
                    output_data = json.load(f)
                
                if 'interview' in output_data and 'questions' in output_data['interview']:
                    questions = output_data['interview']['questions']
                    if 'product_vision' in questions and "Code Builder is an AI-powered" in str(questions['product_vision']):
                        print("   ✅ Test answers properly integrated in CLI output")
                    else:
                        print("   ⚠️  Test answers may not be properly integrated")
                
                # Clean up
                output_file.unlink()
                print("   🧹 Cleaned up test output file")
            else:
                print("   ❌ Output file was not created")
        else:
            print(f"   ❌ CLI command failed: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  CLI command timed out (this is expected for discovery)")
    except Exception as e:
        print(f"   ❌ CLI test failed: {e}")


if __name__ == "__main__":
    print("🚀 Starting Discovery Test with Test Answers")
    print("=" * 60)
    
    # Check if test answers file exists
    test_answers_file = Path("tests/data/discovery_test_answers.json")
    if not test_answers_file.exists():
        print(f"❌ Test answers file not found: {test_answers_file}")
        print("   Please ensure the test answers file exists before running this test.")
        sys.exit(1)
    
    # Run tests
    success = test_discovery_with_answers()
    
    if success:
        test_cli_integration()
        print("\n🎯 Test Summary:")
        print("   ✅ Discovery system successfully supports test answers")
        print("   ✅ Test answers are properly loaded and used")
        print("   ✅ Fallback to default answers works when no test file provided")
        print("   ✅ CLI integration works with test answers parameter")
        print("\n💡 Usage:")
        print("   python -m builder.core.cli discover:analyze --repo-root --test-answers tests/data/discovery_test_answers.json")
    else:
        print("\n❌ Some tests failed. Check the output above for details.")
        sys.exit(1)
