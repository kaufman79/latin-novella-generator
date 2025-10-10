#!/bin/bash
echo "🏛️ Latin Book Engine - Streamlit App"
echo "Starting app..."
echo ""
echo "📌 Open in browser: http://localhost:8501"
echo ""

# Set library paths for WeasyPrint to find Homebrew libraries
export DYLD_LIBRARY_PATH="/opt/homebrew/lib:$DYLD_LIBRARY_PATH"

streamlit run app.py
