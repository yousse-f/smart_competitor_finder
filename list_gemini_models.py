#!/usr/bin/env python3
"""List available Gemini models"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv("backend/.env")

import google.generativeai as genai

api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

print("\n📋 Available Gemini Models:\n")
print("="*80)

for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"✅ {model.name}")
        print(f"   Description: {model.description}")
        print(f"   Methods: {', '.join(model.supported_generation_methods)}")
        print("-"*80)

print("\n💡 Use one of these model names in your code (without 'models/' prefix)")
