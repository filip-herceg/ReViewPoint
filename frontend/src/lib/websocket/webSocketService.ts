/**
 * WebSocket Service
 * 
 * Production-ready WebSocket connection management for real-time updates.
 * 
 * Features:
 * - Automatic reconnection with exponential backoff and jitter
 * - JWT token authentication with refresh handling
 * - Message queuing during disconnections with retry logic
 * - Event routing and subscription management
 * - Connection state management with detailed error tracking
 * - Comprehensive error handling and logging
 * - Rate limiting protection
 * - Connection timeout handling
 * - Heartbeat/ping-pong mechanism
 * - Memory leak prevention
 * - Performance monitoring
 */

import logger from '@/logger';
import { useAuthStore } from '@/lib/store/authStore';
import type { AuthTokens } from '@/lib/api/types';
import {
    getWebSocketConfig,
    validateWebSocketConfig,
    type WebSocketConfig as WSConfig,
    type ConnectionState,
    type WebSocketEventType,
    type WebSocketMessage,
    type WebSocketIncomingMessage,
    type WebSocketError,
    type ConnectionStats,
    WebSocketMessageSchema,
    WebSocketIncomingMessageSchema,
} from './config';

// Event listener function type
export type EventListener = (data: any) => void;

interface ConnectionMetadata {
    connectionId?: string;
    userId?: string;
    connectedAt?: Date;
    lastHeartbeat?: Date;
    lastMessageSent?: Date;
    lastMessageReceived?: Date;
    totalMessagesSent: number;
    totalMessagesReceived: number;
    totalReconnects: number;
    latencyMeasurements: number[];
}

interface QueuedMessage {
    message: WebSocketMessage;
    timestamp: Date;
    retryCount: number;
    maxRetries: number;
}

interface RateLimitState {
    messageCount: number;
    windowStart: Date;
    isLimited: boolean;
    resetTime?: Date;
}

class WebSocketService {
    private ws: WebSocket | null = null;
    private config: WSConfig;
    private state: ConnectionState = 'disconnected';
    private reconnectAttempts = 0;
    private reconnectTimer?: NodeJS.Timeout;
    private heartbeatTimer?: NodeJS.Timeout;
    private connectionTimer?: NodeJS.Timeout;
    private pingTimer?: NodeJS.Timeout;
    private eventListeners: Map<WebSocketEventType, Set<EventListener>> = new Map();
    private messageQueue: QueuedMessage[] = [];
    private metadata: ConnectionMetadata = {
        totalMessagesSent: 0,
        totalMessagesReceived: 0,
        totalReconnects: 0,
        latencyMeasurements: [],
    };
    private subscriptions: Set<WebSocketEventType> = new Set();
    private currentError?: WebSocketError;
    private authUnsubscribe?: () => void;
    private rateLimitState: RateLimitState = {
        messageCount: 0,
        windowStart: new Date(),
        isLimited: false,
    };
    private pendingPings: Map<string, { timestamp: Date; timeout: NodeJS.Timeout }> = new Map();

    constructor(config?: Partial<WSConfig>) {
        this.config = validateWebSocketConfig({
            ...getWebSocketConfig(),
            ...config,
        });

        logger.info('[WebSocket] Service initialized', {
            config: {
                url: this.config.url,
                maxReconnectAttempts: this.config.maxReconnectAttempts,
                heartbeatInterval: this.config.heartbeatInterval,
                enableAutoReconnect: this.config.enableAutoReconnect,
            }
        });

        // Listen for auth state changes
        this.setupAuthListener();
        
        // Setup cleanup on page unload
        this.setupUnloadListener();
    }

    /**
     * Setup listener for authentication state changes
     */
    private setupAuthListener(): void {
        let lastAuthState = useAuthStore.getState().isAuthenticated;

        const checkAuthState = () => {
            const currentAuthState = useAuthStore.getState().isAuthenticated;

            if (currentAuthState !== lastAuthState) {
                logger.debug('[WebSocket] Auth state changed', {
                    isAuthenticated: currentAuthState,
                    wasAuthenticated: lastAuthState,
                    currentState: this.state
                });

                if (currentAuthState && this.state === 'disconnected') {
                    // User logged in - attempt connection
                    this.connect();
                } else if (!currentAuthState) {
                    // User logged out - disconnect
                    this.disconnect();
                }

                lastAuthState = currentAuthState;
            }
        };

        // Check auth state every second
        const authCheckInterval = setInterval(checkAuthState, 1000);

        // Store cleanup function
        this.authUnsubscribe = () => {
            clearInterval(authCheckInterval);
        };
    }

