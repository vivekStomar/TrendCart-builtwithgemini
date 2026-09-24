package com.retail.proxy.controller;

import com.retail.proxy.dto.ChatRequest;
import com.retail.proxy.dto.ChatResponse;
import com.retail.proxy.service.AgentProxyService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/v1")
@CrossOrigin(origins = "*", allowedHeaders = "*")
public class AgentProxyController {

    private final AgentProxyService agentProxyService;

    public AgentProxyController(AgentProxyService agentProxyService) {
        this.agentProxyService = agentProxyService;
    }

    /**
     * Health check endpoint to verify Spring Boot Proxy status
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "Spring Boot ADK Agent Proxy",
                "timestamp", java.time.Instant.now().toString()
        ));
    }

    /**
     * Main chat endpoint for frontend clients (Browser, Mobile App, etc.)
     */
    @PostMapping("/chat")
    public ResponseEntity<ChatResponse> chat(@RequestBody ChatRequest request) {
        if (request.getMessage() == null || request.getMessage().isBlank()) {
            return ResponseEntity.badRequest().body(new ChatResponse(request.getSessionId(), "Message cannot be empty.", "BAD_REQUEST"));
        }
        ChatResponse response = agentProxyService.processChat(request);
        return ResponseEntity.ok(response);
    }
}
