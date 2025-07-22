import { useState, useEffect, useRef } from 'react';
import { FileText, Layers, Hash, Brain, ChevronDown, ChevronUp } from 'lucide-react';
import { DocumentInfo } from '@/types/document';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface DocumentAnalysisProps {
  documentInfo: DocumentInfo;
}

const DocumentAnalysis = ({ documentInfo }: DocumentAnalysisProps) => {
  console.log('DocumentAnalysis summary:', documentInfo.summary);
  const [isExpanded, setIsExpanded] = useState(true);
  const [displayedSummary, setDisplayedSummary] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const summaryRef = useRef<HTMLDivElement>(null);
  const [displayedWords, setDisplayedWords] = useState<string[]>([]);

  // Typing animation for summary (word-by-word, with auto-scroll)
  useEffect(() => {
    if (!documentInfo.summary) return;

    const words = documentInfo.summary.split(' ');
    let currentIndex = 0;
    setDisplayedWords([]);
    setIsTyping(true);

    // Scroll to summary section when summary generation starts
    setTimeout(() => {
      summaryRef.current?.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 100);

    const typingInterval = setInterval(() => {
      if (currentIndex < words.length) {
        setDisplayedWords((prev) => [...prev, words[currentIndex]]);
        currentIndex++;
      } else {
        setIsTyping(false);
        clearInterval(typingInterval);
      }
    }, 120);

    return () => clearInterval(typingInterval);
  }, [documentInfo.summary]);

  const getFileTypeDisplay = (type: string) => {
    switch (type) {
      case 'application/pdf':
        return 'PDF Document';
      case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
        return 'Word Document';
      case 'application/vnd.openxmlformats-officedocument.presentationml.presentation':
        return 'PowerPoint Presentation';
      case 'text/plain':
        return 'Text File';
      default:
        return 'Document';
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  if (!documentInfo) return null;

  return (
    <div className="w-full max-w-4xl mx-auto animate-slide-up">
      <div className="glass-card p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-primary/10 rounded-2xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Document Analysis</h2>
              <p className="text-muted-foreground">AI-powered insights and summary</p>
            </div>
          </div>
          
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsExpanded(!isExpanded)}
            className="hover:bg-primary/10"
          >
            {isExpanded ? <ChevronUp /> : <ChevronDown />}
          </Button>
        </div>

        {/* Document Stats */}
        <div className="grid md:grid-cols-4 gap-4 mb-6">
          <div className="bg-primary/5 rounded-xl p-4 text-center">
            <FileText className="w-6 h-6 text-primary mx-auto mb-2" />
            <div className="text-sm text-muted-foreground">Document Type</div>
            <div className="font-semibold">{getFileTypeDisplay(documentInfo.type)}</div>
          </div>
          
          <div className="bg-primary/5 rounded-xl p-4 text-center">
            <Layers className="w-6 h-6 text-primary mx-auto mb-2" />
            <div className="text-sm text-muted-foreground">Pages</div>
            <div className="font-semibold">{documentInfo.pageCount}</div>
          </div>
          
          <div className="bg-primary/5 rounded-xl p-4 text-center">
            <Hash className="w-6 h-6 text-primary mx-auto mb-2" />
            <div className="text-sm text-muted-foreground">Text Chunks</div>
            <div className="font-semibold">{documentInfo.chunkCount}</div>
          </div>
          
          <div className="bg-primary/5 rounded-xl p-4 text-center">
            <Brain className="w-6 h-6 text-primary mx-auto mb-2" />
            <div className="text-sm text-muted-foreground">Classification</div>
            <div className="font-semibold text-sm">{documentInfo.classification}</div>
          </div>
        </div>

        {/* Expandable Content */}
        {isExpanded && (
          <div className="space-y-6 animate-fade-in">
            {/* Document Info */}
            <div className="bg-muted/30 rounded-xl p-4">
              <h3 className="font-semibold mb-2">Document Details</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="text-muted-foreground">Filename:</span>
                  <span className="ml-2 font-medium">{documentInfo.filename}</span>
                </div>
                <div>
                  <span className="text-muted-foreground">Processed:</span>
                  <span className="ml-2 font-medium">{formatDate(documentInfo.uploadedAt)}</span>
                </div>
              </div>
            </div>

            {/* AI Summary */}
            <div ref={summaryRef} className="bg-muted/30 rounded-xl p-6">
              <h3 className="font-semibold mb-4 flex items-center gap-2">
                <Brain className="w-5 h-5 text-primary" />
                AI-Generated Summary
              </h3>
              
              <div className="prose prose-sm max-w-none">
                <p className={"text-foreground leading-relaxed"}>
                  {displayedWords.map((word, idx) => (
                    <span key={idx}>{word} </span>
                  ))}
                  {isTyping && <span className="ml-1">|</span>}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default DocumentAnalysis;