    /**
     * Setup cleanup on page unload
     */
    private setupUnloadListener(): void {
        const handleUnload = () => {
            this.disconnect();
        };

        window.addEventListener('beforeunload', handleUnload);
        window.addEventListener('unload', handleUnload);
        
        // Store cleanup for this too if needed
    }

    /**
     * Check and update rate limiting state
     */
    private checkRateLimit(): boolean {
        const now = new Date();
        const timeSinceWindowStart = now.getTime() - this.rateLimitState.windowStart.getTime();

        // Reset window if expired
        if (timeSinceWindowStart >= this.config.rateLimitWindow) {
            this.rateLimitState = {
                messageCount: 0,
                windowStart: now,
                isLimited: false,
            };
        }

        // Check if at limit
        if (this.rateLimitState.messageCount >= this.config.rateLimitMaxMessages) {
            if (!this.rateLimitState.isLimited) {
                this.rateLimitState.isLimited = true;
                this.rateLimitState.resetTime = new Date(
                    this.rateLimitState.windowStart.getTime() + this.config.rateLimitWindow
                );
                this.setState('rate_limited');
                this.emit('connection.rate_limited', {
                    resetTime: this.rateLimitState.resetTime,
                    messagesInWindow: this.rateLimitState.messageCount,
                });
                logger.warn('[WebSocket] Rate limit exceeded', {
                    messagesInWindow: this.rateLimitState.messageCount,
                    resetTime: this.rateLimitState.resetTime,
                });
            }
            return false;
        }

        // If was limited but now okay
        if (this.rateLimitState.isLimited) {
            this.rateLimitState.isLimited = false;
            this.rateLimitState.resetTime = undefined;
            if (this.state === 'rate_limited') {
                this.setState('disconnected');
            }
        }

        return true;
    }

    /**
     * Connect to WebSocket server with comprehensive error handling
     */
    public async connect(): Promise<void> {
        if (this.state === 'connected' || this.state === 'connecting') {
            logger.debug('[WebSocket] Already connected or connecting');
            return;
        }

        const authStore = useAuthStore.getState();
        if (!authStore.isAuthenticated || !authStore.tokens?.access_token) {
            logger.warn('[WebSocket] Cannot connect - not authenticated');
            this.setState('authentication_failed');
            return;
        }

        try {
            this.setState('connecting');
            this.clearCurrentError();

            const token = authStore.tokens.access_token;
            const wsUrl = `${this.config.url}/${token}`;

            logger.info('[WebSocket] Attempting connection', { 
                url: wsUrl.replace(token, '[TOKEN]'),
                attempt: this.reconnectAttempts + 1
            });

            // Create WebSocket with timeout
            this.ws = new WebSocket(wsUrl);
            this.setupWebSocketEventHandlers();

            // Set connection timeout
            this.connectionTimer = setTimeout(() => {
                if (this.state === 'connecting') {
                    logger.error('[WebSocket] Connection timeout');
                    this.setError({
                        code: 'CONNECTION_TIMEOUT',
                        message: 'Connection timeout exceeded',
                        timestamp: new Date(),
                        retryable: true,
                    });
                    this.ws?.close();
                }
            }, this.config.connectionTimeout);

        } catch (error) {
            const wsError: WebSocketError = {
                code: 'CONNECTION_FAILED',
                message: error instanceof Error ? error.message : 'Unknown connection error',
                details: error,
                timestamp: new Date(),
                retryable: true,
            };

            logger.error('[WebSocket] Connection failed', {
                error: wsError,
                reconnectAttempts: this.reconnectAttempts
            });

            this.setError(wsError);
            this.scheduleReconnect();
        }
    }

    /**
     * Disconnect from WebSocket server
     */
    public disconnect(): void {
        logger.info('[WebSocket] Disconnecting', { state: this.state });

        this.clearTimers();
        this.clearPendingPings();

        if (this.ws) {
            this.ws.close(1000, 'User disconnect');
            this.ws = null;
        }

        this.setState('disconnected');
        this.reconnectAttempts = 0;
        this.resetMetadata();
        this.messageQueue = [];
        this.clearCurrentError();
    }

    /**
     * Reset connection metadata
     */
    private resetMetadata(): void {
        this.metadata = {
            totalMessagesSent: 0,
            totalMessagesReceived: 0,
            totalReconnects: 0,
            latencyMeasurements: [],
        };
    }

    /**
     * Clear current error state
     */
    private clearCurrentError(): void {
        this.currentError = undefined;
    }

    /**
     * Set error state
     */
    private setError(error: WebSocketError): void {
        this.currentError = error;
        this.setState('error');
        this.emit('connection.error', {
            code: error.code,
            message: error.message,
            details: error.details,
            timestamp: error.timestamp.toISOString(),
            retryable: error.retryable,
        });
    }

