#!/usr/bin/env python3
"""
Master Script: Fix All Issues and Test Thoroughly
Runs all fixes and comprehensive verification before committing
"""
import subprocess
import sys
import time

def run_script(script_name, description):
    """Run a Python script and return success status"""
    print("\n" + "="*70)
    print(f"🔧 {description}")
    print("="*70)
    
    try:
        result = subprocess.run(
            [sys.executable, f'scripts/{script_name}'],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ {description} - ERROR: {str(e)}")
        return False

def main():
    print("="*70)
    print("  MEETINGMIND - FIX ALL ISSUES & COMPREHENSIVE TEST")
    print("="*70)
    print("\nThis script will:")
    print("  1. Fix SQS permissions")
    print("  2. Enable S3 versioning")
    print("  3. Setup CloudWatch alarms")
    print("  4. Run comprehensive access check")
    print("  5. Verify all services are working")
    print("\n" + "="*70)
    
    input("\nPress Enter to continue...")
    
    results = {}
    
    # Step 1: Fix SQS permissions
    results['SQS Permissions'] = run_script(
        'fix-sqs-permissions.py',
        'Step 1: Fix SQS Permissions'
    )
    time.sleep(2)
    
    # Step 2: Enable S3 versioning
    results['S3 Versioning'] = run_script(
        'enable-s3-versioning.py',
        'Step 2: Enable S3 Versioning'
    )
    time.sleep(2)
    
    # Step 3: Setup CloudWatch alarms
    results['CloudWatch Alarms'] = run_script(
        'setup-cloudwatch-alarms.py',
        'Step 3: Setup CloudWatch Alarms'
    )
    time.sleep(2)
    
    # Step 4: Run comprehensive access check
    print("\n" + "="*70)
    print("🔍 Step 4: Comprehensive Access Check")
    print("="*70)
    print("\n⏳ Waiting 5 seconds for IAM propagation...")
    time.sleep(5)
    
    results['Access Check'] = run_script(
        'comprehensive-access-check.py',
        'Step 4: Verify All Services'
    )
    
    # Final Summary
    print("\n" + "="*70)
    print("  FINAL SUMMARY")
    print("="*70)
    
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    print(f"\n📊 Results: {success_count}/{total_count} steps successful\n")
    
    for step, success in results.items():
        icon = "✅" if success else "❌"
        print(f"   {icon} {step}")
    
    print("\n" + "="*70)
    
    if success_count == total_count:
        print("🎉 ALL FIXES APPLIED SUCCESSFULLY!")
        print("\n✅ Ready to commit:")
        print("   - SQS permissions fixed")
        print("   - S3 versioning enabled")
        print("   - CloudWatch alarms configured")
        print("   - All services verified")
        print("\n💡 Next steps:")
        print("   1. Review the changes above")
        print("   2. Run: git add -A")
        print("   3. Run: git commit -m 'fix: enable monitoring and fix permissions'")
        print("   4. Run: git push origin master")
    else:
        print("⚠️  SOME FIXES FAILED")
        print("\n💡 Review the errors above before committing")
    
    print("="*70)
    
    return success_count == total_count

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
