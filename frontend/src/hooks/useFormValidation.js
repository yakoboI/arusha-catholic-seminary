import { useState, useCallback } from 'react';

// Validation rules
const VALIDATION_RULES = {
  required: (value) => value && value.trim().length > 0 || 'This field is required',
  
  email: (value) => {
    if (!value) return true; // Skip if empty (use required for mandatory)
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(value) || 'Please enter a valid email address';
  },
  
  minLength: (min) => (value) => {
    if (!value) return true;
    return value.length >= min || `Must be at least ${min} characters`;
  },
  
  maxLength: (max) => (value) => {
    if (!value) return true;
    return value.length <= max || `Must be no more than ${max} characters`;
  },
  
  phone: (value) => {
    if (!value) return true;
    const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
    return phoneRegex.test(value.replace(/[\s\-\(\)]/g, '')) || 'Please enter a valid phone number';
  },
  
  password: (value) => {
    if (!value) return true;
    const hasUpperCase = /[A-Z]/.test(value);
    const hasLowerCase = /[a-z]/.test(value);
    const hasNumbers = /\d/.test(value);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(value);
    
    if (value.length < 8) return 'Password must be at least 8 characters';
    if (!hasUpperCase) return 'Password must contain at least one uppercase letter';
    if (!hasLowerCase) return 'Password must contain at least one lowercase letter';
    if (!hasNumbers) return 'Password must contain at least one number';
    if (!hasSpecialChar) return 'Password must contain at least one special character';
    
    return true;
  },
  
  confirmPassword: (password) => (value) => {
    if (!value) return true;
    return value === password || 'Passwords do not match';
  },
  
  number: (value) => {
    if (!value) return true;
    return !isNaN(value) && !isNaN(parseFloat(value)) || 'Must be a valid number';
  },
  
  positiveNumber: (value) => {
    if (!value) return true;
    const num = parseFloat(value);
    return !isNaN(num) && num > 0 || 'Must be a positive number';
  },
  
  date: (value) => {
    if (!value) return true;
    const date = new Date(value);
    return !isNaN(date.getTime()) || 'Please enter a valid date';
  },
  
  futureDate: (value) => {
    if (!value) return true;
    const date = new Date(value);
    const today = new Date();
    return date > today || 'Date must be in the future';
  },
  
  pastDate: (value) => {
    if (!value) return true;
    const date = new Date(value);
    const today = new Date();
    return date < today || 'Date must be in the past';
  },
  
  url: (value) => {
    if (!value) return true;
    try {
      new URL(value);
      return true;
    } catch {
      return 'Please enter a valid URL';
    }
  },
  
  custom: (validator) => (value) => {
    return validator(value);
  },
};

// Validation schemas for common forms
export const VALIDATION_SCHEMAS = {
  login: {
    username: ['required', 'email'],
    password: ['required', 'minLength:6'],
  },
  
  register: {
    username: ['required', 'email'],
    full_name: ['required', 'minLength:2', 'maxLength:100'],
    password: ['required', 'password'],
    confirm_password: ['required', 'confirmPassword'],
    role: ['required'],
  },
  
  student: {
    admission_number: ['required', 'minLength:3', 'maxLength:20'],
    prem_number: ['required', 'minLength:3', 'maxLength:20'],
    full_name: ['required', 'minLength:2', 'maxLength:100'],
    date_of_birth: ['required', 'date', 'pastDate'],
    gender: ['required'],
    address: ['required', 'minLength:5', 'maxLength:200'],
    phone: ['required', 'phone'],
    email: ['email'],
    parent_name: ['required', 'minLength:2', 'maxLength:100'],
    parent_phone: ['required', 'phone'],
    student_level: ['required'],
  },
  
  teacher: {
    employee_id: ['required', 'minLength:3', 'maxLength:20'],
    full_name: ['required', 'minLength:2', 'maxLength:100'],
    email: ['required', 'email'],
    phone: ['required', 'phone'],
    subject: ['required', 'minLength:2', 'maxLength:50'],
    qualification: ['required', 'minLength:2', 'maxLength:100'],
    hire_date: ['required', 'date'],
    salary: ['required', 'positiveNumber'],
    status: ['required'],
  },
  
  class: {
    name: ['required', 'minLength:2', 'maxLength:50'],
    level: ['required'],
    capacity: ['required', 'positiveNumber'],
    academic_year: ['required', 'minLength:4', 'maxLength:4'],
    room_number: ['required', 'minLength:1', 'maxLength:20'],
    description: ['maxLength:200'],
  },
  
  grade: {
    student_id: ['required', 'number'],
    subject_id: ['required', 'number'],
    class_id: ['required', 'number'],
    term: ['required', 'minLength:2', 'maxLength:20'],
    academic_year: ['required', 'minLength:4', 'maxLength:4'],
    test_score: ['number'],
    exam_score: ['number'],
    assignment_score: ['number'],
    remarks: ['maxLength:500'],
  },
};