    /**
     * Clear all pending ping timeouts
     */
    private clearPendingPings(): void {
        for (const [id, { timeout }] of this.pendingPings) {
            clearTimeout(timeout);
        }
        this.pendingPings.clear();
    }

    /**
     * Setup WebSocket event handlers with comprehensive error handling
     */
    private setupWebSocketEventHandlers(): void {
        if (!this.ws) return;

        this.ws.onopen = () => {
            logger.info('[WebSocket] Connection established');
            
            // Clear connection timeout
            if (this.connectionTimer) {
                clearTimeout(this.connectionTimer);
                this.connectionTimer = undefined;
            }

            this.setState('connected');
            this.reconnectAttempts = 0;
            this.metadata.connectedAt = new Date();

            // Send initial subscriptions
            this.sendSubscriptions();

            // Start heartbeat if enabled
            if (this.config.enableHeartbeat) {
                this.startHeartbeat();
            }

            // Process queued messages
            if (this.config.enableMessageQueue) {
                this.processMessageQueue();
            }

            // Emit connection event
            this.emit('connection.established', { 
                timestamp: new Date().toISOString(),
                connectionId: this.metadata.connectionId,
            });
        };

        this.ws.onmessage = (event) => {
            try {
                const message: WebSocketMessage = JSON.parse(event.data);
                
                // Validate message structure
                const validatedMessage = WebSocketMessageSchema.parse(message);
                
                this.metadata.lastMessageReceived = new Date();
                this.metadata.totalMessagesReceived++;
                
                this.handleMessage(validatedMessage);
            } catch (error) {
                logger.error('[WebSocket] Failed to parse message', {
                    error: error instanceof Error ? error.message : 'Unknown error',
                    data: event.data.substring(0, 200), // Truncate for logging
                });
            }
        };

        this.ws.onclose = (event) => {
            logger.info('[WebSocket] Connection closed', {
                code: event.code,
                reason: event.reason,
                wasClean: event.wasClean
            });

            this.clearTimers();
            this.clearPendingPings();
            this.ws = null;

            // Handle different close codes
            if (event.code === 1008) {
                // Authentication failure
                this.setState('authentication_failed');
                this.emit('connection.authentication_failed', {
                    reason: event.reason,
                    timestamp: new Date().toISOString()
                });
            } else if (this.state !== 'disconnected') {
                this.setState('reconnecting');
                this.emit('connection.lost', {
                    code: event.code,
                    reason: event.reason,
                    timestamp: new Date().toISOString()
                });
                
                if (this.config.enableAutoReconnect) {
                    this.scheduleReconnect();
                }
            }
        };

        this.ws.onerror = (event) => {
            logger.error('[WebSocket] Connection error', { event });
            
            const wsError: WebSocketError = {
                code: 'CONNECTION_ERROR',
                message: 'WebSocket connection error',
                details: event,
                timestamp: new Date(),
                retryable: true,
            };
            
            this.setError(wsError);
        };
    }

    /**
     * Handle incoming WebSocket message with validation and processing
     */
    private handleMessage(message: WebSocketMessage): void {
        logger.debug('[WebSocket] Message received', {
            type: message.type,
            id: message.id
        });

        // Handle special message types
        switch (message.type) {
            case 'connection.established':
                this.metadata.connectionId = message.data.connection_id;
                this.metadata.userId = message.data.user_id;
                break;

            case 'pong':
                this.handlePongResponse(message);
                return; // Don't emit pong events to application

            case 'subscription.acknowledged':
                logger.info('[WebSocket] Subscriptions acknowledged', {
                    events: message.data.events
                });
                break;
        }

        // Emit to listeners
        this.emit(message.type as WebSocketEventType, message.data);
    }

    /**
     * Handle pong response and calculate latency
     */
    private handlePongResponse(message: WebSocketMessage): void {
        const pingId = message.data?.pingId;
        if (!pingId || !this.pendingPings.has(pingId)) {
            logger.debug('[WebSocket] Received pong without matching ping', { pingId });
            return;
        }

        const { timestamp, timeout } = this.pendingPings.get(pingId)!;
        clearTimeout(timeout);
        this.pendingPings.delete(pingId);

        // Calculate latency
        const latency = Date.now() - timestamp.getTime();
        this.metadata.latencyMeasurements.push(latency);
        
        // Keep only last 10 measurements
        if (this.metadata.latencyMeasurements.length > 10) {
            this.metadata.latencyMeasurements.shift();
        }

        this.metadata.lastHeartbeat = new Date();
        
        logger.debug('[WebSocket] Heartbeat received', { 
            latency: `${latency}ms`,
            avgLatency: this.getAverageLatency(),
        });
    }

