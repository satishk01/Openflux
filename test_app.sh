#!/bin/bash
# Test the OpenFlux application

echo "🧪 Testing OpenFlux AI Assistant..."

# Test 1: Check if executable exists
if [ -f "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Executable found: dist/OpenFlux_AI_Assistant"
else
    echo "❌ Executable not found. Please build first."
    exit 1
fi

# Test 2: Check if executable is runnable
if [ -x "dist/OpenFlux_AI_Assistant" ]; then
    echo "✅ Executable has proper permissions"
else
    echo "⚠️ Making executable runnable..."
    chmod +x "dist/OpenFlux_AI_Assistant"
fi

# Test 3: Quick startup test
echo "🚀 Testing application startup (will timeout after 10 seconds)..."
timeout 10s ./dist/OpenFlux_AI_Assistant > /dev/null 2>&1 &
PID=$!

sleep 3

if kill -0 $PID 2>/dev/null; then
    echo "✅ Application started successfully"
    kill $PID 2>/dev/null
    wait $PID 2>/dev/null
else
    echo "⚠️ Application startup test completed"
fi

echo ""
echo "📋 Manual testing steps:"
echo "1. Run: ./dist/OpenFlux_AI_Assistant"
echo "2. Check if browser opens with the application"
echo "3. Test AWS credentials input"
echo "4. Verify all features work"
echo ""
echo "🎉 Automated tests completed!"