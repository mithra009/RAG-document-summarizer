import { useState } from 'react';
import { QueryMessage, ApiError } from '@/types/document';
import { toast } from '@/hooks/use-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:7860';

export const useDocumentQuery = (filename: string | null) => {
  const [messages, setMessages] = useState<QueryMessage[]>([]);
  const [isQuerying, setIsQuerying] = useState(false);

  const addMessage = (content: string, type: 'user' | 'ai', isTyping = false): string => {
    // Generate a more robust unique ID (timestamp + random suffix)
    const id = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const message: QueryMessage = {
      id,
      type,
      content,
      timestamp: new Date().toISOString(),
      isTyping
    };
    
    setMessages(prev => [...prev, message]);
    return id;
  };

  const updateMessage = (id: string, updates: Partial<QueryMessage>) => {
    setMessages(prev => prev.map(msg => 
      msg.id === id ? { ...msg, ...updates } : msg
    ));
  };

  const queryDocument = async (query: string): Promise<void> => {
    if (!filename) {
      toast({
        title: "No Document",
        description: "Please upload a document first before querying.",
        variant: "destructive"
      });
      return;
    }

    setIsQuerying(true);
    
    // Add user message
    addMessage(query, 'user');
    
    // Add AI typing indicator
    const aiMessageId = addMessage('', 'ai', true);

    try {
      const formData = new FormData();
      formData.append('filename', filename);
      formData.append('query', query);

      const response = await fetch(`${API_BASE_URL}/query`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Query failed: ${response.statusText}`);
      }

      const result = await response.json();
      const answer = result.answer || result.response || 'I apologize, but I couldn\'t generate a response to your query.';

      // Directly display the full answer to avoid excessive re-renders that block scrolling
      updateMessage(aiMessageId, {
        content: answer,
        isTyping: false,
      });

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Query failed';
      
      updateMessage(aiMessageId, {
        content: `I apologize, but I encountered an error: ${errorMessage}`,
        isTyping: false
      });

      toast({
        title: "Query Failed",
        description: errorMessage,
        variant: "destructive"
      });
    } finally {
      setIsQuerying(false);
    }
  };

  const clearMessages = () => {
    setMessages([]);
  };

  const getSuggestions = (): string[] => {
    return [
      "What are the key points?",
      "Explain the main concepts",
      "What conclusions are drawn?",
      "Summarize the document",
      "What are the important details?",
      "What questions does this raise?"
    ];
  };

  return {
    messages,
    isQuerying,
    queryDocument,
    clearMessages,
    getSuggestions
  };
};