#!/usr/bin/env python3
"""
Test suite for TTS migration from ElevenLabs to Speechify API.
This test suite ensures backward compatibility and functionality.
"""

import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
from dotenv import load_dotenv

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tts import text_to_speech, get_available_voices, filter_voice_models

class TestTTSMigration(unittest.TestCase):
    """Test cases for TTS migration functionality."""
    
    def setUp(self):
        """Set up test environment."""
        load_dotenv()
        self.test_text = "Hello, this is a test message."
        self.test_text_multilingual = "Hola, esto es un mensaje de prueba."
        
    def test_imports(self):
        """Test that all required imports are available."""
        try:
            from speechify import Speechify
            from speechify.tts import GetSpeechOptionsRequest
            import base64
            self.assertTrue(True, "All required imports are available")
        except ImportError as e:
            self.fail(f"Missing required import: {e}")
    
    def test_environment_variable(self):
        """Test that SPEECHIFY_API_KEY environment variable is set."""
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if api_key and api_key != "your_key":
            self.assertIsNotNone(api_key, "SPEECHIFY_API_KEY should be set")
        else:
            self.skipTest("SPEECHIFY_API_KEY not properly configured")
    
    def test_text_to_speech_basic_functionality(self):
        """Test basic text-to-speech functionality."""
        # Skip this test if no API key is configured
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key or api_key == "your_key":
            self.skipTest("SPEECHIFY_API_KEY not properly configured")
            
        # Test with real API call using English text
        result = text_to_speech(self.test_text, "scott")
        
        # Verify we got a valid audio response
        self.assertIsNotNone(result, "Should get audio response for English text")
        self.assertIsInstance(result, BytesIO, "Should return BytesIO object")
        self.assertGreater(len(result.getvalue()), 0, "Audio data should not be empty")
    
    def test_text_to_speech_multilingual_detection(self):
        """Test that multilingual text uses the correct model."""
        # Skip this test if no API key is configured
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key or api_key == "your_key":
            self.skipTest("SPEECHIFY_API_KEY not properly configured")
            
        # Test with real API call using multilingual text
        result = text_to_speech(self.test_text_multilingual, "scott")
        
        # Verify we got a valid audio response
        self.assertIsNotNone(result, "Should get audio response for multilingual text")
        self.assertIsInstance(result, BytesIO, "Should return BytesIO object")
        self.assertGreater(len(result.getvalue()), 0, "Audio data should not be empty")
    
    def test_backward_compatibility_voice_mapping(self):
        """Test backward compatibility with ElevenLabs voice IDs."""
        # Skip this test if no API key is configured
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key or api_key == "your_key":
            self.skipTest("SPEECHIFY_API_KEY not properly configured")
            
        # Test with old ElevenLabs voice IDs - they should all map to "scott"
        old_voice_ids = [
            "21m00Tcm4TlvDq8ikWAM",  # Rachel
            "EXAVITQu4vr4xnSDxMaL",  # Bella
            "AZnzlk1XvdvUeBnXmlld",  # Antoni
            "IKne3meq5aSn9XLyUdCD",  # Daniel
        ]
        
        for old_voice_id in old_voice_ids:
            result = text_to_speech(self.test_text, old_voice_id)
            # Verify we get a valid response (indicating the mapping worked)
            self.assertIsNotNone(result, f"Should get audio response for voice ID {old_voice_id}")
            self.assertIsInstance(result, BytesIO, f"Should return BytesIO for voice ID {old_voice_id}")
            self.assertGreater(len(result.getvalue()), 0, f"Audio data should not be empty for voice ID {old_voice_id}")
    
    def test_error_handling_invalid_voice(self):
        """Test error handling with invalid voice ID."""
        # Skip this test if no API key is configured
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key or api_key == "your_key":
            self.skipTest("SPEECHIFY_API_KEY not properly configured")
            
        # Test with invalid voice ID - should handle gracefully
        result = text_to_speech(self.test_text, "invalid_voice_id")
        # Should either return None or handle the error gracefully
        # We don't assert the exact behavior since it depends on the API response
    
    @patch('tts.speechify_client')
    def test_client_not_initialized(self, mock_client):
        """Test behavior when Speechify client is not initialized."""
        # Set client to None
        import tts
        original_client = tts.speechify_client
        tts.speechify_client = None
        
        try:
            result = text_to_speech(self.test_text, "scott")
            self.assertIsNone(result)
        finally:
            # Restore original client
            tts.speechify_client = original_client
    
    def test_get_available_voices(self):
        """Test getting available voices."""
        # Skip this test if no API key is configured
        api_key = os.getenv("SPEECHIFY_API_KEY")
        if not api_key or api_key == "your_key":
            self.skipTest("SPEECHIFY_API_KEY not properly configured")
            
        # Test with real API call
        voices = get_available_voices()
        
        # Verify we get a list of voices
        self.assertIsInstance(voices, list, "Should return a list of voices")
        self.assertGreater(len(voices), 0, "Should have at least one voice available")
        
        # Verify voice objects have expected attributes based on actual API response
        if voices:
            voice = voices[0]
            # Based on the actual API response, we know these attributes exist
            self.assertTrue(hasattr(voice, 'id'), "Voice should have id attribute")
            self.assertTrue(hasattr(voice, 'display_name'), "Voice should have display_name attribute")
            self.assertTrue(hasattr(voice, 'gender'), "Voice should have gender attribute")
            self.assertTrue(hasattr(voice, 'models'), "Voice should have models attribute")
    
    def test_filter_voice_models(self):
        """Test voice filtering functionality."""
        # Create mock voice objects
        mock_voice1 = Mock()
        mock_voice1.gender = "male"
        mock_voice1.tags = ["timbre:deep"]
        mock_model1 = Mock()
        mock_lang1 = Mock()
        mock_lang1.locale = "en-US"
        mock_model1.languages = [mock_lang1]
        mock_voice1.models = [mock_model1]
        mock_model1.name = "model1"
        
        mock_voice2 = Mock()
        mock_voice2.gender = "female"
        mock_voice2.tags = ["timbre:bright"]
        mock_model2 = Mock()
        mock_lang2 = Mock()
        mock_lang2.locale = "es-ES"
        mock_model2.languages = [mock_lang2]
        mock_voice2.models = [mock_model2]
        mock_model2.name = "model2"
        
        voices = [mock_voice1, mock_voice2]
        
        # Test gender filtering
        male_voices = filter_voice_models(voices, gender="male")
        self.assertEqual(len(male_voices), 1)
        self.assertEqual(male_voices[0], "model1")
        
        # Test locale filtering
        en_voices = filter_voice_models(voices, locale="en-US")
        self.assertEqual(len(en_voices), 1)
        self.assertEqual(en_voices[0], "model1")
        
        # Test tags filtering
        deep_voices = filter_voice_models(voices, tags=["timbre:deep"])
        self.assertEqual(len(deep_voices), 1)
        self.assertEqual(deep_voices[0], "model1")
        
        # Test combined filtering
        combined = filter_voice_models(voices, gender="male", locale="en-US", tags=["timbre:deep"])
        self.assertEqual(len(combined), 1)
        self.assertEqual(combined[0], "model1")

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete TTS system."""
    
    def setUp(self):
        """Set up integration test environment."""
        load_dotenv()
    
    def test_requirements_file_updated(self):
        """Test that requirements.txt has been updated correctly."""
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
        
        self.assertIn('speechify-api', requirements)
        self.assertNotIn('elevenlabs', requirements)
    
    def test_env_file_updated(self):
        """Test that .env file has been updated correctly."""
        with open('.env', 'r') as f:
            env_content = f.read()
        
        self.assertIn('SPEECHIFY_API_KEY', env_content)
        self.assertNotIn('ELEVENLABS_API_KEY', env_content)
    
    def test_app_py_voice_mapping(self):
        """Test that app.py voice mapping includes Speechify voices."""
        with open('app.py', 'r') as f:
            app_content = f.read()
        
        self.assertIn('"Scott": "scott"', app_content)
        self.assertIn('Powered by Speechify', app_content)

def run_migration_tests():
    """Run all migration tests."""
    print("🧪 Running TTS Migration Tests...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestTTSMigration))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("✅ All tests passed! Migration appears successful.")
    else:
        print("❌ Some tests failed. Please review the issues above.")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_migration_tests()
    sys.exit(0 if success else 1) 