import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Sparkles, User, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useDocumentQuery } from '@/hooks/useDocumentQuery';
import { DocumentInfo } from '@/types/document';
import { cn } from '@/lib/utils';

interface QueryInterfaceProps {
  documentInfo: DocumentInfo | null;
}

const QueryInterface = ({ documentInfo }: QueryInterfaceProps) => {
  const [inputValue, setInputValue] = useState(''); // Single source of truth for input field
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  
  const { messages, isQuerying, queryDocument, getSuggestions } = useDocumentQuery(
    documentInfo?.filename || null
  );

  const suggestions = getSuggestions();

  // Only auto-scroll if user is at the bottom
  useEffect(() => {
    if (autoScroll) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, autoScroll]);

  // Detect if user scrolls up
  useEffect(() => {
    const chatDiv = chatContainerRef.current;
    if (!chatDiv) return;
    const handleScroll = () => {
      const atBottom = chatDiv.scrollHeight - chatDiv.scrollTop - chatDiv.clientHeight < 10;
      setAutoScroll(atBottom);
    };
    chatDiv.addEventListener('scroll', handleScroll);
    return () => chatDiv.removeEventListener('scroll', handleScroll);
  }, []);

  // Helper to scroll only if autoScroll is true is already handled by the effect below.
  // Removed unconditional scroll to allow the user to scroll during typing.

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const queryText = inputValue.trim();
    if (!queryText || isQuerying || !documentInfo) return;

    // Clear the input immediately to prevent any interference
    setInputValue('');
    
    // Process the query
    await queryDocument(queryText);
  };

  const handleSuggestionClick = (suggestion: string) => {
    if (isQuerying || !documentInfo) return;
    setInputValue(suggestion);
    inputRef.current?.focus();
  };

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  // Helper to get summary for deduplication
  const summary = documentInfo?.summary?.trim();

  if (!documentInfo) {
    return (
      <div className="w-full max-w-4xl mx-auto">
        <div className="glass-card p-8 text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-muted/30 rounded-3xl flex items-center justify-center">
            <MessageSquare className="w-8 h-8 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2 text-muted-foreground">
            Query Interface
          </h3>
          <p className="text-muted-foreground">
            Upload and process a document to start asking questions
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-4xl mx-auto animate-slide-up">
      <div className="glass-card p-6 rounded-none">
        {/* Header */}
        <div className="flex items-center gap-3 mb-6">
          <div className="w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center">
            <MessageSquare className="w-6 h-6 text-primary" />
          </div>
          <div>
            <h2 className="text-2xl font-bold">Query Your Document</h2>
            <p className="text-muted-foreground">
              Ask questions about "{documentInfo.filename}"
            </p>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="mb-6">
          {messages.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-primary/5 rounded-3xl flex items-center justify-center">
                <Sparkles className="w-8 h-8 text-primary" />
              </div>
              <p className="text-muted-foreground mb-4">
                No messages yet. Ask your first question!
              </p>
              
              {/* Suggestion Pills */}
              <div className="flex flex-wrap gap-2 justify-center">
                {suggestions.slice(0, 3).map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="outline"
                    size="sm"
                    onClick={() => handleSuggestionClick(suggestion)}
                    className="glass-card border-primary/20 hover:border-primary/40 hover:bg-primary/5"
                    disabled={isQuerying}
                  >
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>
          ) : (
            <div
              ref={chatContainerRef}
              className="space-y-4 overflow-y-auto pr-2 custom-scrollbar bg-card/50 rounded-xl p-4 border border-border"
            >
              {messages.map((message) => {
                // Skip displaying AI message if it matches the summary
                if (
                  message.type === 'ai' &&
                  summary &&
                  message.content.trim() === summary
                ) {
                  return null;
                }
                return (
                  <div
                    key={message.id}
                    className={cn(
                      "flex gap-3 animate-fade-in items-end",
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    )}
                  >
                    {message.type === 'ai' && (
                      <div className="w-8 h-8 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                        <Bot className="w-4 h-4 text-primary" />
                      </div>
                    )}
                    <div
                      className={cn(
                        "max-w-[80%] p-4 rounded-2xl shadow-md",
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground ml-auto border-2 border-primary'
                          : 'bg-card text-card-foreground border border-border'
                      )}
                    >
                      <div className="text-sm whitespace-pre-line">
                        {message.content || (message.isTyping && (
                          <div className="flex items-center gap-1">
                            <span>Thinking</span>
                            <div className="flex gap-1">
                              <div className="w-1 h-1 bg-current rounded-full animate-pulse"></div>
                              <div className="w-1 h-1 bg-current rounded-full animate-pulse animation-delay-200"></div>
                              <div className="w-1 h-1 bg-current rounded-full animate-pulse animation-delay-400"></div>
                            </div>
                          </div>
                        ))}
                      </div>
                      <div className="text-xs opacity-70 mt-2 text-right">
                        {formatTime(message.timestamp)}
                      </div>
                    </div>
                    {message.type === 'user' && (
                      <div className="w-8 h-8 bg-primary/10 rounded-xl flex items-center justify-center flex-shrink-0">
                        <User className="w-4 h-4 text-primary" />
                      </div>
                    )}
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="flex gap-3">
          <Input
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Ask a question about your document..."
            className="flex-1 glass-card border-primary/20 focus:border-primary/40 bg-card text-card-foreground"
            disabled={isQuerying}
          />
          <Button
            type="submit"
            disabled={!inputValue.trim() || isQuerying}
            className="btn-primary"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>

        {/* Suggestions */}
        {messages.length === 0 && (
          <div className="mt-4">
            <p className="text-sm text-muted-foreground mb-2">Suggested questions:</p>
            <div className="flex flex-wrap gap-2">
              {suggestions.map((suggestion, index) => (
                <Button
                  key={index}
                  variant="outline"
                  size="sm"
                  onClick={() => handleSuggestionClick(suggestion)}
                  className="text-xs glass-card border-primary/20 hover:border-primary/40 hover:bg-primary/5"
                  disabled={isQuerying}
                >
                  {suggestion}
                </Button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryInterface;