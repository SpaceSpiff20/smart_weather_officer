# TTS Migration Guide: ElevenLabs to Speechify

## Overview
This document outlines the migration from ElevenLabs TTS API to Speechify API in the Smart Weather Officer application.

## Changes Made

### 1. Core TTS Module (`tts.py`)
- **Replaced**: ElevenLabs client with Speechify client
- **Added**: Backward compatibility for existing voice IDs
- **Enhanced**: Automatic language detection for model selection
- **Added**: Voice filtering and management functions

### 2. Dependencies (`requirements.txt`)
- **Removed**: `elevenlabs`
- **Added**: `speechify-api`

### 3. Environment Variables (`.env`)
- **Removed**: `ELEVENLABS_API_KEY`
- **Added**: `SPEECHIFY_API_KEY`

### 4. Application Interface (`app.py`)
- **Updated**: Voice selection options to include Speechify voices
- **Maintained**: Backward compatibility with existing voice mappings
- **Updated**: Provider branding from ElevenLabs to Speechify

## Backward Compatibility

### Voice ID Mapping
The migration maintains backward compatibility by mapping old ElevenLabs voice IDs to Speechify equivalents:

| ElevenLabs Voice | ElevenLabs ID | Speechify ID |
|------------------|---------------|--------------|
| Rachel           | 21m00Tcm4TlvDq8ikWAM | scott |
| Bella            | EXAVITQu4vr4xnSDxMaL | scott |
| Antoni           | AZnzlk1XvdvUeBnXmlld | scott |
| Daniel           | IKne3meq5aSn9XLyUdCD | scott |

### Function Signature
The `text_to_speech(text: str, voice_id: str) -> BytesIO | None` function signature remains unchanged, ensuring existing code continues to work.

## New Features

### 1. Automatic Language Detection
The system now automatically detects if text contains non-English characters and selects the appropriate model:
- `simba-english` for English text
- `simba-multilingual` for text with non-ASCII characters

### 2. Enhanced Voice Management
- `get_available_voices()`: Retrieve all available Speechify voices
- `filter_voice_models()`: Filter voices by gender, locale, and tags

### 3. Improved Error Handling
- Graceful handling of API initialization failures
- Better error messages for debugging

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
1. Sign up for Speechify API at https://console.sws.speechify.com/signup
2. Update your `.env` file:
```env
SPEECHIFY_API_KEY='your_actual_speechify_api_key'
```

### 3. Test the Migration
```bash
python test_tts_migration.py
```

## API Differences

### ElevenLabs vs Speechify

| Feature | ElevenLabs | Speechify |
|---------|------------|-----------|
| Voice Settings | Stability, Similarity Boost, Style, Speaker Boost, Speed | Loudness Normalization, Text Normalization |
| Audio Format | MP3 with specific encoding | MP3, AAC, OGG, WAV |
| Language Support | Multilingual model | English + Multilingual models |
| Voice Selection | Large voice library | Curated voice selection |

### Lost Functionality
1. **Voice Settings**: ElevenLabs' granular voice control (stability, similarity_boost, style, speaker_boost, speed) is not available in Speechify
2. **Voice Variety**: Reduced voice selection compared to ElevenLabs' extensive library
3. **Real-time Streaming**: ElevenLabs provided streaming audio chunks, Speechify returns complete audio data

### Gained Functionality
1. **Language Detection**: Automatic model selection based on text content
2. **Voice Filtering**: Advanced voice filtering by gender, locale, and tags
3. **Simplified API**: Cleaner, more straightforward API interface

## Testing

### Running Tests
```bash
python test_tts_migration.py
```

### Test Coverage
- ✅ Import validation
- ✅ Environment variable configuration
- ✅ Basic TTS functionality
- ✅ Multilingual text detection
- ✅ Backward compatibility
- ✅ Error handling
- ✅ Voice management functions
- ✅ Integration tests

## Troubleshooting

### Common Issues

1. **"Speechify client not initialized"**
   - Check that `SPEECHIFY_API_KEY` is set in `.env`
   - Verify the API key is valid

2. **Import errors**
   - Ensure `speechify-api` is installed: `pip install speechify-api`

3. **Audio generation fails**
   - Check API key permissions
   - Verify text input is not empty
   - Check network connectivity

### Debug Mode
Enable debug logging by setting the environment variable:
```bash
export DEBUG_TTS=1
```

## Performance Considerations

### Audio Quality
- Speechify provides high-quality audio output
- Automatic language detection may improve pronunciation for non-English text

### API Limits
- Check Speechify's rate limits and billing
- Consider implementing caching for frequently used text

## Future Enhancements

1. **Voice Caching**: Cache generated audio for repeated text
2. **Multiple Voice Support**: Add more Speechify voices to the selection
3. **Advanced Filtering**: Implement more sophisticated voice filtering
4. **Audio Post-processing**: Add audio enhancement features

## Support

For issues related to:
- **Speechify API**: Contact Speechify support
- **Migration**: Review this guide and test suite
- **Application**: Check the application logs and error messages 