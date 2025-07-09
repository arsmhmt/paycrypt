#!/usr/bin/env python3
"""
Script to clear rate limiting data
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.utils.security import rate_limiter

def clear_rate_limits():
    """Clear all rate limiting data"""
    app = create_app()
    
    with app.app_context():
        try:
            # If using Redis
            if hasattr(rate_limiter, 'redis') and rate_limiter.redis:
                try:
                    keys = list(rate_limiter.redis.keys('rate_limit:*'))
                    if keys:
                        rate_limiter.redis.delete(*keys)
                        print(f"✅ Cleared {len(keys)} rate limit entries from Redis")
                    else:
                        print("✅ No rate limit entries found in Redis")
                except Exception as e:
                    print(f"⚠️  Redis error: {e}")
                    # Fall back to memory store clearing
                    from app.utils.security import _memory_store
                    _memory_store.clear()
                    print("✅ Cleared in-memory rate limit data as fallback")
            else:
                # If using memory store
                from app.utils.security import _memory_store
                if _memory_store:
                    _memory_store.clear()
                    print("✅ Cleared in-memory rate limit data")
                else:
                    print("✅ No in-memory rate limit data found")
                    
            print("✅ Rate limits cleared successfully")
            
        except Exception as e:
            print(f"❌ Error clearing rate limits: {e}")

if __name__ == "__main__":
    clear_rate_limits()
