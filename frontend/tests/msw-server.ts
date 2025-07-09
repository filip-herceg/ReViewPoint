
import { setupServer } from 'msw/node';
import { handlers } from './msw-handlers';
import { testLogger } from './test-utils';

export const server = setupServer(...handlers);

server.events.on('request:start', ({ request }) => {
    testLogger.info(`[MSW] Request start: ${request.method} ${request.url}`);
});
server.events.on('request:match', ({ request }) => {
    testLogger.debug(`[MSW] Request matched: ${request.method} ${request.url}`);
});
server.events.on('request:unhandled', ({ request }) => {
    testLogger.warn(`[MSW] Unhandled request: ${request.method} ${request.url}`);
});
server.events.on('request:end', ({ request }) => {
    testLogger.info(`[MSW] Request end: ${request.method} ${request.url}`);
});
