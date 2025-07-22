import { useState, useRef, DragEvent, ChangeEvent } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface FileUploadProps {
  onUploadComplete: () => void;
  uploadDocument: (file: File) => Promise<boolean>;
  uploadProgress: any;
  isProcessing: boolean;
}

const FileUpload = ({ onUploadComplete, uploadDocument, uploadProgress, isProcessing }: FileUploadProps) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const allowedTypes = [
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
  ];

  const maxSize = 100 * 1024 * 1024; // 100MB

  const validateFile = (file: File): string | null => {
    if (!allowedTypes.includes(file.type)) {
      return 'Please upload a PDF, DOCX, PPTX, or TXT file.';
    }
    if (file.size > maxSize) {
      return 'File size must be less than 100MB.';
    }
    return null;
  };

  const handleFileSelect = (file: File) => {
    const error = validateFile(file);
    if (error) {
      alert(error); // In a real app, use a proper notification
      return;
    }
    setSelectedFile(file);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragOver(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    const success = await uploadDocument(selectedFile);
    if (success) {
      onUploadComplete();
    }
  };

  const getFileIcon = (file: File) => {
    return <FileText className="w-8 h-8 text-primary" />;
  };

  const getStageIcon = () => {
    switch (uploadProgress.stage) {
      case 'error':
        return <AlertCircle className="w-5 h-5 text-destructive" />;
      case 'complete':
        return <CheckCircle2 className="w-5 h-5 text-success" />;
      default:
        return null;
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      {/* Upload Area */}
      <div
        className={cn(
          "upload-area transition-all duration-300",
          isDragOver && "dragover",
          isProcessing && "pointer-events-none opacity-50"
        )}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.docx,.pptx,.txt"
          onChange={handleFileChange}
          className="hidden"
          disabled={isProcessing}
        />

        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-primary/10 rounded-3xl flex items-center justify-center">
            <Upload className="w-8 h-8 text-primary" />
          </div>
          
          <h3 className="text-xl font-semibold mb-2">
            {selectedFile ? 'File Selected' : 'Upload Your Document'}
          </h3>
          
          <p className="text-muted-foreground mb-4">
            {selectedFile 
              ? `${selectedFile.name} (${(selectedFile.size / 1024 / 1024).toFixed(1)} MB)`
              : 'Drag & drop your file here or click to browse'
            }
          </p>

          {selectedFile && (
            <div className="flex items-center justify-center gap-2 mb-4 p-3 bg-primary/5 rounded-xl">
              {getFileIcon(selectedFile)}
              <span className="text-sm font-medium">{selectedFile.name}</span>
            </div>
          )}

          <div className="text-sm text-muted-foreground space-y-1">
            <p>Supported formats: PDF, DOCX, PPTX, TXT</p>
            <p>Maximum size: 100MB</p>
          </div>
        </div>
      </div>

      {/* Upload Button */}
      {selectedFile && !isProcessing && uploadProgress.stage !== 'complete' && (
        <div className="mt-6 text-center">
          <Button 
            onClick={handleUpload}
            className="btn-primary"
            size="lg"
          >
            <Upload className="w-5 h-5 mr-2" />
            Upload & Analyze
          </Button>
        </div>
      )}

      {/* Progress Indicator */}
      {isProcessing && (
        <div className="mt-6 glass-card p-6">
          <div className="flex items-center gap-3 mb-3">
            {getStageIcon()}
            <span className="font-medium">{uploadProgress.message}</span>
          </div>
          
          <div className="w-full bg-muted rounded-full h-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-500"
              style={{ width: `${uploadProgress.progress}%` }}
            />
          </div>
          
          <div className="text-right text-sm text-muted-foreground mt-2">
            {uploadProgress.progress}%
          </div>
        </div>
      )}

      {/* Success State */}
      {uploadProgress.stage === 'complete' && (
        <div className="mt-6 glass-card p-6 border border-success/20">
          <div className="flex items-center gap-3 text-success">
            <CheckCircle2 className="w-6 h-6" />
            <span className="font-medium">Document processed successfully!</span>
          </div>
        </div>
      )}

      {/* Error State */}
      {uploadProgress.stage === 'error' && (
        <div className="mt-6 glass-card p-6 border border-destructive/20">
          <div className="flex items-center gap-3 text-destructive">
            <AlertCircle className="w-6 h-6" />
            <span className="font-medium">{uploadProgress.message}</span>
          </div>
          <Button 
            onClick={() => setSelectedFile(null)}
            variant="outline" 
            className="mt-3"
          >
            Try Again
          </Button>
        </div>
      )}
    </div>
  );
};

export default FileUpload;