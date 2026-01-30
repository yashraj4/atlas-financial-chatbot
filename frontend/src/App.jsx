import { AnimatePresence, motion } from 'framer-motion';
import { Activity, Bot, Send, Shield, Sparkles, User } from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { sendMessage } from './api';
import './App.css';

// --- Components ---

const AICore = ({ active }) => (
  <div className={`ai-core ${active ? 'active' : ''}`}>
    <div className="orb-ring ring-1"></div>
    <div className="orb-ring ring-2"></div>
    <div className="orb-ring ring-3"></div>
    <div className="orb-center"></div>
  </div>
);

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MarkdownMessage = ({ content }) => (
  <div className="markdown-body">
    <ReactMarkdown remarkPlugins={[remarkGfm]}>
      {content}
    </ReactMarkdown>
  </div>
);

function App() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content: "Atlas System Online. How may I assist your financial operations today?",
      type: 'text'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { id: Date.now(), role: 'user', content: input, type: 'text' };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendMessage(userMessage.content);
      const botResponse = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.final_response || response.output || "Processed.",
        type: 'text'
      };
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      setMessages(prev => [...prev, {
        id: Date.now() + 1,
        role: 'assistant',
        content: "Connection to Neural Net lost.",
        type: 'error'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  // Stagger variants
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.3
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    show: { y: 0, opacity: 1 }
  };

  return (
    <>
      <div className="living-bg"></div>

      <motion.div
        className="app-layout"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        {/* Sidebar / Navigation */}
        <motion.nav className="glass-panel sidebar" variants={itemVariants}>
          <div className="logo-container">
            <div className="logo-glow">
              <Sparkles size={24} color="var(--neon-cyan)" />
            </div>
          </div>

          <div className="nav-actions">
            <button
              className={`nav-btn active`}
            >
              <Activity size={20} />
            </button>
          </div>

          <div className="nav-footer">
            <Shield size={20} color="var(--text-secondary)" />
          </div>
        </motion.nav>

        {/* Main Content */}
        <motion.main className="glass-panel main-content" variants={itemVariants}>

          {/* Header */}
          <header className="main-header">
            <div className="header-title">
              <h1>ATLAS</h1>
              <span className="status-dot"></span>
              <span className="status-text">SYSTEM ONLINE</span>
            </div>

            <AICore active={isLoading} />
          </header>

          {/* Chat Container */}
          <div className="chat-viewport">
            <div className="messages-list">
              <AnimatePresence>
                {messages.map((msg) => (
                  <motion.div
                    key={msg.id}
                    className={`msg-row ${msg.role}`}
                    initial={{ opacity: 0, x: msg.role === 'user' ? 20 : -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {msg.role === 'assistant' && (
                      <div className="avatar bot"><Bot size={18} /></div>
                    )}

                    <div className="msg-bubble glass-card">
                      {msg.role === 'assistant' ? (
                        <MarkdownMessage content={msg.content} />
                      ) : (
                        <p>{msg.content}</p>
                      )}
                      {msg.type === 'error' && <span className="error-text">! NETWORK ERROR</span>}
                    </div>

                    {msg.role === 'user' && (
                      <div className="avatar user"><User size={18} /></div>
                    )}
                  </motion.div>
                ))}
                {isLoading && (
                  <motion.div
                    className="msg-row assistant"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                  >
                    <div className="avatar bot"><Bot size={18} /></div>
                    <div className="msg-bubble glass-card loading">
                      <span className="blink">_ PROCESSING DATA STREAM</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              <div ref={messagesEndRef} />
            </div>
          </div>

          {/* Input Area */}
          <footer className="input-zone">
            <form onSubmit={handleSend} className="glass-input-wrapper">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Command Atlas..."
                disabled={isLoading}
              />
              <button type="submit" disabled={isLoading || !input.trim()}>
                <Send size={18} />
              </button>
            </form>
          </footer>

        </motion.main>
      </motion.div>
    </>
  );
}

export default App;
