package com.retail.proxy.dto;

public class ChatRequest {
    private String userId;
    private String sessionId;
    private String message;

    public ChatRequest() {}

    public ChatRequest(String userId, String sessionId, String message) {
        this.userId = userId;
        this.sessionId = sessionId;
        this.message = message;
    }

    public String getUserId() {
        return userId;
    }

    public void setUserId(String userId) {
        this.userId = userId;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
}
