#!/usr/bin/env node

/**
 * Simple WebSocket Connection Test
 * 
 * This script tests if the frontend can establish a WebSocket connection 
 * to the backend using a mock authentication token.
 */

const WebSocket = require('ws');

const TEST_TOKEN = 'test-token-for-connection-verification';
const WS_URL = `ws://localhost:8000/api/v1/ws/${TEST_TOKEN}`;

console.log('🧪 Testing WebSocket Connection...');
console.log(`📡 URL: ${WS_URL}`);
console.log('⏳ Attempting connection...\n');

const ws = new WebSocket(WS_URL);

ws.on('open', () => {
    console.log('✅ WebSocket connection established successfully!');
    console.log('🎉 Real-time connection is working!\n');

    // Send a test message
    ws.send(JSON.stringify({
        type: 'ping',
        data: { message: 'test-connection' },
        timestamp: new Date().toISOString(),
        id: 'test-ping-1'
    }));

    console.log('📤 Sent test ping message');

    // Close after 2 seconds
    setTimeout(() => {
        ws.close();
        console.log('🔒 Connection closed');
        process.exit(0);
    }, 2000);
});

ws.on('message', (data) => {
    console.log('📥 Received message:', data.toString());
});

ws.on('error', (error) => {
    console.log('❌ WebSocket connection failed:');
    console.log('   Error:', error.message);
    console.log('\n🔍 This indicates either:');
    console.log('   1. Backend is not running on port 8000');
    console.log('   2. WebSocket endpoint is not available at /api/v1/ws/{token}');
    console.log('   3. Token authentication is required but test token is invalid');
    process.exit(1);
});

ws.on('close', (code, reason) => {
    if (code !== 1000) {
        console.log(`⚠️  Connection closed with code ${code}: ${reason}`);
        console.log('\n🔍 This might indicate:');
        console.log('   1. Authentication failed (invalid token)');
        console.log('   2. Server rejected the connection');
        console.log('   3. Connection was terminated unexpectedly');
    }
});

// Set a timeout for the connection attempt
setTimeout(() => {
    if (ws.readyState === WebSocket.CONNECTING) {
        console.log('⏰ Connection timeout - backend may not be responding');
        ws.close();
        process.exit(1);
    }
}, 10000);
