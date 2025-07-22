import { useState } from 'react';
import { DocumentInfo, UploadProgress, ApiError } from '@/types/document';
import { toast } from '@/hooks/use-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:7860';

export const useDocumentUpload = () => {
  const [uploadProgress, setUploadProgress] = useState<UploadProgress>({
    stage: 'idle',
    progress: 0,
    message: ''
  });
  const [documentInfo, setDocumentInfo] = useState<DocumentInfo | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const uploadDocument = async (file: File): Promise<boolean> => {
    setIsProcessing(true);
    setUploadProgress({
      stage: 'uploading',
      progress: 10,
      message: 'Uploading document...'
    });

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => ({
          ...prev,
          progress: Math.min(prev.progress + 10, 80)
        }));
      }, 200);

      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      setUploadProgress({
        stage: 'analyzing',
        progress: 85,
        message: 'Analyzing document structure...'
      });

      const result = await response.json();

      setUploadProgress({
        stage: 'summarizing',
        progress: 95,
        message: 'Generating summary...'
      });

      // Create document info from response
      const docInfo: DocumentInfo = {
        filename: result.filename,
        type: file.type,
        pageCount: result.page_estimate || 1,
        chunkCount: result.chunk_count || 1,
        summary: result.summary || 'Document processed successfully.',
        classification: result.classification || 'General Document',
        uploadedAt: new Date().toISOString()
      };

      setDocumentInfo(docInfo);
      setUploadProgress({
        stage: 'complete',
        progress: 100,
        message: 'Document processed successfully!'
      });

      toast({
        title: "Success",
        description: "Document uploaded and processed successfully!",
        variant: "default"
      });

      return true;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Upload failed';
      
      setUploadProgress({
        stage: 'error',
        progress: 0,
        message: errorMessage
      });

      toast({
        title: "Upload Failed",
        description: errorMessage,
        variant: "destructive"
      });

      return false;
    } finally {
      setIsProcessing(false);
    }
  };

  const resetUpload = () => {
    setUploadProgress({
      stage: 'idle',
      progress: 0,
      message: ''
    });
    setDocumentInfo(null);
    setIsProcessing(false);
  };

  return {
    uploadProgress,
    documentInfo,
    isProcessing,
    uploadDocument,
    resetUpload
  };
};