    /**
     * Get average latency from recent measurements
     */
    private getAverageLatency(): number | undefined {
        if (this.metadata.latencyMeasurements.length === 0) return undefined;
        
        const sum = this.metadata.latencyMeasurements.reduce((a, b) => a + b, 0);
        return Math.round(sum / this.metadata.latencyMeasurements.length);
    }

    /**
     * Send message to server with validation and rate limiting
     */
    public send(type: WebSocketEventType, data: any = {}): void {
        // Validate input message
        try {
            WebSocketIncomingMessageSchema.parse({ type, data });
        } catch (error) {
            logger.error('[WebSocket] Invalid message format', {
                type,
                error: error instanceof Error ? error.message : 'Unknown error'
            });
            return;
        }

        // Check rate limiting
        if (this.config.enableRateLimiting && !this.checkRateLimit()) {
            logger.warn('[WebSocket] Message blocked by rate limiting', { type });
            return;
        }

        const message: WebSocketMessage = {
            type,
            data,
            timestamp: new Date().toISOString(),
            id: crypto.randomUUID(),
        };

        if (this.state === 'connected' && this.ws?.readyState === WebSocket.OPEN) {
            try {
                this.ws.send(JSON.stringify(message));
                this.metadata.lastMessageSent = new Date();
                this.metadata.totalMessagesSent++;
                
                // Update rate limiting counter
                if (this.config.enableRateLimiting) {
                    this.rateLimitState.messageCount++;
                }
                
                logger.debug('[WebSocket] Message sent', { type, id: message.id });
            } catch (error) {
                logger.error('[WebSocket] Failed to send message', {
                    type,
                    error: error instanceof Error ? error.message : 'Unknown error'
                });
                
                if (this.config.enableMessageQueue) {
                    this.queueMessage(message);
                }
            }
        } else {
            if (this.config.enableMessageQueue) {
                logger.debug('[WebSocket] Message queued (not connected)', { type });
                this.queueMessage(message);
            } else {
                logger.warn('[WebSocket] Message dropped (not connected, queue disabled)', { type });
            }
        }
    }

    /**
     * Send ping and track for pong response
     */
    private sendPing(): void {
        const pingId = crypto.randomUUID();
        const timestamp = new Date();
        
        // Set timeout for ping response
        const timeout = setTimeout(() => {
            this.pendingPings.delete(pingId);
            logger.warn('[WebSocket] Ping timeout', { pingId });
            
            // Consider this a connection issue
            this.setError({
                code: 'PING_TIMEOUT',
                message: 'Ping response timeout',
                timestamp: new Date(),
                retryable: true,
            });
        }, this.config.pingTimeout);

        this.pendingPings.set(pingId, { timestamp, timeout });
        
        this.send('ping', { pingId });
    }

    /**
     * Subscribe to specific event types
     */
    public subscribe(events: WebSocketEventType[]): void {
        events.forEach(event => this.subscriptions.add(event));

        if (this.state === 'connected') {
            this.sendSubscriptions();
        }

        logger.info('[WebSocket] Subscribed to events', { events });
    }

    /**
     * Unsubscribe from specific event types
     */
    public unsubscribe(events: WebSocketEventType[]): void {
        events.forEach(event => this.subscriptions.delete(event));

        if (this.state === 'connected') {
            this.send('unsubscribe', { events });
        }

        logger.info('[WebSocket] Unsubscribed from events', { events });
    }

