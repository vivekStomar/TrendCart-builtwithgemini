import React, { useState, useEffect, useRef } from 'react';
import { 
  Bot, 
  User, 
  Send, 
  RotateCcw, 
  ShoppingBag, 
  MapPin, 
  Search, 
  CloudSun, 
  CheckCircle2, 
  XCircle,
  Zap
} from 'lucide-react';
import './App.css';

const SPRINGBOOT_PROXY_URL = 'http://127.0.0.1:8081/api/v1';

export default function App() {
  const [messages, setMessages] = useState([
    {
      id: 'welcome-1',
      sender: 'assistant',
      text: "👋 Hello! I am your NovaSmart AI Retail Shopping Assistant.\n\nI can help you search our product catalog, check real-time stock levels, find nearby stores, convert currencies, add items to your cart, or tell you the weather. How can I assist you today?"
    }
  ]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [serverHealth, setServerHealth] = useState({ online: false, checking: true });
  const messagesEndRef = useRef(null);

  // Check Spring Boot Proxy Health on mount
  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 15000);
    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const checkHealth = async () => {
    try {
      const res = await fetch(`${SPRINGBOOT_PROXY_URL}/health`);
      if (res.ok) {
        const data = await res.json();
        if (data.status === 'UP') {
          setServerHealth({ online: true, checking: false });
          return;
        }
      }
      setServerHealth({ online: false, checking: false });
    } catch {
      setServerHealth({ online: false, checking: false });
    }
  };

  const sendMessage = async (textToSend) => {
    const text = textToSend || input;
    if (!text.trim() || loading) return;

    const userMsgId = Date.now().toString();
    const newMessages = [...messages, { id: userMsgId, sender: 'user', text }];
    setMessages(newMessages);
    if (!textToSend) setInput('');
    setLoading(true);

    try {
      const response = await fetch(`${SPRINGBOOT_PROXY_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: 'react-user',
          sessionId: sessionId,
          message: text
        })
      });

      if (!response.ok) {
        throw new Error(`Proxy error: ${response.status}`);
      }

      const data = await response.json();
      if (data.sessionId && !sessionId) {
        setSessionId(data.sessionId);
      }

      const botReply = data.reply || "No response received from agent.";
      setMessages(prev => [
        ...prev,
        { id: (Date.now() + 1).toString(), sender: 'assistant', text: botReply }
      ]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        { 
          id: (Date.now() + 1).toString(), 
          sender: 'assistant', 
          text: `⚠️ Communication Error: Unable to reach Spring Boot Proxy API (http://127.0.0.1:8081/api/v1/chat).\n\nDetails: ${err.message}` 
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const resetChat = () => {
    setSessionId(null);
    setMessages([
      {
        id: Date.now().toString(),
        sender: 'assistant',
        text: "✨ Chat session reset! How can I help you with your retail shopping today?"
      }
    ]);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="app-container">
      {/* App Header */}
      <header className="app-header">
        <div className="brand">
          <div className="logo-badge">
            <ShoppingBag size={22} />
          </div>
          <div className="brand-info">
            <h1>NovaSmart Retail AI</h1>
            <p>Powered by Spring Boot Proxy & ADK Agent Platform</p>
          </div>
        </div>

        <div className="status-bar">
          <div className={`status-badge ${serverHealth.online ? 'online' : 'offline'}`}>
            <span className="status-dot"></span>
            <span>{serverHealth.checking ? 'Connecting...' : serverHealth.online ? 'Spring Boot Proxy Online' : 'Proxy Offline'}</span>
          </div>

          <button className="new-chat-btn" onClick={resetChat} title="Reset Chat Session">
            <RotateCcw size={16} />
            <span>New Chat</span>
          </button>
        </div>
      </header>

      {/* Chat Messages Area */}
      <div className="chat-window">
        {messages.map((msg) => (
          <div key={msg.id} className={`message-wrapper ${msg.sender}`}>
            <div className="avatar">
              {msg.sender === 'assistant' ? <Bot size={20} /> : <User size={20} />}
            </div>
            <div className="bubble">
              {msg.text}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-wrapper assistant">
            <div className="avatar">
              <Bot size={20} />
            </div>
            <div className="bubble">
              <div className="typing-dots">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Suggestion Chips */}
      <div className="quick-chips">
        <button className="chip-btn" onClick={() => sendMessage('Show me running shoes')}>
          <Search size={14} /> Performance Running Shoes
        </button>
        <button className="chip-btn" onClick={() => sendMessage('Search for blue tshirt')}>
          <Search size={14} /> Blue T-Shirt
        </button>
        <button className="chip-btn" onClick={() => sendMessage('Find store near zip code 10001')}>
          <MapPin size={14} /> Store near 10001
        </button>
        <button className="chip-btn" onClick={() => sendMessage('What is in my cart?')}>
          <ShoppingBag size={14} /> Shopping Cart
        </button>
        <button className="chip-btn" onClick={() => sendMessage('What is the weather in New York?')}>
          <CloudSun size={14} /> Weather in NY
        </button>
      </div>

      {/* Input Bar */}
      <div className="input-container">
        <form className="input-form" onSubmit={(e) => { e.preventDefault(); sendMessage(); }}>
          <input
            type="text"
            className="chat-input"
            placeholder="Ask about products, stock, stores, or orders..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={loading}
          />
          <button type="submit" className="send-btn" disabled={loading || !input.trim()}>
            <Send size={18} />
          </button>
        </form>
      </div>
    </div>
  );
}
