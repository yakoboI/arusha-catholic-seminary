import React, { createContext, useContext, useState, useCallback } from 'react';
import ActionFeedback, { LoadingFeedback, ProgressFeedback, ConfirmationDialog } from '../components/ActionFeedback';

const FeedbackContext = createContext();

export const useFeedback = () => {
  const context = useContext(FeedbackContext);
  if (!context) {
    throw new Error('useFeedback must be used within a FeedbackProvider');
  }
  return context;
};

export const FeedbackProvider = ({ children }) => {
  const [feedback, setFeedback] = useState({
    show: false,
    type: 'info',
    message: '',
    title: '',
    autoClose: true,
    autoCloseDelay: 5000
  });

  const [loading, setLoading] = useState({
    show: false,
    message: 'Processing...'
  });

  const [progress, setProgress] = useState({
    show: false,
    progress: 0,
    message: 'Uploading...',
    onCancel: null
  });

  const [confirmation, setConfirmation] = useState({
    show: false,
    title: 'Confirm Action',
    message: 'Are you sure you want to perform this action?',
    confirmText: 'Confirm',
    cancelText: 'Cancel',
    type: 'warning',
    onConfirm: null,
    onCancel: null
  });

  // Show success feedback
  const showSuccess = useCallback((message, title = 'Success', autoClose = true, delay = 3000) => {
    setFeedback({
      show: true,
      type: 'success',
      message,
      title,
      autoClose,
      autoCloseDelay: delay
    });
  }, []);

  // Show error feedback
  const showError = useCallback((message, title = 'Error', autoClose = true, delay = 5000) => {
    setFeedback({
      show: true,
      type: 'error',
      message,
      title,
      autoClose,
      autoCloseDelay: delay
    });
  }, []);

  // Show warning feedback
  const showWarning = useCallback((message, title = 'Warning', autoClose = true, delay = 4000) => {
    setFeedback({
      show: true,
      type: 'warning',
      message,
      title,
      autoClose,
      autoCloseDelay: delay
    });
  }, []);

  // Show info feedback
  const showInfo = useCallback((message, title = 'Information', autoClose = true, delay = 4000) => {
    setFeedback({
      show: true,
      type: 'info',
      message,
      title,
      autoClose,
      autoCloseDelay: delay
    });
  }, []);

  // Hide feedback
  const hideFeedback = useCallback(() => {
    setFeedback(prev => ({ ...prev, show: false }));
  }, []);

  // Show loading
  const showLoading = useCallback((message = 'Processing...') => {
    setLoading({
      show: true,
      message
    });
  }, []);

  // Hide loading
  const hideLoading = useCallback(() => {
    setLoading(prev => ({ ...prev, show: false }));
  }, []);

  // Show progress
  const showProgress = useCallback((progress = 0, message = 'Uploading...', onCancel = null) => {
    setProgress({
      show: true,
      progress,
      message,
      onCancel
    });
  }, []);

  // Update progress
  const updateProgress = useCallback((progress, message = null) => {
    setProgress(prev => ({
      ...prev,
      progress,
      ...(message && { message })
    }));
  }, []);

  // Hide progress
  const hideProgress = useCallback(() => {
    setProgress(prev => ({ ...prev, show: false }));
  }, []);

  // Show confirmation dialog
  const showConfirmation = useCallback(({
    title = 'Confirm Action',
    message = 'Are you sure you want to perform this action?',
    confirmText = 'Confirm',
    cancelText = 'Cancel',
    type = 'warning',
    onConfirm,
    onCancel
  }) => {
    setConfirmation({
      show: true,
      title,
      message,
      confirmText,
      cancelText,
      type,
      onConfirm,
      onCancel
    });
  }, []);

  // Hide confirmation dialog
  const hideConfirmation = useCallback(() => {
    setConfirmation(prev => ({ ...prev, show: false }));
  }, []);

  // Handle confirmation
  const handleConfirm = useCallback(() => {
    if (confirmation.onConfirm) {
      confirmation.onConfirm();
    }
    hideConfirmation();
  }, [confirmation, hideConfirmation]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    if (confirmation.onCancel) {
      confirmation.onCancel();
    }
    hideConfirmation();
  }, [confirmation, hideConfirmation]);

  // API wrapper for async operations
  const withFeedback = useCallback(async (asyncOperation, {
    loadingMessage = 'Processing...',
    successMessage = 'Operation completed successfully',
    errorMessage = 'An error occurred',
    successTitle = 'Success',
    errorTitle = 'Error'
  } = {}) => {
    try {
      showLoading(loadingMessage);
      const result = await asyncOperation();
      hideLoading();
      
      if (result && result.success !== false) {
        showSuccess(successMessage, successTitle);
        return result;
      } else {
        const errorMsg = result?.error || errorMessage;
        showError(errorMsg, errorTitle);
        return result;
      }
    } catch (error) {
      hideLoading();
      const errorMsg = error?.message || errorMessage;
      showError(errorMsg, errorTitle);
      throw error;
    }
  }, [showLoading, hideLoading, showSuccess, showError]);

  const value = {
    // Feedback methods
    showSuccess,
    showError,
    showWarning,
    showInfo,
    hideFeedback,
    
    // Loading methods
    showLoading,
    hideLoading,
    
    // Progress methods
    showProgress,
    updateProgress,
    hideProgress,
    
    // Confirmation methods
    showConfirmation,
    hideConfirmation,
    
    // Utility method
    withFeedback,
    
    // State
    feedback,
    loading,
    progress,
    confirmation
  };

  return (
    <FeedbackContext.Provider value={value}>
      {children}
      
      {/* Global Feedback Components */}
      <ActionFeedback
        type={feedback.type}
        message={feedback.message}
        title={feedback.title}
        show={feedback.show}
        onClose={hideFeedback}
        autoClose={feedback.autoClose}
        autoCloseDelay={feedback.autoCloseDelay}
      />

      <LoadingFeedback
        message={loading.message}
        show={loading.show}
      />

      <ProgressFeedback
        progress={progress.progress}
        message={progress.message}
        show={progress.show}
        onCancel={progress.onCancel}
      />

      <ConfirmationDialog
        title={confirmation.title}
        message={confirmation.message}
        confirmText={confirmation.confirmText}
        cancelText={confirmation.cancelText}
        type={confirmation.type}
        show={confirmation.show}
        onConfirm={handleConfirm}
        onCancel={handleCancel}
      />
    </FeedbackContext.Provider>
  );
}; 