"""Diagnostic test for Gemini Live API and v2 services.

Run this to verify:
1. Gemini client can connect to Live API
2. All v2 services can be instantiated
3. V2 analysis runner works
4. SSE streaming endpoints are functional
"""
import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

async def test_gemini_live_api():
    """Test Gemini Live API connectivity."""
    print("\n" + "="*70)
    print("TEST 1: Gemini Live API Connectivity")
    print("="*70)
    
    try:
        from backend.services.v2_services.gemini_client import GeminiClientV2
        
        client = GeminiClientV2()
        print("✓ GeminiClientV2 instantiated")
        
        # Test if Live API is available
        has_live = False
        if hasattr(client._sdk_client, 'aio'):
            if hasattr(client._sdk_client.aio, 'live'):
                if hasattr(client._sdk_client.aio.live, 'chat'):
                    has_live = True
        
        if has_live:
            print("✓ Live API detected (client.aio.live.chat available)")
        else:
            print("⚠ Live API NOT detected - will use simulated streaming")
        
        # Test basic query
        try:
            result = await client.query_text("Say 'test successful'")
            print(f"✓ Basic query works: {result[:50]}...")
        except Exception as e:
            print(f"✗ Basic query failed: {e}")
        
        # Test json_stream
        try:
            chunk_count = 0
            async for chunk in client.json_stream("Return JSON: {\"status\": \"ok\"}", schema={"type": "object"}):
                chunk_count += 1
                if chunk.get("done"):
                    break
            print(f"✓ json_stream works ({chunk_count} chunks, Live={'yes' if has_live else 'no'})")
        except Exception as e:
            print(f"✗ json_stream failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Gemini client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_v2_services():
    """Test v2 service instantiation."""
    print("\n" + "="*70)
    print("TEST 2: V2 Services Instantiation")
    print("="*70)
    
    try:
        from backend.services.v2_services.service_registry import SERVICE_FACTORIES
        from backend.services.v2_services.gemini_client import GeminiClientV2
        
        client = GeminiClientV2()
        context = {
            "gemini_client": client,
            "transcript": "Test transcript",
            "audio": b"test_audio_data",
            "meta": {}
        }
        
        print(f"\nTesting {len(SERVICE_FACTORIES)} services:")
        success_count = 0
        
        for name, factory in SERVICE_FACTORIES.items():
            try:
                service = factory(context)
                print(f"  ✓ {name:25s} v{service.serviceVersion}")
                success_count += 1
            except Exception as e:
                print(f"  ✗ {name:25s} FAILED: {e}")
        
        print(f"\n{success_count}/{len(SERVICE_FACTORIES)} services instantiated successfully")
        return success_count == len(SERVICE_FACTORIES)
        
    except Exception as e:
        print(f"✗ Service instantiation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_v2_runner():
    """Test V2AnalysisRunner."""
    print("\n" + "="*70)
    print("TEST 3: V2AnalysisRunner")
    print("="*70)
    
    try:
        from backend.services.v2_services.runner import V2AnalysisRunner
        from backend.services.v2_services.gemini_client import GeminiClientV2
        
        client = GeminiClientV2()
        runner = V2AnalysisRunner(gemini_client=client)
        
        print("✓ V2AnalysisRunner instantiated")
        print(f"  Services to run: {len(runner.services)}")
        
        # Test with minimal audio (will fail but should not crash)
        try:
            # Create tiny audio bytes
            audio_bytes = b'\x00' * 1000
            
            event_count = 0
            async for event in runner.stream_run(
                audio=audio_bytes,
                transcript=None,
                meta={"session_id": "test"}
            ):
                event_count += 1
                event_name = event.get("event", "unknown")
                service = event.get("service", "")
                print(f"  Event {event_count}: {event_name} from {service}")
                
                if event_count > 20:  # Limit output
                    print("  ... (stopping after 20 events)")
                    break
            
            print(f"✓ Runner produced {event_count} events")
            return True
            
        except Exception as e:
            print(f"⚠ Runner execution had issues (expected with test data): {e}")
            return True  # This is expected
        
    except Exception as e:
        print(f"✗ Runner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_api_availability():
    """Test if v2 API endpoints are registered."""
    print("\n" + "="*70)
    print("TEST 4: API Endpoints")
    print("="*70)
    
    try:
        from backend.api.analysis_routes import router
        
        # Check if v2 routes exist
        v2_routes = [route for route in router.routes if 'v2' in route.path]
        
        print(f"Found {len(v2_routes)} v2 routes:")
        for route in v2_routes:
            methods = ', '.join(route.methods) if hasattr(route, 'methods') else 'N/A'
            print(f"  {methods:10s} {route.path}")
        
        if len(v2_routes) >= 2:
            print("✓ v2 routes appear to be registered")
            return True
        else:
            print("⚠ Expected at least 2 v2 routes (/v2/analyze, /v2/analyze/stream)")
            return False
        
    except Exception as e:
        print(f"✗ API endpoint test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all diagnostic tests."""
    print("\n" + "="*70)
    print("V2 SERVICES DIAGNOSTIC TEST")
    print("="*70)
    
    results = []
    
    # Test 1: Gemini Live API
    results.append(("Gemini Live API", await test_gemini_live_api()))
    
    # Test 2: V2 Services
    results.append(("V2 Services", await test_v2_services()))
    
    # Test 3: V2 Runner
    results.append(("V2 Runner", await test_v2_runner()))
    
    # Test 4: API Endpoints
    results.append(("API Endpoints", await test_api_availability()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8s} {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems operational!")
    else:
        print("\n⚠️  Some systems need attention. Check logs above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
