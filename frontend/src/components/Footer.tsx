import { Github } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="mt-20 bg-white/5 backdrop-blur-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center">

          <div className="flex items-center justify-center gap-6 mt-4">
            <a
              href="https://github.com/mithra009"
              target="_blank"
              rel="noopener noreferrer"
              className="text-muted-foreground hover:text-primary transition-colors"
              aria-label="GitHub"
            >
              <Github className="w-5 h-5" />
            </a>

          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;