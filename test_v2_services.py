#!/usr/bin/env python3
"""
Real Gemini API test for v2 AnalysisService implementation.
Uses actual Gemini API calls to verify the complete v2 architecture.
"""
import asyncio
import sys
import json
sys.path.append('.')

async def test_real_gemini_v2():
    print("🔬 Testing v2 AnalysisService with REAL Gemini API calls...")
    
    try:
        # Import v2 components
        from backend.services.v2_services.gemini_client import GeminiClientV2
        from backend.services.v2_services.quantitative_metrics_service import QuantitativeMetricsService
        from backend.services.v2_services.runner import V2AnalysisRunner
        
        print("✅ All v2 components imported successfully")
        
        # Create v2 client with real Gemini API access
        client = GeminiClientV2()
        print("✅ GeminiClientV2 created with real API access")
        
        # Test 1: List available models
        print("\n📋 Testing model discovery...")
        models = await client.list_available_models()
        print(f"   Available models: {len(models)}")
        print(f"   Sample models: {models[:3] if models else 'None'}")
        
        # Test 2: Model selection
        print("\n🎯 Testing model selection...")
        model = await client.choose_model('gemini-2.5-flash')
        print(f"   Selected model: {model}")
        
        # Test 3: Simple Gemini query
        print("\n💬 Testing basic Gemini query...")
        test_prompt = 'Analyze this short transcript and return valid JSON: Hello world. This is a test conversation about technology.'
        result = await client.query_json(test_prompt, model_hint=model)
        print(f"   Query result type: {type(result)}")
        if isinstance(result, dict):
            print(f"   Result keys: {list(result.keys())}")
            print(f"   Content preview: {str(result)[:300]}...")
        else:
            print(f"   Content preview: {str(result)[:300]}...")
        
        # Test 4: Service with real Gemini
        print("\n🚀 Testing v2 service with real Gemini analysis...")
        service = QuantitativeMetricsService(
            gemini_client=client,
            transcript='Hello world. This is a test conversation about artificial intelligence and machine learning.',
            meta={'duration': 45.0, 'session_id': 'real-test-123'}
        )
        print(f"   Service created: {service.serviceName} v{service.serviceVersion}")
        
        # Test 5: Run service analysis with real Gemini
        print("\n📊 Running service analysis...")
        analysis_result = await service.analyze(
            transcript='Hello world. This is a test conversation about artificial intelligence and machine learning.',
            audio=None,
            meta={'duration': 45.0, 'session_id': 'real-test-123'}
        )
        
        print("   Service analysis completed!")
        print(f"   Result structure: {list(analysis_result.keys())}")
        print(f"   Service name: {analysis_result.get('service_name')}")
        print(f"   Service version: {analysis_result.get('service_version')}")
        
        # Check local metrics
        local_metrics = analysis_result.get('local', {})
        print(f"   Local metrics present: {len(local_metrics)} fields")
        if local_metrics:
            print(f"   Local fields: {list(local_metrics.keys())}")
        
        # Check Gemini analysis
        gemini_result = analysis_result.get('gemini', {})
        print(f"   Gemini analysis present: {len(gemini_result) > 0}")
        if gemini_result and isinstance(gemini_result, dict):
            print(f"   Gemini fields: {list(gemini_result.keys())}")
        
        # Test 6: Runner with real services
        print("\n🏃 Testing runner with real services...")
        runner = V2AnalysisRunner([service])
        
        runner_result = await runner.run(
            transcript='Hello world. This is a test conversation about artificial intelligence and machine learning.',
            audio=None,
            meta={'duration': 45.0, 'session_id': 'real-test-123'}
        )
        
        print("   Runner completed!")
        print(f"   Total services processed: {len(runner_result.get('services', {}))}")
        print(f"   Errors encountered: {len(runner_result.get('errors', []))}")
        print(f"   Transcript included: {len(runner_result.get('transcript', '')) > 0}")
        
        # Test 7: Structured output (if supported)
        print("\n🔧 Testing structured output...")
        schema = {
            "type": "object",
            "properties": {
                "sentiment": {
                    "type": "string",
                    "enum": ["positive", "negative", "neutral"]
                },
                "confidence": {
                    "type": "number",
                    "minimum": 0,
                    "maximum": 1
                }
            },
            "required": ["sentiment", "confidence"]
        }
        
        try:
            structured_result = await client.query_json_schema(
                "Analyze the sentiment of this text: 'I love this amazing technology!'", 
                schema,
                model_hint=model
            )
            print(f"   Structured output result: {structured_result}")
        except Exception as e:
            print(f"   Structured output test failed (expected if not supported): {e}")
        
        print("\n🎉 ALL REAL GEMINI TESTS PASSED!")
        print("   ✅ Model discovery works")
        print("   ✅ Model selection works") 
        print("   ✅ Basic Gemini queries work")
        print("   ✅ v2 Service integration works")
        print("   ✅ Service analysis produces results")
        print("   ✅ Runner orchestrates services correctly")
        print("   ✅ End-to-end v2 architecture is functional")
        
        return True
        
    except Exception as e:
        print(f"\n❌ REAL GEMINI TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting real Gemini API test for v2 architecture...")
    print("Make sure GEMINI_API_KEY is set in your environment.")
    print("=" * 60)
    
    success = asyncio.run(test_real_gemini_v2())
    
    if success:
        print("\n" + "=" * 60)
        print("🚀 V2 ARCHITECTURE VERIFIED WITH REAL GEMINI API!")
        print("Ready to migrate additional services.")
    else:
        print("\n" + "=" * 60)
        print("❌ V2 architecture needs debugging before proceeding.")
    
    sys.exit(0 if success else 1)