import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { studentResultAPI, studentAPI, subjectAPI, subjectTeacherAPI } from '../services/api';
import { toast } from 'react-hot-toast';
import DashboardLayout from '../components/DashboardLayout';

const ARUCASER = () => {
  const { resultId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (resultId) {
      fetchResult();
    }
  }, [resultId]);

  const fetchResult = async () => {
    try {
      setLoading(true);
      const response = await studentResultAPI.getStudentResultById(resultId);
      setResult(response.data);
    } catch (error) {
      console.error('Error fetching result:', error);
      setError('Failed to load student result');
      toast.error('Failed to load student result');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade) => {
    const gradeColors = {
      'A': 'text-green-600 bg-green-100',
      'B': 'text-blue-600 bg-blue-100',
      'C': 'text-yellow-600 bg-yellow-100',
      'D': 'text-orange-600 bg-orange-100',
      'E': 'text-red-600 bg-red-100',
      'F': 'text-red-700 bg-red-200'
    };
    return gradeColors[grade] || 'text-gray-600 bg-gray-100';
  };

  const getPerformanceStatus = (average) => {
    if (average >= 80) return { status: 'Excellent', color: 'text-green-600 bg-green-100' };
    if (average >= 70) return { status: 'Very Good', color: 'text-blue-600 bg-blue-100' };
    if (average >= 60) return { status: 'Good', color: 'text-yellow-600 bg-yellow-100' };
    if (average >= 50) return { status: 'Pass', color: 'text-orange-600 bg-orange-100' };
    return { status: 'Fail', color: 'text-red-600 bg-red-100' };
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error || !result) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">Error Loading Result</h2>
            <p className="text-gray-600">{error || 'Result not found'}</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  const performance = getPerformanceStatus(result.average_score);

  return (
    <DashboardLayout>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center">
                  <span className="text-white text-2xl font-bold">A</span>
                </div>
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">ARUCASER</h1>
                  <p className="text-gray-600">Arusha Catholic Seminary Academic Results</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Date Issued</p>
                <p className="font-semibold">{new Date(result.date_issued).toLocaleDateString()}</p>
              </div>
            </div>
          </div>

          {/* Student Information */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-4">Student Information</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <p className="text-lg font-semibold text-gray-900">{result.student_name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Class</label>
                <p className="text-lg font-semibold text-gray-900">{result.class_name || 'Not Assigned'}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Academic Year</label>
                <p className="text-lg font-semibold text-gray-900">{result.academic_year}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Term</label>
                <p className="text-lg font-semibold text-gray-900">{result.term}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Total Subjects</label>
                <p className="text-lg font-semibold text-gray-900">{result.total_subjects}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Position in Class</label>
                <p className="text-lg font-semibold text-gray-900">
                  {result.position_in_class ? `${result.position_in_class} of ${result.total_students_in_class}` : 'Not Available'}
                </p>
              </div>
            </div>
          </div>

          {/* Academic Performance Summary */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-4">Academic Performance Summary</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90">Total Score</p>
                    <p className="text-3xl font-bold">{result.total_score}</p>
                  </div>
                  <div className="text-4xl opacity-20">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90">Average Score</p>
                    <p className="text-3xl font-bold">{result.average_score.toFixed(2)}%</p>
                  </div>
                  <div className="text-4xl opacity-20">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90">Performance</p>
                    <p className="text-3xl font-bold">{performance.status}</p>
                  </div>
                  <div className="text-4xl opacity-20">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  </div>
                </div>
              </div>
              
              <div className="bg-gradient-to-r from-orange-500 to-orange-600 rounded-lg p-6 text-white">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm opacity-90">Subjects</p>
                    <p className="text-3xl font-bold">{result.total_subjects}</p>
                  </div>
                  <div className="text-4xl opacity-20">
                    <svg className="w-12 h-12" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10.394 2.08a1 1 0 00-.788 0l-7 3a1 1 0 000 1.84L5.25 8.051a.999.999 0 01.356-.257l4-1.714a1 1 0 11.788 1.838L7.667 9.088l1.94.831a1 1 0 00.787 0l7-3a1 1 0 000-1.838l-7-3zM3.31 9.397L5 10.12v4.102a8.969 8.969 0 00-1.05-.174 1 1 0 01-.89-.89 11.115 11.115 0 01.25-3.762zM9.3 16.573A9.026 9.026 0 007 14.935v-3.957l1.818.78a3 3 0 002.364 0l5.508-2.361a11.026 11.026 0 01.25 3.762 1 1 0 01-.89.89 8.968 8.968 0 00-5.35 2.524 1 1 0 01-1.4 0zM6 18a1 1 0 001-1v-2.065a8.935 8.935 0 00-2-.712V17a1 1 0 001 1z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Subject Results */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-4">Subject Results</h2>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Subject
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Subject Teacher
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Score
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Grade
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Remarks
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {result.result_details.map((detail, index) => (
                    <tr key={detail.id} className={index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">{detail.subject_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{detail.teacher_name}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-semibold text-gray-900">{detail.score}%</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getGradeColor(detail.grade_letter)}`}>
                          {detail.grade_letter}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm text-gray-900">{detail.remarks || 'No remarks'}</div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Remarks Section */}
          {result.remarks && (
            <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6 border-b pb-4">General Remarks</h2>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
                <p className="text-gray-800">{result.remarks}</p>
              </div>
            </div>
          )}

          {/* Footer */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Issued by</p>
                  <p className="font-semibold text-gray-900">School Administration</p>
                </div>
              </div>
              <div className="text-right">
                <p className="text-sm text-gray-500">Result ID</p>
                <p className="font-semibold text-gray-900">#{result.id}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default ARUCASER; 