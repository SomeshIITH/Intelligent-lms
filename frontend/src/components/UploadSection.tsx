import React, { useState, useRef } from 'react';
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { apiService } from '../services/api';
import { logger } from '../utils/logger';

const CONTEXT = 'UPLOAD_COMPONENT';

interface UploadSectionProps {
  onUploadSuccess: (filename: string) => void;
}

export const UploadSection: React.FC<UploadSectionProps> = ({ onUploadSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [chunkCount, setChunkCount] = useState<number | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.type !== 'application/pdf') {
        logger.warn(CONTEXT, 'Rejected non-PDF asset submission attempt.');
        setErrorMessage('Invalid type. Please select a structural PDF file.');
        setStatus('error');
        return;
      }
      logger.info(CONTEXT, `Staged file target for ingestion: ${selectedFile.name}`);
      setFile(selectedFile);
      setStatus('idle');
      setErrorMessage('');
      setChunkCount(null);
    }
  };

  const handleUploadSubmit = async () => {
    if (!file) return;

    setStatus('uploading');
    logger.info(CONTEXT, `Dispatching multipart upload package: ${file.name}`);

    try {
      const response = await apiService.uploadFile(file);
      if (response.success) {
        logger.info(CONTEXT, `Successfully ingested file layout context: ${response.filename}`);
        setStatus('success');
        setChunkCount(response.chunk_count);
        onUploadSuccess(response.filename);
      } else {
        throw new Error(response.message || 'Ingestion engine pipeline validation rejected.');
      }
    } catch (err: any) {
      const msg = err.message || 'Connection failure encountered during file upload execution.';
      logger.error(CONTEXT, 'Ingestion validation routine crashed.', err);
      setStatus('error');
      setErrorMessage(msg);
    }
  };

  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="mb-4">
        <h2 className="text-xl font-bold text-slate-800 tracking-tight">Knowledge Base Ingestion</h2>
        <p className="text-sm text-slate-500">
          Upload an academic lecture or text PDF. Note: Ingesting a new context purges previous index matrices.
        </p>
      </div>

      <div 
        onClick={triggerFileSelect}
        className={`border-2 border-dashed rounded-lg p-8 flex flex-col items-center justify-center cursor-pointer transition-colors ${
          status === 'uploading' ? 'bg-slate-50 border-blue-300 pointer-events-none' : 'border-slate-300 hover:bg-slate-50'
        }`}
      >
        <input 
          type="file" 
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf"
          className="hidden"
        />
        
        {file ? (
          <FileText className="h-10 w-10 text-blue-500 mb-2" />
        ) : (
          <Upload className="h-10 w-10 text-slate-400 mb-2" />
        )}

        <span className="text-sm font-medium text-slate-700">
          {file ? file.name : 'Click to select PDF document'}
        </span>
        <span className="text-xs text-slate-400 mt-1">
          {file ? `${(file.size / (1024 * 1024)).toFixed(2)} MB` : 'PDF specifications only up to 50MB'}
        </span>
      </div>

      {status === 'error' && (
        <div className="mt-4 flex items-start gap-3 bg-red-50 border border-red-200 p-3 rounded-lg text-red-700 text-sm">
          <AlertCircle className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Ingestion Error:</span> {errorMessage}
          </div>
        </div>
      )}

      {status === 'success' && (
        <div className="mt-4 flex items-start gap-3 bg-emerald-50 border border-emerald-200 p-3 rounded-lg text-emerald-800 text-sm">
          <CheckCircle2 className="h-5 w-5 shrink-0 mt-0.5" />
          <div>
            <span className="font-semibold">Context Uploaded Successfully!</span>
            <p className="text-xs text-emerald-600 mt-1">
              Parsed vector store targets into <span className="font-bold">{chunkCount}</span> overlapping matrices segments.
            </p>
          </div>
        </div>
      )}

      {file && status !== 'success' && (
        <button
          onClick={handleUploadSubmit}
          disabled={status === 'uploading'}
          className="w-full mt-4 bg-slate-900 text-white font-medium py-2.5 px-4 rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2 disabled:bg-slate-400 cursor-pointer"
        >
          {status === 'uploading' ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin" />
              Parsing Content Matrices...
            </>
          ) : (
            'Process Document Structure'
          )}
        </button>
      )}
    </div>
  );
};