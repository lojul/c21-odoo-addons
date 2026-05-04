/** @odoo-module **/

import { registry } from "@web/core/registry";
import { rpc } from "@web/core/network/rpc";

/**
 * AI Chat Service - handles API communication
 */
export const aiChatService = {
    dependencies: ["notification"],

    start(env, { notification }) {
        let currentSessionId = null;

        return {
            /**
             * Send a chat message
             * @param {string} message - User's message
             * @param {string} sessionId - Optional session ID
             * @returns {Promise<Object>} Response data
             */
            async sendMessage(message, sessionId = null) {
                try {
                    const result = await rpc("/ai_assistant/chat", {
                        message: message,
                        session_id: sessionId || currentSessionId,
                    });

                    if (result.success && result.session_id) {
                        currentSessionId = result.session_id;
                    }

                    return result;
                } catch (error) {
                    console.error("[AI Assistant] Send message error:", error);
                    notification.add("發送訊息時發生錯誤", { type: "danger" });
                    throw error;
                }
            },

            /**
             * Create a new chat session
             * @returns {Promise<Object>} Session data with welcome message
             */
            async newSession() {
                try {
                    const result = await rpc("/ai_assistant/session/new", {});

                    if (result.success) {
                        currentSessionId = result.session_id;
                    }

                    return result;
                } catch (error) {
                    console.error("[AI Assistant] New session error:", error);
                    throw error;
                }
            },

            /**
             * Get chat history for a session
             * @param {string} sessionId
             * @returns {Promise<Object>} Messages array
             */
            async getHistory(sessionId) {
                try {
                    return await rpc("/ai_assistant/session/history", {
                        session_id: sessionId,
                    });
                } catch (error) {
                    console.error("[AI Assistant] Get history error:", error);
                    throw error;
                }
            },

            /**
             * Close the current session
             * @param {string} sessionId
             * @returns {Promise<Object>}
             */
            async closeSession(sessionId = null) {
                try {
                    const result = await rpc("/ai_assistant/session/close", {
                        session_id: sessionId || currentSessionId,
                    });

                    if (result.success) {
                        currentSessionId = null;
                    }

                    return result;
                } catch (error) {
                    console.error("[AI Assistant] Close session error:", error);
                    throw error;
                }
            },

            /**
             * List recent sessions
             * @param {number} limit
             * @returns {Promise<Object>} Sessions array
             */
            async listSessions(limit = 10) {
                try {
                    return await rpc("/ai_assistant/sessions", {
                        limit: limit,
                    });
                } catch (error) {
                    console.error("[AI Assistant] List sessions error:", error);
                    throw error;
                }
            },

            /**
             * Get client configuration
             * @returns {Promise<Object>} Config data
             */
            async getConfig() {
                try {
                    return await rpc("/ai_assistant/config", {});
                } catch (error) {
                    console.error("[AI Assistant] Get config error:", error);
                    throw error;
                }
            },

            /**
             * Get current session ID
             * @returns {string|null}
             */
            getCurrentSessionId() {
                return currentSessionId;
            },

            /**
             * Set current session ID
             * @param {string} sessionId
             */
            setCurrentSessionId(sessionId) {
                currentSessionId = sessionId;
            },
        };
    },
};

registry.category("services").add("aiChat", aiChatService);
