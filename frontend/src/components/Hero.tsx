import { FileText, Brain, MessageSquare, Zap } from 'lucide-react';

const Hero = () => {
  return (
    <div className="relative min-h-screen flex items-center justify-center px-4 py-20">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-primary/20 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-accent/20 rounded-full blur-3xl animate-float animation-delay-400"></div>
      </div>

      <div className="max-w-4xl mx-auto text-center relative z-10">
        {/* Main heading */}
        <div className="mb-8">
          <h1 className="text-5xl md:text-7xl font-bold mb-6">
            <span className="gradient-text">AI Document</span>
            <br />
            <span className="text-foreground">Summarizer</span>
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
            Upload any document and get instant AI-powered summaries and intelligent answers to your questions
          </p>
        </div>

        {/* Feature cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-12">
          <div className="glass-card p-6 group hover:scale-105 transition-all duration-300">
            <div className="w-12 h-12 mx-auto mb-4 bg-primary/10 rounded-2xl flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <FileText className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Upload Documents</h3>
            <p className="text-sm text-muted-foreground">
              Support for PDF, DOCX, PPTX, and TXT files up to 100MB
            </p>
          </div>

          <div className="glass-card p-6 group hover:scale-105 transition-all duration-300">
            <div className="w-12 h-12 mx-auto mb-4 bg-primary/10 rounded-2xl flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">AI Analysis</h3>
            <p className="text-sm text-muted-foreground">
              Get instant summaries and document classification
            </p>
          </div>

          <div className="glass-card p-6 group hover:scale-105 transition-all duration-300">
            <div className="w-12 h-12 mx-auto mb-4 bg-primary/10 rounded-2xl flex items-center justify-center group-hover:bg-primary/20 transition-colors">
              <MessageSquare className="w-6 h-6 text-primary" />
            </div>
            <h3 className="font-semibold mb-2">Smart Queries</h3>
            <p className="text-sm text-muted-foreground">
              Ask questions and get intelligent answers about your documents
            </p>
          </div>
        </div>

        {/* Call to action */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Zap className="w-4 h-4 text-primary" />
            <span>Fast, secure, and intelligent</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Hero;