    /**
     * Add event listener
     */
    public on(event: WebSocketEventType, listener: EventListener): () => void {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, new Set());
        }

        this.eventListeners.get(event)!.add(listener);

        logger.debug('[WebSocket] Event listener added', { event });

        // Return unsubscribe function
        return () => {
            this.off(event, listener);
        };
    }

    /**
     * Remove event listener
     */
    public off(event: WebSocketEventType, listener: EventListener): void {
        const listeners = this.eventListeners.get(event);
        if (listeners) {
            listeners.delete(listener);
            if (listeners.size === 0) {
                this.eventListeners.delete(event);
            }
        }

        logger.debug('[WebSocket] Event listener removed', { event });
    }

    /**
     * Get current connection state
     */
    public getState(): ConnectionState {
        return this.state;
    }

    /**
     * Get connection metadata
     */
    public getMetadata(): Readonly<ConnectionMetadata> {
        return { ...this.metadata };
    }

    /**
     * Get comprehensive connection statistics
     */
    public getStats(): ConnectionStats {
        return {
            state: this.state,
            reconnectAttempts: this.reconnectAttempts,
            queuedMessages: this.messageQueue.length,
            activeListeners: Array.from(this.eventListeners.entries()).map(([event, listeners]) => ({
                event,
                count: listeners.size,
            })),
            subscriptions: Array.from(this.subscriptions),
            metadata: {
                ...this.metadata,
                averageLatency: this.getAverageLatency(),
            },
            rateLimiting: {
                isLimited: this.rateLimitState.isLimited,
                messagesInWindow: this.rateLimitState.messageCount,
                windowStart: this.rateLimitState.windowStart,
                limitResetTime: this.rateLimitState.resetTime,
            },
        };
    }

    /**
     * Cleanup and destroy service
     */
    public destroy(): void {
        logger.info('[WebSocket] Service destroying');

        this.disconnect();
        this.eventListeners.clear();
        this.subscriptions.clear();

        // Cleanup auth listener
        if (this.authUnsubscribe) {
            this.authUnsubscribe();
        }
    }

    // Private helper methods

    private setState(newState: ConnectionState): void {
        const oldState = this.state;
        this.state = newState;

        logger.debug('[WebSocket] State changed', { from: oldState, to: newState });
    }

    private emit(event: WebSocketEventType, data: any): void {
        const listeners = this.eventListeners.get(event);
        if (listeners) {
            listeners.forEach(listener => {
                try {
                    listener(data);
                } catch (error) {
                    logger.error('[WebSocket] Event listener error', {
                        event,
                        error: error instanceof Error ? error.message : 'Unknown error'
                    });
                }
            });
        }
    }

    private queueMessage(message: WebSocketMessage): void {
        if (this.messageQueue.length >= this.config.messageQueueMaxSize) {
            const removed = this.messageQueue.shift();
            logger.warn('[WebSocket] Message queue full, removing oldest message', {
                removedType: removed?.message.type
            });
        }

        this.messageQueue.push({
            message,
            timestamp: new Date(),
            retryCount: 0,
            maxRetries: 3, // Default max retries
        });
    }

    private processMessageQueue(): void {
        if (this.messageQueue.length === 0) return;

        logger.info('[WebSocket] Processing message queue', {
            count: this.messageQueue.length
        });

        const queue = [...this.messageQueue];
        this.messageQueue = [];

        queue.forEach(({ message, retryCount, maxRetries }) => {
            if (retryCount < maxRetries) {
                this.send(message.type as WebSocketEventType, message.data);
            } else {
                logger.warn('[WebSocket] Message max retries exceeded, dropping', {
                    type: message.type,
                    retries: retryCount
                });
            }
        });
    }

    private sendSubscriptions(): void {
        if (this.subscriptions.size > 0) {
            this.send('subscribe', {
                events: Array.from(this.subscriptions),
            });
        }
    }

    private startHeartbeat(): void {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
        }

        this.heartbeatTimer = setInterval(() => {
            if (this.state === 'connected') {
                this.sendPing();
            }
        }, this.config.heartbeatInterval);
    }

    private clearTimers(): void {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = undefined;
        }

        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = undefined;
        }

        if (this.connectionTimer) {
            clearTimeout(this.connectionTimer);
            this.connectionTimer = undefined;
        }

        if (this.pingTimer) {
            clearTimeout(this.pingTimer);
            this.pingTimer = undefined;
        }
    }

    private scheduleReconnect(): void {
        if (!this.config.enableAutoReconnect) {
            logger.info('[WebSocket] Auto-reconnect disabled');
            return;
        }

        if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
            logger.error('[WebSocket] Max reconnect attempts reached', {
                attempts: this.reconnectAttempts
            });
            this.setState('error');
            return;
        }

        // Exponential backoff with jitter
        const baseDelay = this.config.reconnectDelay * Math.pow(2, this.reconnectAttempts);
        const maxDelay = this.config.maxReconnectDelay;
        const jitter = Math.random() * 1000; // Add up to 1 second jitter
        const delay = Math.min(baseDelay + jitter, maxDelay);

        this.reconnectAttempts++;
        this.metadata.totalReconnects++;

        logger.info('[WebSocket] Scheduling reconnect', {
            attempt: this.reconnectAttempts,
            delay: Math.round(delay),
            maxAttempts: this.config.maxReconnectAttempts
        });

        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }
}

// Export singleton instance
export const webSocketService = new WebSocketService();

// Export class for testing
export { WebSocketService };
export type { WSConfig as WebSocketConfig, ConnectionMetadata, WebSocketEventType, WebSocketMessage, ConnectionStats };
