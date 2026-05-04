/** @odoo-module **/

import { Component, useState, useRef, onMounted, markup } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { escape } from "@web/core/utils/strings";

/**
 * AI Chat Widget - Floating Button Component
 * Renders as a fixed floating button in the bottom-right corner
 */
export class AiChatWidget extends Component {
    static template = "c21_ai_assistant.AiChatSystray";

    setup() {
        this.aiChat = useService("aiChat");
        this.state = useState({
            isOpen: false,
            isLoading: false,
            messages: [],
            inputValue: "",
            hasAccess: true,
            welcomeMessage: "",
            sessionId: null,
        });
        this.messagesRef = useRef("messagesContainer");

        onMounted(async () => {
            await this.loadConfig();
        });
    }

    async loadConfig() {
        try {
            const config = await this.aiChat.getConfig();
            this.state.hasAccess = config.has_access;
            this.state.welcomeMessage = config.welcome_message;
        } catch (error) {
            console.error("[AI Assistant] Failed to load config:", error);
        }
    }

    toggleChat() {
        this.state.isOpen = !this.state.isOpen;

        if (this.state.isOpen && this.state.messages.length === 0) {
            this.startNewSession();
        }
    }

    async startNewSession() {
        this.state.isLoading = true;
        try {
            const result = await this.aiChat.newSession();
            if (result.success) {
                this.state.sessionId = result.session_id;
                this.state.messages = [];

                // Add welcome message
                if (result.welcome_message) {
                    this.state.messages.push({
                        role: "assistant",
                        content: result.welcome_message,
                        timestamp: new Date().toISOString(),
                    });
                }
            }
        } catch (error) {
            console.error("[AI Assistant] Failed to start session:", error);
        } finally {
            this.state.isLoading = false;
        }
    }

    async sendMessage() {
        const message = this.state.inputValue.trim();
        if (!message || this.state.isLoading) return;

        // Add user message to UI
        this.state.messages.push({
            role: "user",
            content: message,
            timestamp: new Date().toISOString(),
        });
        this.state.inputValue = "";
        this.state.isLoading = true;

        // Scroll to bottom
        this.scrollToBottom();

        try {
            const result = await this.aiChat.sendMessage(message, this.state.sessionId);

            if (result.success) {
                this.state.sessionId = result.session_id;
                this.state.messages.push({
                    role: "assistant",
                    content: result.response,
                    timestamp: new Date().toISOString(),
                    intent: result.intent,
                    searchResults: result.search_results,
                    sources: result.sources,
                });
            } else {
                this.state.messages.push({
                    role: "assistant",
                    content: result.response || "Sorry, an error occurred. Please try again.",
                    timestamp: new Date().toISOString(),
                    isError: true,
                });
            }
        } catch (error) {
            this.state.messages.push({
                role: "assistant",
                content: "Sorry, could not connect to the AI service. Please try again later.",
                timestamp: new Date().toISOString(),
                isError: true,
            });
        } finally {
            this.state.isLoading = false;
            this.scrollToBottom();
        }
    }

    onKeyDown(ev) {
        if (ev.key === "Enter" && !ev.shiftKey) {
            ev.preventDefault();
            this.sendMessage();
        }
    }

    onInputChange(ev) {
        this.state.inputValue = ev.target.value;
    }

    scrollToBottom() {
        setTimeout(() => {
            const container = this.messagesRef.el;
            if (container) {
                container.scrollTop = container.scrollHeight;
            }
        }, 50);
    }

    closeChat() {
        this.state.isOpen = false;
    }

    clearChat() {
        this.startNewSession();
    }

    formatMessage(content) {
        if (!content) return "";

        // Escape HTML to prevent XSS
        let formatted = escape(content);

        // Bold: **text**
        formatted = formatted.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");

        // Line breaks
        formatted = formatted.replace(/\n/g, "<br>");

        // Return as markup to render HTML
        return markup(formatted);
    }

    formatTime(timestamp) {
        if (!timestamp) return "";
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
        });
    }

    get hasSearchResults() {
        return (msg) => msg.searchResults && msg.searchResults.length > 0;
    }
}

AiChatWidget.props = {};

// Register as a main component (renders independently, not in systray)
registry.category("main_components").add("AiChatWidget", {
    Component: AiChatWidget,
});
