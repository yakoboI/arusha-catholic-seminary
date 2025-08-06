import React, { useState, useRef } from 'react';
import { fileUploadAPI } from '../services/api';
import { toast } from 'react-hot-toast';

const PhotoUpload = ({ 
  type = 'passport', // 'passport' or 'logo'
  userId, 
  currentPhoto = null,
  onPhotoUploaded = () => {},
  className = ''
}) => {
  const [isUploading, setIsUploading] = useState(false);
  const [preview, setPreview] = useState(currentPhoto);
  const fileInputRef = useRef(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      toast.error('Please select an image file');
      return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('File size must be less than 5MB');
      return;
    }

    // Create preview
    const reader = new FileReader();
    reader.onload = (e) => {
      setPreview(e.target.result);
    };
    reader.readAsDataURL(file);

    // Upload file
    uploadFile(file);
  };

  const uploadFile = async (file) => {
    setIsUploading(true);
    try {
      const uploadFunction = type === 'passport' 
        ? fileUploadAPI.uploadPassportPhoto 
        : fileUploadAPI.uploadSeminaryLogo;
      
      const response = await uploadFunction(file, userId);
      toast.success(`${type === 'passport' ? 'Passport photo' : 'Seminary logo'} uploaded successfully`);
      onPhotoUploaded(response.data.file_path);
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Failed to upload image. Please try again.');
      setPreview(currentPhoto); // Reset to current photo
    } finally {
      setIsUploading(false);
    }
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const getUploadText = () => {
    if (type === 'passport') {
      return preview ? 'Change Passport Photo' : 'Upload Passport Photo';
    } else {
      return preview ? 'Change Seminary Logo' : 'Upload Seminary Logo';
    }
  };

  return (
    <div className={`relative ${className}`}>
      {/* Photo/Logo Display */}
      <div 
        className={`
          relative cursor-pointer rounded-lg border-2 border-dashed border-gray-300 
          hover:border-blue-400 transition-colors duration-200
          ${type === 'passport' ? 'w-32 h-40' : 'w-32 h-32'}
          ${isUploading ? 'opacity-50' : ''}
        `}
        onClick={handleClick}
      >
        {preview ? (
          <img
            src={preview}
            alt={type === 'passport' ? 'Passport Photo' : 'Seminary Logo'}
            className="w-full h-full object-cover rounded-lg"
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-full text-gray-500">
            <svg className="w-8 h-8 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-xs text-center">
              {type === 'passport' ? 'Passport Photo' : 'Seminary Logo'}
            </span>
          </div>
        )}
        
        {/* Upload overlay */}
        <div className="absolute inset-0 bg-black bg-opacity-0 hover:bg-opacity-30 transition-all duration-200 rounded-lg flex items-center justify-center">
          <span className="text-white text-xs font-medium opacity-0 hover:opacity-100 transition-opacity duration-200">
            {getUploadText()}
          </span>
        </div>
      </div>

      {/* Loading indicator */}
      {isUploading && (
        <div className="absolute inset-0 bg-black bg-opacity-50 rounded-lg flex items-center justify-center">
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
        </div>
      )}

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileSelect}
        className="hidden"
        disabled={isUploading}
      />

      {/* Upload button */}
      <button
        type="button"
        onClick={handleClick}
        disabled={isUploading}
        className="mt-2 w-full px-3 py-1 text-xs font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md transition-colors duration-200 disabled:opacity-50"
      >
        {isUploading ? 'Uploading...' : getUploadText()}
      </button>
    </div>
  );
};

export default PhotoUpload; 