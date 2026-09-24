package com.retail.proxy.dto;

import java.util.Map;

public class ChatResponse {
    private String sessionId;
    private String reply;
    private String status;
    private Map<String, Object> metadata;

    public ChatResponse() {}

    public ChatResponse(String sessionId, String reply, String status) {
        this.sessionId = sessionId;
        this.reply = reply;
        this.status = status;
    }

    public ChatResponse(String sessionId, String reply, String status, Map<String, Object> metadata) {
        this.sessionId = sessionId;
        this.reply = reply;
        this.status = status;
        this.metadata = metadata;
    }

    public String getSessionId() {
        return sessionId;
    }

    public void setSessionId(String sessionId) {
        this.sessionId = sessionId;
    }

    public String getReply() {
        return reply;
    }

    public void setReply(String reply) {
        this.reply = reply;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public Map<String, Object> getMetadata() {
        return metadata;
    }

    public void setMetadata(Map<String, Object> metadata) {
        this.metadata = metadata;
    }
}
