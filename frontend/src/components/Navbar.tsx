import { Brain, FileText, RotateCcw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface NavbarProps {
  onReset: () => void;
  hasDocument: boolean;
}

const Navbar = ({ onReset, hasDocument }: NavbarProps) => {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-white/20" style={{ borderRadius: 0 }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary/10 rounded-2xl flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary" />
            </div>
            <div className="hidden sm:block">
              <h1 className="text-lg font-bold gradient-text">
                AI Document Summarizer
              </h1>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {hasDocument && (
              <Button
                onClick={onReset}
                variant="outline"
                size="sm"
                className="glass-card border-primary/20 hover:border-primary/40"
              >
                <RotateCcw className="w-4 h-4 mr-2" />
                <span className="hidden sm:inline">New Document</span>
                <span className="sm:hidden">Reset</span>
              </Button>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;