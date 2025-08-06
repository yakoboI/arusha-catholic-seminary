import React, { useState, useEffect } from 'react';
import { attendanceAPI, studentAPI, classAPI, handleApiError } from '../services/api';
import toast from 'react-hot-toast';

const Attendance = () => {
  const [attendance, setAttendance] = useState([]);
  const [students, setStudents] = useState([]);
  const [classes, setClasses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingAttendance, setEditingAttendance] = useState(null);
  const [selectedClass, setSelectedClass] = useState('');
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [formData, setFormData] = useState({
    class_id: '',
    date: '',
    student_id: '',
    status: 'present',
    remarks: ''
  });

  useEffect(() => {
    fetchAttendance();
    fetchSupportingData();
  }, []);

  const fetchAttendance = async () => {
    try {
      setLoading(true);
      const response = await attendanceAPI.getAttendance();
      if (response.success) {
        setAttendance(response.data || []);
      } else {
        toast.error(response.error?.message || 'Failed to fetch attendance');
        setAttendance([]);
      }
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
      setAttendance([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchSupportingData = async () => {
    try {
      const [studentsRes, classesRes] = await Promise.all([
        studentAPI.getStudents(),
        classAPI.getClasses()
      ]);
      setStudents(studentsRes.success ? (studentsRes.data || []) : []);
      setClasses(classesRes.success ? (classesRes.data || []) : []);
    } catch (error) {
      console.error('Error fetching supporting data:', error);
      setStudents([]);
      setClasses([]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingAttendance) {
        await attendanceAPI.updateAttendance(editingAttendance.id, formData);
        toast.success('Attendance updated successfully');
      } else {
        await attendanceAPI.createAttendance(formData);
        toast.success('Attendance marked successfully');
      }
      
      setShowAddModal(false);
      setEditingAttendance(null);
      resetForm();
      fetchAttendance();
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
  };

  const handleEdit = (attendanceRecord) => {
    setEditingAttendance(attendanceRecord);
    setFormData({
      class_id: attendanceRecord.class_id,
      date: attendanceRecord.date,
      student_id: attendanceRecord.student_id,
      status: attendanceRecord.status,
      remarks: attendanceRecord.remarks
    });
    setShowAddModal(true);
  };

  const handleDelete = async (attendanceId) => {
    if (window.confirm('Are you sure you want to delete this attendance record?')) {
      try {
        await attendanceAPI.deleteAttendance(attendanceId);
        toast.success('Attendance record deleted successfully');
        fetchAttendance();
      } catch (error) {
        const errorData = handleApiError(error);
        toast.error(errorData.message);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      class_id: '',
      date: '',
      student_id: '',
      status: 'present',
      remarks: ''
    });
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
    setEditingAttendance(null);
    resetForm();
  };

  const getStudentName = (studentId) => {
    if (!students || !Array.isArray(students)) return 'Unknown';
    const student = students.find(s => s.id === studentId);
    return student ? student.full_name : 'Unknown';
  };

  const getClassName = (classId) => {
    if (!classes || !Array.isArray(classes)) return 'Unknown';
    const classItem = classes.find(c => c.id === classId);
    return classItem ? classItem.name : 'Unknown';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'present': return 'bg-green-100 text-green-800';
      case 'absent': return 'bg-red-100 text-red-800';
      case 'late': return 'bg-yellow-100 text-yellow-800';
      case 'excused': return 'bg-blue-100 text-blue-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'present': return 'Present';
      case 'absent': return 'Absent';
      case 'late': return 'Late';
      case 'excused': return 'Excused';
      default: return status;
    }
  };

  const getAttendanceStats = () => {
    if (!attendance || !Array.isArray(attendance)) {
      return { present: 0, absent: 0, late: 0, excused: 0, total: 0, percentage: 0 };
    }
    
    const today = new Date().toISOString().split('T')[0];
    const todayAttendance = attendance.filter(a => a.date === today);
    const present = todayAttendance.filter(a => a.status === 'present').length;
    const absent = todayAttendance.filter(a => a.status === 'absent').length;
    const late = todayAttendance.filter(a => a.status === 'late').length;
    const excused = todayAttendance.filter(a => a.status === 'excused').length;
    const total = todayAttendance.length;
    const percentage = total > 0 ? Math.round((present / total) * 100) : 0;

    return { present, absent, late, excused, total, percentage };
  };

  const stats = getAttendanceStats();

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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Attendance Management</h1>
          <p className="text-secondary-600">Track and manage student attendance</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
        >
          Mark Attendance
        </button>
      </div>

      {/* Today's Stats */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        <div className="bg-white p-4 rounded-lg shadow-soft">
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.present}</div>
            <div className="text-sm text-secondary-600">Present</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-soft">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{stats.absent}</div>
            <div className="text-sm text-secondary-600">Absent</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-soft">
          <div className="text-center">
            <div className="text-2xl font-bold text-yellow-600">{stats.late}</div>
            <div className="text-sm text-secondary-600">Late</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-soft">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.excused}</div>
            <div className="text-sm text-secondary-600">Excused</div>
          </div>
        </div>
        <div className="bg-white p-4 rounded-lg shadow-soft">
          <div className="text-center">
            <div className="text-2xl font-bold text-primary-600">{stats.percentage}%</div>
            <div className="text-sm text-secondary-600">Attendance Rate</div>
          </div>
        </div>
      </div>

      {/* Attendance List */}
      <div className="bg-white rounded-lg shadow-soft">
        <div className="px-6 py-4 border-b border-secondary-200">
          <h3 className="text-lg font-medium text-secondary-900">Attendance Records ({attendance && attendance.length ? attendance.length : 0})</h3>
        </div>
        {loading ? (
          <div className="px-6 py-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-secondary-600">Loading attendance records...</p>
          </div>
        ) : !attendance || attendance.length === 0 ? (
          <div className="px-6 py-8 text-center">
            <p className="text-secondary-600">No attendance records found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-secondary-200">
              <thead className="bg-secondary-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Student
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Class
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Remarks
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-secondary-200">
                {attendance.map((record) => (
                  <tr key={record.id} className="hover:bg-secondary-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                      {new Date(record.date).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">
                      {getStudentName(record.student_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                      {getClassName(record.class_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(record.status)}`}>
                        {getStatusText(record.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                      {record.remarks || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEdit(record)}
                          className="text-primary-600 hover:text-primary-900"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => handleDelete(record.id)}
                          className="text-error-600 hover:text-error-900"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add/Edit Modal */}
      {showAddModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-secondary-900">
                {editingAttendance ? 'Edit Attendance' : 'Mark Attendance'}
              </h2>
              <button
                onClick={handleCloseModal}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Class
                  </label>
                  <select
                    name="class_id"
                    value={formData.class_id}
                    onChange={(e) => setFormData({...formData, class_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Class</option>
                    {classes && classes.map(classItem => (
                      <option key={classItem.id} value={classItem.id}>
                        {classItem.name}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Date
                  </label>
                  <input
                    type="date"
                    name="date"
                    value={formData.date}
                    onChange={(e) => setFormData({...formData, date: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Student
                  </label>
                  <select
                    name="student_id"
                    value={formData.student_id}
                    onChange={(e) => setFormData({...formData, student_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Student</option>
                    {students && students.map(student => (
                      <option key={student.id} value={student.id}>
                        {student.full_name} - {student.student_id}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Status
                  </label>
                  <select
                    name="status"
                    value={formData.status}
                    onChange={(e) => setFormData({...formData, status: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="present">Present</option>
                    <option value="absent">Absent</option>
                    <option value="late">Late</option>
                    <option value="excused">Excused</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Remarks
                </label>
                <textarea
                  name="remarks"
                  value={formData.remarks}
                  onChange={(e) => setFormData({...formData, remarks: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  placeholder="Optional remarks about attendance"
                />
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="px-4 py-2 border border-secondary-300 text-secondary-700 rounded-lg hover:bg-secondary-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
                >
                  {editingAttendance ? 'Update Attendance' : 'Mark Attendance'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Attendance; 