const useFormValidation = (initialValues = {}, schema = {}) => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Validate a single field
  const validateField = useCallback((name, value) => {
    if (!schema[name]) return '';
    
    const fieldRules = Array.isArray(schema[name]) ? schema[name] : [schema[name]];
    
    for (const rule of fieldRules) {
      let validator;
      let validatorArgs = [];
      
      if (typeof rule === 'string') {
        if (rule.includes(':')) {
          const [ruleName, ...args] = rule.split(':');
          validator = VALIDATION_RULES[ruleName];
          validatorArgs = args;
        } else {
          validator = VALIDATION_RULES[rule];
        }
      } else if (typeof rule === 'function') {
        validator = rule;
      } else if (rule.type && VALIDATION_RULES[rule.type]) {
        validator = VALIDATION_RULES[rule.type];
        validatorArgs = rule.args || [];
      }
      
      if (validator) {
        const validationFn = validatorArgs.length > 0 ? validator(...validatorArgs) : validator;
        const result = validationFn(value, values);
        
        if (result !== true) {
          return result;
        }
      }
    }
    
    return '';
  }, [schema, values]);

  // Validate all fields
  const validateForm = useCallback(() => {
    const newErrors = {};
    let isValid = true;
    
    Object.keys(schema).forEach(fieldName => {
      const error = validateField(fieldName, values[fieldName] || '');
      if (error) {
        newErrors[fieldName] = error;
        isValid = false;
      }
    });
    
    setErrors(newErrors);
    return isValid;
  }, [schema, values, validateField]);

  // Handle input change
  const handleChange = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  }, [errors]);

  // Handle input blur
  const handleBlur = useCallback((name) => {
    setTouched(prev => ({ ...prev, [name]: true }));
    
    const error = validateField(name, values[name] || '');
    setErrors(prev => ({ ...prev, [name]: error }));
  }, [validateField, values]);

  // Handle form submission
  const handleSubmit = useCallback(async (onSubmit) => {
    setIsSubmitting(true);
    
    // Mark all fields as touched
    const allTouched = {};
    Object.keys(schema).forEach(key => {
      allTouched[key] = true;
    });
    setTouched(allTouched);
    
    // Validate form
    const isValid = validateForm();
    
    if (isValid) {
      try {
        await onSubmit(values);
      } catch (error) {
        console.error('Form submission error:', error);
      }
    }
    
    setIsSubmitting(false);
  }, [schema, values, validateForm]);

  // Reset form
  const resetForm = useCallback((newValues = {}) => {
    setValues(newValues);
    setErrors({});
    setTouched({});
    setIsSubmitting(false);
  }, []);

  // Set field value
  const setFieldValue = useCallback((name, value) => {
    setValues(prev => ({ ...prev, [name]: value }));
  }, []);

  // Set field error
  const setFieldError = useCallback((name, error) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  // Get field props for input components
  const getFieldProps = useCallback((name) => ({
    value: values[name] || '',
    onChange: (e) => handleChange(name, e.target.value),
    onBlur: () => handleBlur(name),
    error: touched[name] ? errors[name] : '',
    isTouched: touched[name],
  }), [values, handleChange, handleBlur, touched, errors]);

  // Check if form is valid
  const isValid = Object.keys(errors).length === 0 || Object.values(errors).every(error => !error);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    isValid,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
    setFieldValue,
    setFieldError,
    getFieldProps,
    validateField,
    validateForm,
  };
};

export default useFormValidation; 