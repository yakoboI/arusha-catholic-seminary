import React, { useState, useEffect } from 'react';
import { alumniAPI } from '../services/api';
import toast from 'react-hot-toast';

const Alumni = () => {
  const [alumni, setAlumni] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedYear, setSelectedYear] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedAlumni, setSelectedAlumni] = useState(null);
  const [showViewModal, setShowViewModal] = useState(false);

  useEffect(() => {
    setLoading(true);
    alumniAPI.getAlumni()
      .then(res => {
        setAlumni(res.data);
      })
      .catch(() => {
        toast.error('Failed to fetch alumni data');
      })
      .finally(() => setLoading(false));
  }, []);

  const filteredAlumni = alumni.filter(alum =>
    alum.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alum.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
    alum.current_occupation?.toLowerCase().includes(searchTerm.toLowerCase())
  ).filter(alum => 
    !selectedYear || alum.graduation_year.toString() === selectedYear
  );

  const graduationYears = [...new Set(alumni.map(alum => alum.graduation_year))].sort((a, b) => b - a);

  const handleViewAlumni = (alum) => {
    setSelectedAlumni(alum);
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
            <h1 className="text-2xl font-bold text-secondary-900">Alumni Network</h1>
            <p className="text-secondary-600 mt-1">Connect with our graduated students</p>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid gap-6 md:grid-cols-3">
        <div className="bg-white rounded-xl shadow-soft p-6">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <svg className="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Total Alumni</p>
              <p className="text-2xl font-bold text-secondary-900">{alumni.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-soft p-6">
          <div className="flex items-center">
            <div className="p-3 bg-accent-100 rounded-lg">
              <svg className="w-6 h-6 text-accent-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V8a2 2 0 012-2V6" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Graduation Years</p>
              <p className="text-2xl font-bold text-secondary-900">{graduationYears.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl shadow-soft p-6">
          <div className="flex items-center">
            <div className="p-3 bg-success-100 rounded-lg">
              <svg className="w-6 h-6 text-success-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-secondary-600">Active Network</p>
              <p className="text-2xl font-bold text-secondary-900">{alumni.filter(a => a.is_active).length}</p>
            </div>
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
                placeholder="Search alumni by name, email, or occupation..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="block w-full pl-10 pr-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              />
            </div>
          </div>
          <div className="sm:w-48">
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="block w-full px-3 py-2 border border-secondary-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="">All Years</option>
              {graduationYears.map(year => (
                <option key={year} value={year}>{year}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Alumni Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {filteredAlumni.map((alum) => (
          <div key={alum.id} className="bg-white rounded-xl shadow-soft p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-start justify-between mb-4">
              <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                <span className="text-primary-600 font-semibold text-lg">
                  {alum.full_name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => handleViewAlumni(alum)}
                  className="p-2 text-secondary-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
              </div>
            </div>
            
            <h3 className="text-lg font-semibold text-secondary-900 mb-1">{alum.full_name}</h3>
            <p className="text-secondary-600 text-sm mb-3">{alum.current_occupation || 'Occupation not specified'}</p>
            
            <div className="space-y-2 mb-4">
              <div className="flex items-center text-sm">
                <svg className="w-4 h-4 text-secondary-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
                <span className="text-secondary-600">{alum.email}</span>
              </div>
              <div className="flex items-center text-sm">
                <svg className="w-4 h-4 text-secondary-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                </svg>
                <span className="text-secondary-600">{alum.phone}</span>
              </div>
            </div>
            
            <div className="border-t border-secondary-200 pt-4">
              <div className="flex items-center justify-between text-sm">
                <span className="text-secondary-500">Graduated:</span>
                <span className="font-medium text-secondary-900">{alum.graduation_year}</span>
              </div>
              <div className="flex items-center justify-between text-sm mt-1">
                <span className="text-secondary-500">Class:</span>
                <span className="font-medium text-secondary-900">{alum.class_name}</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* View Alumni Modal */}
      {showViewModal && selectedAlumni && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-secondary-900">Alumni Details</h2>
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
                    {selectedAlumni.full_name.split(' ').map(n => n[0]).join('')}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-secondary-900">{selectedAlumni.full_name}</h3>
                  <p className="text-secondary-600">{selectedAlumni.current_occupation || 'Occupation not specified'}</p>
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Email</label>
                  <p className="text-secondary-900">{selectedAlumni.email}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Phone</label>
                  <p className="text-secondary-900">{selectedAlumni.phone}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Graduation Year</label>
                  <p className="text-secondary-900">{selectedAlumni.graduation_year}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Class</label>
                  <p className="text-secondary-900">{selectedAlumni.class_name}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Employer</label>
                  <p className="text-secondary-900">{selectedAlumni.employer || 'Not specified'}</p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Address</label>
                  <p className="text-secondary-900">{selectedAlumni.address || 'Not specified'}</p>
                </div>
              </div>
              
              {selectedAlumni.achievements && (
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Achievements</label>
                  <p className="text-secondary-900">{selectedAlumni.achievements}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Alumni; 