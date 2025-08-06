import React, { useState, useEffect } from 'react';
import { studentAPI } from '../services/api';
import toast from 'react-hot-toast';

const Parents = () => {
  const [parents, setParents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedParent, setSelectedParent] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);

  useEffect(() => {
    setLoading(true);
    studentAPI.getStudents()
      .then(res => {
        // Map students to parent info objects
        const parentList = res.data
          .filter(student => student.parent_name && student.parent_phone)
          .map(student => ({
            id: student.id,
            name: student.parent_name,
            phone: student.parent_phone,
            studentName: student.full_name,
            studentClass: student.class_id || '',
            address: student.address || '',
            // Add more fields if available
          }));
        setParents(parentList);
      })
      .catch(() => {
        toast.error('Failed to fetch parent data');
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredParents = parents.filter(parent =>
    parent.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    parent.studentName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    parent.phone.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewParent = (parent) => {
    setSelectedParent(parent);
    setShowViewModal(true);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl shadow-soft p-6">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">Parents</h1>
            <p className="text-secondary-600 mt-1">Manage parent information and communications</p>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white rounded-xl shadow-soft p-6">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-5 w-5 text-secondary-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <input
                type="text"
                placeholder="Search parents by name, student, or phone..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Parents Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredParents.map((parent) => (
          <div key={parent.id} className="bg-white rounded-xl shadow-soft p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-600 font-semibold text-lg">
                  {parent.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleViewParent(parent)}
                  className="p-2 text-secondary-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-secondary-900 mb-1">{parent.name}</h3>
            <div className="space-y-2 mb-4">
              <div className="flex items-center text-sm">
                <svg className="w-4 h-4 text-secondary-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
                <span className="text-secondary-600">{parent.phone}</span>
              </div>
            </div>
            <div className="border-t border-secondary-200 pt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-secondary-500">Student:</span>
                <span className="font-medium text-secondary-900">{parent.studentName}</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-secondary-500">Class:</span>
                <span className="font-medium text-secondary-900">{parent.studentClass}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* View Parent Modal */}
      {showViewModal && selectedParent && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-secondary-900">Parent Details</h2>
              <button
                onClick={() => setShowViewModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
                  <span className="text-primary-600 font-semibold text-xl">
                    {selectedParent.name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900">{selectedParent.name}</h3>
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Phone</label>
                  <p className="text-secondary-900">{selectedParent.phone}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Student Name</label>
                  <p className="text-secondary-900">{selectedParent.studentName}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Class</label>
                  <p className="text-secondary-900">{selectedParent.studentClass}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Address</label>
                  <p className="text-secondary-900">{selectedParent.address}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Parents; 