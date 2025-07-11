const http = require('http');

// Test the backend auth endpoint directly
const postData = JSON.stringify({
    email: 'test@example.com',
    password: 'TestPassword123!',
    name: 'Test User'
});

const options = {
    hostname: 'localhost',
    port: 8000,
    path: '/api/v1/auth/register',
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
        'Accept': 'application/json'
    }
};

const req = http.request(options, (res) => {
    console.log(`STATUS: ${res.statusCode}`);
    console.log(`HEADERS: ${JSON.stringify(res.headers)}`);
    
    let data = '';
    res.on('data', (chunk) => {
        data += chunk;
    });
    
    res.on('end', () => {
        console.log('RESPONSE:', data);
        try {
            const parsed = JSON.parse(data);
            console.log('PARSED:', JSON.stringify(parsed, null, 2));
        } catch (e) {
            console.log('Failed to parse JSON:', e.message);
        }
    });
});

req.on('error', (e) => {
    console.error(`Request error: ${e.message}`);
});

req.write(postData);
req.end();
