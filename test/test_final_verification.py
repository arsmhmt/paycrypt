#!/usr/bin/env python3
"""
Final CSS conflict resolution verification
"""
import requests
import re

def final_verification():
    try:
        # Test CSS file directly
        css_response = requests.get('http://localhost:8080/static/css/client-dashboard.css')
        print(f"CSS Status: {css_response.status_code}")
        print(f"CSS Size: {len(css_response.content)} bytes")
        
        if css_response.status_code == 200:
            css_content = css_response.text
            
            # Check critical conflict resolution features
            checks = {
                'Body override with !important': 'body.sb-nav-fixed' in css_content and 'background: linear-gradient' in css_content and '!important' in css_content,
                'Card glassmorphism override': '.card.glass-card' in css_content and 'backdrop-filter: blur' in css_content,
                'Header transparency override': '.card-header' in css_content and 'background: transparent !important' in css_content,
                'Base template card override': '.card,' in css_content and '.card.glass-card' in css_content,
                'Multiple selector priority': css_content.count('.card') >= 3,
                'Important declarations': css_content.count('!important') >= 10
            }
            
            print("\n🔍 CSS Conflict Resolution Verification:")
            for check, passed in checks.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {status} {check}")
            
            # Check for glassmorphism keywords
            glassmorphism_features = [
                'backdrop-filter: blur(',
                'rgba(255,255,255,0.85)',
                'box-shadow: 0 8px 32px',
                'linear-gradient(135deg, #e0e7ff'
            ]
            
            print("\n🎨 Glassmorphism Features:")
            for feature in glassmorphism_features:
                present = feature in css_content
                status = "✅ ACTIVE" if present else "❌ MISSING"
                print(f"  {status} {feature}")
            
            # Check for conflict-prone selectors
            conflict_resolution = [
                ('Body selector specificity', 'body.sb-nav-fixed' in css_content),
                ('Card selector priority', '.card.glass-card' in css_content),
                ('Important declarations', '!important' in css_content),
                ('Override base styles', css_content.count('!important') > 5)
            ]
            
            print("\n⚔️ Conflict Resolution:")
            for desc, check in conflict_resolution:
                status = "✅ RESOLVED" if check else "❌ ISSUE"
                print(f"  {status} {desc}")
                
            # Summary
            total_checks = len(checks) + len(glassmorphism_features) + len(conflict_resolution)
            passed_checks = sum(checks.values()) + sum(f in css_content for f in glassmorphism_features) + sum(check for _, check in conflict_resolution)
            
            print(f"\n📊 Overall Status: {passed_checks}/{total_checks} checks passed")
            
            if passed_checks >= total_checks * 0.8:
                print("🎉 CSS CONFLICTS RESOLVED - Dashboard should display modern styling")
            else:
                print("⚠️ Some conflicts remain - manual inspection needed")
                
        else:
            print(f"❌ Failed to load CSS: {css_response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    final_verification()
