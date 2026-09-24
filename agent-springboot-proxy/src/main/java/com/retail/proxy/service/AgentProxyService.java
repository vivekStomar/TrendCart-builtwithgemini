package com.retail.proxy.service;

import com.retail.proxy.dto.ChatRequest;
import com.retail.proxy.dto.ChatResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.*;

@Service
public class AgentProxyService {

    private static final Logger log = LoggerFactory.getLogger(AgentProxyService.class);

    private final RestClient restClient;

    @Value("${adk.agent.app-name:app}")
    private String appName;

    @Value("${adk.agent.user-id:user}")
    private String userId;

    public AgentProxyService(@Value("${adk.agent.base-url:http://127.0.0.1:8080}") String baseUrl) {
        this.restClient = RestClient.builder()
                .baseUrl(baseUrl)
                .build();
    }

    /**
     * Creates a new session if sessionId is empty, then sends the user message to ADK Agent.
     */
    public ChatResponse processChat(ChatRequest request) {
        String effectiveUserId = (request.getUserId() != null && !request.getUserId().isBlank())
                ? request.getUserId()
                : this.userId;

        String sessionId = request.getSessionId();
        if (sessionId == null || sessionId.isBlank()) {
            sessionId = createSession(effectiveUserId);
            log.info("Created new ADK agent session: {}", sessionId);
        }

        log.info("Proxying message to ADK agent (session: {}): '{}'", sessionId, request.getMessage());

        // Prepare ADK request body
        Map<String, Object> adkPayload = new HashMap<>();
        adkPayload.put("app_name", this.appName);
        adkPayload.put("user_id", effectiveUserId);
        adkPayload.put("session_id", sessionId);

        Map<String, Object> messageMap = new HashMap<>();
        messageMap.put("role", "user");
        messageMap.put("parts", List.of(Map.of("text", request.getMessage())));
        adkPayload.put("message", messageMap);

        try {
            String rawResponse = restClient.post()
                    .uri("/run_sse")
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(adkPayload)
                    .retrieve()
                    .body(String.class);

            String replyText = parseAdkSseResponse(rawResponse);
            return new ChatResponse(sessionId, replyText, "SUCCESS");

        } catch (Exception e) {
            log.error("Failed to communicate with ADK agent: ", e);
            return new ChatResponse(sessionId, "Error contacting AI agent: " + e.getMessage(), "ERROR");
        }
    }

    /**
     * Create a session on the ADK server via POST /apps/{appName}/users/{userId}/sessions
     */
    public String createSession(String uid) {
        try {
            Map<?, ?> response = restClient.post()
                    .uri("/apps/{appName}/users/{userId}/sessions", this.appName, uid)
                    .contentType(MediaType.APPLICATION_JSON)
                    .retrieve()
                    .body(Map.class);

            if (response != null && response.containsKey("id")) {
                return response.get("id").toString();
            }
        } catch (Exception e) {
            log.warn("Could not create session on ADK server, generating fallback UUID: ", e);
        }
        return UUID.randomUUID().toString();
    }

    /**
     * Parses SSE events returned by ADK /run_sse and extracts final text / A2UI parts.
     */
    private String parseAdkSseResponse(String rawSse) {
        if (rawSse == null || rawSse.isBlank()) {
            return "No response received from agent.";
        }

        StringBuilder fullText = new StringBuilder();
        String[] lines = rawSse.split("\n");

        for (String line : lines) {
            if (line.startsWith("data: ")) {
                String jsonData = line.substring(6).trim();
                if (jsonData.equals("[DONE]")) {
                    continue;
                }
                // Try to extract text content from SSE payload line
                if (jsonData.contains("\"text\"")) {
                    int idx = jsonData.indexOf("\"text\":");
                    if (idx != -1) {
                        int start = jsonData.indexOf("\"", idx + 7) + 1;
                        int end = jsonData.indexOf("\"", start);
                        if (start > 0 && end > start) {
                            String extracted = jsonData.substring(start, end)
                                    .replace("\\n", "\n")
                                    .replace("\\\"", "\"");
                            fullText.append(extracted);
                        }
                    }
                }
            }
        }

        String result = fullText.toString().trim();
        return result.isEmpty() ? rawSse : result;
    }
}
