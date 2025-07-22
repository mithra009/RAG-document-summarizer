import { useState, useEffect } from 'react';
import { Toaster } from '@/components/ui/toaster';
import { useDocumentUpload } from '@/hooks/useDocumentUpload';
import Navbar from '@/components/Navbar';
import Hero from '@/components/Hero';
import FileUpload from '@/components/FileUpload';
import DocumentAnalysis from '@/components/DocumentAnalysis';
import QueryInterface from '@/components/QueryInterface';
import Footer from '@/components/Footer';

const Index = () => {
  const [showUpload, setShowUpload] = useState(true);
  const {
    documentInfo,
    resetUpload,
    uploadDocument,
    uploadProgress,
    isProcessing
  } = useDocumentUpload();

  useEffect(() => {
    if (documentInfo) {
      console.log('documentInfo updated:', documentInfo);
    }
  }, [documentInfo]);

  const handleUploadComplete = () => {
    setShowUpload(false);
  };

  const handleReset = () => {
    resetUpload();
    setShowUpload(true);
  };

  return (
    <div className="min-h-screen">
      <Navbar onReset={handleReset} hasDocument={!!documentInfo} />
      <main className="pt-16">
        {/* Hero Section - Always visible */}
        <section id="hero">
          <Hero />
        </section>
        {/* Upload Section - Show when no document or uploading */}
        {showUpload && (
          <section id="upload" className="py-20 px-4">
            <div className="max-w-7xl mx-auto">
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold mb-4">Upload Your Document</h2>
                <p className="text-muted-foreground">
                  Get started by uploading a document for AI-powered analysis
                </p>
              </div>
              <FileUpload
                onUploadComplete={handleUploadComplete}
                uploadDocument={uploadDocument}
                uploadProgress={uploadProgress}
                isProcessing={isProcessing}
              />
            </div>
          </section>
        )}
        {/* Document Analysis Section - Show after successful upload */}
        {documentInfo && (
          <section id="analysis" className="py-20 px-4">
            <div className="max-w-7xl mx-auto">
              <DocumentAnalysis documentInfo={documentInfo} />
            </div>
          </section>
        )}
        {/* Query Section - Show after document analysis */}
        {documentInfo && (
          <section id="query" className="py-20 px-4">
            <div className="max-w-7xl mx-auto">
              <QueryInterface documentInfo={documentInfo} />
            </div>
          </section>
        )}
      </main>
      <Footer />
      <Toaster />
    </div>
  );
};

export default Index;
