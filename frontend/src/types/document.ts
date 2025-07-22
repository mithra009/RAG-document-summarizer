export interface DocumentInfo {
  filename: string;
  type: string;
  pageCount: number;
  chunkCount: number;
  summary: string;
  classification: string;
  uploadedAt: string;
}

export interface QueryMessage {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: string;
  isTyping?: boolean;
}

export interface UploadProgress {
  stage: 'idle' | 'uploading' | 'analyzing' | 'summarizing' | 'complete' | 'error';
  progress: number;
  message: string;
}

export interface ApiError {
  message: string;
  status?: number;
}