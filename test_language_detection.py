#!/usr/bin/env python3
"""
Test script for language detection functionality in Recipe Genie bot
"""

from langdetect import detect, LangDetectException

def detect_language(text: str) -> str:
    """
    Detect the language of the input text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: Language code ('es' for Spanish, 'en' for English, default to 'en')
    """
    try:
        lang = detect(text)
        return lang if lang in ['es', 'en'] else 'en'
    except LangDetectException:
        return 'en'

def test_language_detection():
    """Test the language detection with various inputs."""
    
    test_cases = [
        # English test cases
        ("tomato, chicken, rice", "en"),
        ("how to make pancakes", "en"),
        ("recipe for chocolate cake", "en"),
        ("eggs, milk, flour, sugar", "en"),
        ("beef stir fry recipe", "en"),
        
        # Spanish test cases
        ("tomate, pollo, arroz", "es"),
        ("cómo hacer panqueques", "es"),
        ("receta de pastel de chocolate", "es"),
        ("huevos, leche, harina, azúcar", "es"),
        ("receta de salteado de res", "es"),
        
        # Mixed cases (should default to English)
        ("hello world", "en"),
        ("hola mundo", "es"),
        ("recipe receta", "en"),  # Mixed, should default to English
    ]
    
    print("Testing Language Detection:")
    print("=" * 50)
    
    correct = 0
    total = len(test_cases)
    
    for text, expected in test_cases:
        detected = detect_language(text)
        status = "✅" if detected == expected else "❌"
        print(f"{status} Input: '{text}'")
        print(f"   Expected: {expected}, Detected: {detected}")
        print()
        
        if detected == expected:
            correct += 1
    
    print(f"Results: {correct}/{total} tests passed ({correct/total*100:.1f}%)")
    
    if correct == total:
        print("🎉 All language detection tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")

if __name__ == "__main__":
    test_language_detection()