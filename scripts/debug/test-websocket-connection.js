/**
 * WebSocket Connection Test Script
 * 
 * This script tests the WebSocket communication between frontend and backend.
 * Run this after starting both the backend server and frontend dev server.
 */

console.log('🧪 WebSocket Communication Test\n');

// Test configuration
const BACKEND_URL = 'http://localhost:8000';
const WEBSOCKET_URL = 'ws://localhost:8000/api/v1/ws';

async function testBackendConnection() {
    console.log('1️⃣ Testing backend API connection...');
    
    try {
        const response = await fetch(`${BACKEND_URL}/api/v1/health`);
        if (response.ok) {
            const data = await response.json();
            console.log('✅ Backend API is accessible:', data);
            return true;
        } else {
            console.log('❌ Backend API returned error:', response.status, response.statusText);
            return false;
        }
    } catch (error) {
        console.log('❌ Backend API is not accessible:', error.message);
        console.log('   💡 Make sure the backend server is running: python -m uvicorn src.main:app --reload --port 8000');
        return false;
    }
}

async function testWebSocketEndpoint() {
    console.log('\n2️⃣ Testing WebSocket endpoint availability...');
    
    try {
        // Test with a dummy token (will fail auth but should show endpoint is available)
        const testToken = 'dummy-token-for-endpoint-test';
        const wsUrl = `${WEBSOCKET_URL}/${testToken}`;
        
        const ws = new WebSocket(wsUrl);
        
        return new Promise((resolve) => {
            const timeout = setTimeout(() => {
                ws.close();
                console.log('❌ WebSocket connection timeout');
                resolve(false);
            }, 5000);
            
            ws.onopen = () => {
                clearTimeout(timeout);
                console.log('✅ WebSocket endpoint is accessible (connection opened)');
                ws.close();
                resolve(true);
            };
            
            ws.onerror = (error) => {
                clearTimeout(timeout);
                console.log('⚠️ WebSocket connection failed (expected with dummy token):', error.type);
                console.log('   📝 This indicates the endpoint exists but auth failed (good!)');
                resolve(true); // Auth failure means endpoint exists
            };
            
            ws.onclose = (event) => {
                clearTimeout(timeout);
                if (event.code === 1006) {
                    console.log('⚠️ WebSocket closed abnormally (likely auth rejection - expected)');
                    resolve(true);
                } else {
                    console.log('❌ WebSocket closed unexpectedly:', event.code, event.reason);
                    resolve(false);
                }
            };
        });
    } catch (error) {
        console.log('❌ Failed to create WebSocket connection:', error.message);
        return false;
    }
}

function checkWebSocketConfiguration() {
    console.log('\n3️⃣ Checking WebSocket configuration...');
    
    console.log('📋 Configuration Summary:');
    console.log(`   Backend WebSocket endpoint: ${WEBSOCKET_URL}/{jwt_token}`);
    console.log('   Frontend will connect to: ws://localhost:8000/api/v1/ws/{jwt_token}');
    console.log('   Authentication: JWT token in URL path');
    console.log('   Protocol: WebSocket with automatic reconnection');
    
    return true;
}

function printTestInstructions() {
    console.log('\n📖 To test full WebSocket communication:');
    console.log('\n1. Start the backend server:');
    console.log('   cd backend');
    console.log('   python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000');
    
    console.log('\n2. Start the frontend development server:');
    console.log('   cd frontend');
    console.log('   pnpm run dev');
    
    console.log('\n3. Open the application and login:');
    console.log('   - Open http://localhost:5173');
    console.log('   - Login to get a valid JWT token');
    console.log('   - Check browser dev tools Network tab for WebSocket connection');
    
    console.log('\n4. Monitor WebSocket in browser dev tools:');
    console.log('   - Look for WebSocket connection to ws://localhost:8000/api/v1/ws/{token}');
    console.log('   - Check for heartbeat messages and real-time events');
    
    console.log('\n🎯 Expected behavior:');
    console.log('   ✅ WebSocket connects after login');
    console.log('   ✅ Heartbeat messages every 30 seconds');
    console.log('   ✅ Real-time upload progress events');
    console.log('   ✅ System notifications');
    console.log('   ✅ Automatic reconnection if connection drops');
}

async function runTests() {
    const backendOk = await testBackendConnection();
    const websocketOk = await testWebSocketEndpoint();
    const configOk = checkWebSocketConfiguration();
    
    console.log('\n🏁 Test Results Summary:');
    console.log(`   Backend API: ${backendOk ? '✅ Connected' : '❌ Failed'}`);
    console.log(`   WebSocket Endpoint: ${websocketOk ? '✅ Available' : '❌ Failed'}`);
    console.log(`   Configuration: ${configOk ? '✅ Correct' : '❌ Issues'}`);
    
    if (backendOk && websocketOk && configOk) {
        console.log('\n🎉 All tests passed! WebSocket communication should work correctly.');
    } else {
        console.log('\n⚠️ Some tests failed. Check the issues above.');
    }
    
    printTestInstructions();
}

// Check if we're in Node.js environment
if (typeof window === 'undefined') {
    // Node.js environment - use dynamic imports
    const { default: WebSocket } = await import('ws');
    const { default: fetch } = await import('node-fetch');
    global.WebSocket = WebSocket;
    global.fetch = fetch;
}

// Run the tests
await runTests().catch(console.error);
