import React, { useState, useEffect } from 'react';
import { 
  teacherAPI, 
  teacherAssignmentAPI, 
  examinationMarkAPI, 
  resultFormulaAPI,
  studentAPI,
  subjectAPI,
  classAPI,
  handleApiError 
} from '../services/api';
import toast from 'react-hot-toast';

const Teachers = () => {
  const [teachers, setTeachers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTeacher, setEditingTeacher] = useState(null);
  
  // New state for enhanced features
  const [selectedTeacher, setSelectedTeacher] = useState(null);
  const [teacherAssignments, setTeacherAssignments] = useState([]);
  const [examinationMarks, setExaminationMarks] = useState([]);
  const [resultFormulas, setResultFormulas] = useState([]);
  const [students, setStudents] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [classes, setClasses] = useState([]);
  const [showAssignmentsModal, setShowAssignmentsModal] = useState(false);
  const [showMarksModal, setShowMarksModal] = useState(false);
  const [showFormulasModal, setShowFormulasModal] = useState(false);
  
  // Form states
  const [assignmentForm, setAssignmentForm] = useState({
    teacher_id: '',
    subject_id: '',
    class_id: '',
    academic_year: '',
    term: ''
  });
  
  const [markForm, setMarkForm] = useState({
    assignment_id: '',
    student_id: '',
    test_type: '',
    test_date: '',
    score: '',
    max_score: '100',
    weight: '1.0',
    remarks: ''
  });
  
  const [formulaForm, setFormulaForm] = useState({
    name: '',
    description: '',
    formula: '',
    is_active: true
  });

  const [formData, setFormData] = useState({
    employee_id: '',
    full_name: '',
    department: '',
    qualification: '',
    phone: '',
    address: ''
  });

  useEffect(() => {
    fetchTeachers();
    fetchSupportingData();
  }, []);

  const fetchSupportingData = async () => {
    try {
      const [studentsRes, subjectsRes, classesRes, formulasRes] = await Promise.all([
        studentAPI.getStudents(),
        subjectAPI.getSubjects(),
        classAPI.getClasses(),
        resultFormulaAPI.getResultFormulas()
      ]);
      
      // Handle the API wrapper response structure
      setStudents(studentsRes.success ? (studentsRes.data || []) : []);
      setSubjects(subjectsRes.success ? (subjectsRes.data || []) : []);
      setClasses(classesRes.success ? (classesRes.data || []) : []);
      setResultFormulas(formulasRes.success ? (formulasRes.data || []) : []);
    } catch (error) {
      console.error('Error fetching supporting data:', error);
      // Set empty arrays on error to prevent null issues
      setStudents([]);
      setSubjects([]);
      setClasses([]);
      setResultFormulas([]);
    }
  };

  const fetchTeachers = async () => {
    try {
      setLoading(true);
      const response = await teacherAPI.getTeachers();
      // Handle the API wrapper response structure
      if (response.success) {
        setTeachers(response.data || []);
      } else {
        toast.error(response.error?.message || 'Failed to fetch teachers');
        setTeachers([]);
      }
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
      // Set empty array on error to prevent null issues
      setTeachers([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      if (editingTeacher) {
        await teacherAPI.updateTeacher(editingTeacher.id, formData);
        toast.success('Teacher updated successfully');
      } else {
        await teacherAPI.createTeacher(formData);
        toast.success('Teacher added successfully');
      }
      
      setShowAddModal(false);
      setEditingTeacher(null);
      resetForm();
      fetchTeachers();
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
  };

  const handleEdit = (teacher) => {
    setEditingTeacher(teacher);
    setFormData({
      employee_id: teacher.employee_id,
      full_name: teacher.full_name,
      department: teacher.department,
      qualification: teacher.qualification,
      phone: teacher.phone,
      address: teacher.address
    });
    setShowAddModal(true);
  };

  const handleDelete = async (teacherId) => {
    if (window.confirm('Are you sure you want to delete this teacher?')) {
      try {
        await teacherAPI.deleteTeacher(teacherId);
        toast.success('Teacher deleted successfully');
        fetchTeachers();
      } catch (error) {
        const errorData = handleApiError(error);
        toast.error(errorData.message);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      employee_id: '',
      full_name: '',
      department: '',
      qualification: '',
      phone: '',
      address: ''
    });
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
    setEditingTeacher(null);
    resetForm();
  };

  // Enhanced teacher functions
  const handleViewAssignments = async (teacher) => {
    setSelectedTeacher(teacher);
    try {
      const response = await teacherAssignmentAPI.getTeacherAssignments({ teacher_id: teacher.id });
      setTeacherAssignments(response.data);
      setShowAssignmentsModal(true);
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
  };

  const handleViewMarks = async (teacher) => {
    setSelectedTeacher(teacher);
    try {
      const response = await examinationMarkAPI.getExaminationMarks();
      // Filter marks for this teacher's assignments
      const teacherAssignments = await teacherAssignmentAPI.getTeacherAssignments({ teacher_id: teacher.id });
      const assignmentIds = teacherAssignments.data.map(assignment => assignment.id);
      const teacherMarks = response.data.filter(mark => assignmentIds.includes(mark.assignment_id));
      setExaminationMarks(teacherMarks);
      setShowMarksModal(true);
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
  };

  const handleCreateAssignment = async (e) => {
    e.preventDefault();
    try {
      const assignmentData = {
        ...assignmentForm,
        teacher_id: selectedTeacher.id
      };
      await teacherAssignmentAPI.createTeacherAssignment(assignmentData);
      toast.success('Assignment created successfully');
      setShowAssignmentsModal(false);
      setAssignmentForm({
        teacher_id: '',
        subject_id: '',
        class_id: '',
        academic_year: '',
        term: ''
      });
      // Refresh assignments
      if (selectedTeacher) {
        const response = await teacherAssignmentAPI.getTeacherAssignments({ teacher_id: selectedTeacher.id });
        setTeacherAssignments(response.data);
      }
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
  };

  const handleCreateMark = async (e) => {
    e.preventDefault();
    try {
      const markData = {
        ...markForm,
        score: parseFloat(markForm.score),
        max_score: parseFloat(markForm.max_score),
        weight: parseFloat(markForm.weight),
        test_date: new Date(markForm.test_date).toISOString().split('T')[0]
      };
      await examinationMarkAPI.createExaminationMark(markData);
      toast.success('Examination mark created successfully');
      setShowMarksModal(false);
      setMarkForm({
        assignment_id: '',
        student_id: '',
        test_type: '',
        test_date: '',
        score: '',
        max_score: '100',
        weight: '1.0',
        remarks: ''
      });
      // Refresh marks
      if (selectedTeacher) {
        const response = await examinationMarkAPI.getExaminationMarks();
        const teacherAssignments = await teacherAssignmentAPI.getTeacherAssignments({ teacher_id: selectedTeacher.id });
        const assignmentIds = teacherAssignments.data.map(assignment => assignment.id);
        const teacherMarks = response.data.filter(mark => assignmentIds.includes(mark.assignment_id));
        setExaminationMarks(teacherMarks);
      }
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
  };

  const handleCreateFormula = async (e) => {
    e.preventDefault();
    try {
      await resultFormulaAPI.createResultFormula(formulaForm);
      toast.success('Result formula created successfully');
      setShowFormulasModal(false);
      setFormulaForm({
        name: '',
        description: '',
        formula: '',
        is_active: true
      });
      // Refresh formulas
      const response = await resultFormulaAPI.getResultFormulas();
      setResultFormulas(response.data);
    } catch (error) {
      const errorData = handleApiError(error);
      toast.error(errorData.message);
    }
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
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-secondary-900">Teacher Management</h1>
          <p className="text-secondary-600">Manage teacher information, assignments, and examination marks</p>
        </div>
        <div className="flex space-x-3">
          <button
            onClick={() => setShowFormulasModal(true)}
            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
          >
            Result Formulas
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Add Teacher
          </button>
        </div>
      </div>

      {/* Teachers List */}
      <div className="bg-white rounded-lg shadow-soft">
        <div className="px-6 py-4 border-b border-secondary-200">
          <h3 className="text-lg font-medium text-secondary-900">
            Teachers ({teachers && teachers.length ? teachers.length : 0})
          </h3>
        </div>
        
        {loading ? (
          <div className="px-6 py-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-2 text-secondary-600">Loading teachers...</p>
          </div>
        ) : !teachers || teachers.length === 0 ? (
          <div className="px-6 py-8 text-center">
            <p className="text-secondary-600">No teachers found.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-secondary-200">
              <thead className="bg-secondary-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Employee ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Department
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Qualification
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Phone
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Actions
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">
                    Teaching
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-secondary-200">
                {teachers && teachers.map((teacher) => (
                <tr key={teacher.id} className="hover:bg-secondary-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">
                    {teacher.employee_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                    {teacher.full_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    {teacher.department}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    {teacher.qualification}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">
                    {teacher.phone}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleEdit(teacher)}
                        className="text-primary-600 hover:text-primary-900"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(teacher.id)}
                        className="text-error-600 hover:text-error-900"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewAssignments(teacher)}
                        className="text-blue-600 hover:text-blue-900 text-xs"
                      >
                        Assignments
                      </button>
                      <button
                        onClick={() => handleViewMarks(teacher)}
                        className="text-green-600 hover:text-green-900 text-xs"
                      >
                        Marks
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
                {editingTeacher ? 'Edit Teacher' : 'Add New Teacher'}
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
                    Employee ID
                  </label>
                  <input
                    type="text"
                    name="employee_id"
                    value={formData.employee_id}
                    onChange={(e) => setFormData({...formData, employee_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Full Name
                  </label>
                  <input
                    type="text"
                    name="full_name"
                    value={formData.full_name}
                    onChange={(e) => setFormData({...formData, full_name: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Department
                  </label>
                  <select
                    name="department"
                    value={formData.department}
                    onChange={(e) => setFormData({...formData, department: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Department</option>
                    <option value="Mathematics">Mathematics</option>
                    <option value="Theology">Theology</option>
                    <option value="English">English</option>
                    <option value="Science">Science</option>
                    <option value="History">History</option>
                    <option value="Geography">Geography</option>
                    <option value="Languages">Languages</option>
                    <option value="Physical Education">Physical Education</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Qualification
                  </label>
                  <input
                    type="text"
                    name="qualification"
                    value={formData.qualification}
                    onChange={(e) => setFormData({...formData, qualification: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                    placeholder="e.g., MSc Mathematics, PhD Theology"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">
                    Phone
                  </label>
                  <input
                    type="tel"
                    name="phone"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-1">
                  Address
                </label>
                <textarea
                  name="address"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  rows={3}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
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
                  {editingTeacher ? 'Update Teacher' : 'Add Teacher'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Teacher Assignments Modal */}
      {showAssignmentsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-secondary-900">
                Teacher Assignments - {selectedTeacher?.full_name}
              </h2>
              <button
                onClick={() => setShowAssignmentsModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Create Assignment Form */}
            <div className="mb-6 p-4 bg-secondary-50 rounded-lg">
              <h3 className="text-lg font-medium text-secondary-900 mb-3">Create New Assignment</h3>
              <form onSubmit={handleCreateAssignment} className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Subject</label>
                  <select
                    value={assignmentForm.subject_id}
                    onChange={(e) => setAssignmentForm({...assignmentForm, subject_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Subject</option>
                    {subjects.map(subject => (
                      <option key={subject.id} value={subject.id}>{subject.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Class</label>
                  <select
                    value={assignmentForm.class_id}
                    onChange={(e) => setAssignmentForm({...assignmentForm, class_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Class</option>
                    {classes.map(cls => (
                      <option key={cls.id} value={cls.id}>{cls.name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Academic Year</label>
                  <input
                    type="text"
                    value={assignmentForm.academic_year}
                    onChange={(e) => setAssignmentForm({...assignmentForm, academic_year: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="e.g., 2024-2025"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Term</label>
                  <select
                    value={assignmentForm.term}
                    onChange={(e) => setAssignmentForm({...assignmentForm, term: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Term</option>
                    <option value="First Term">First Term</option>
                    <option value="Second Term">Second Term</option>
                    <option value="Third Term">Third Term</option>
                    <option value="Final">Final</option>
                  </select>
                </div>
                <div className="md:col-span-2 flex items-end">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                  >
                    Create Assignment
                  </button>
                </div>
              </form>
            </div>

            {/* Assignments Table */}
            <div className="bg-white rounded-lg shadow-soft">
              <div className="px-6 py-4 border-b border-secondary-200">
                <h3 className="text-lg font-medium text-secondary-900">Current Assignments ({teacherAssignments.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-secondary-200">
                  <thead className="bg-secondary-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Subject</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Class</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Academic Year</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Term</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Status</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-secondary-200">
                    {teacherAssignments.map((assignment) => (
                      <tr key={assignment.id} className="hover:bg-secondary-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">{assignment.subject_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">{assignment.class_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{assignment.academic_year}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{assignment.term}</td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            assignment.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {assignment.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Examination Marks Modal */}
      {showMarksModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-6xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-secondary-900">
                Examination Marks - {selectedTeacher?.full_name}
              </h2>
              <button
                onClick={() => setShowMarksModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Create Mark Form */}
            <div className="mb-6 p-4 bg-secondary-50 rounded-lg">
              <h3 className="text-lg font-medium text-secondary-900 mb-3">Enter New Examination Mark</h3>
              <form onSubmit={handleCreateMark} className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Assignment</label>
                  <select
                    value={markForm.assignment_id}
                    onChange={(e) => setMarkForm({...markForm, assignment_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Assignment</option>
                    {teacherAssignments.map(assignment => (
                      <option key={assignment.id} value={assignment.id}>
                        {assignment.subject_name} - {assignment.class_name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Student</label>
                  <select
                    value={markForm.student_id}
                    onChange={(e) => setMarkForm({...markForm, student_id: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Student</option>
                    {students.map(student => (
                      <option key={student.id} value={student.id}>{student.full_name}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Test Type</label>
                  <select
                    value={markForm.test_type}
                    onChange={(e) => setMarkForm({...markForm, test_type: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  >
                    <option value="">Select Type</option>
                    <option value="Mid-term">Mid-term</option>
                    <option value="End-term">End-term</option>
                    <option value="Final">Final</option>
                    <option value="Assignment">Assignment</option>
                    <option value="Quiz">Quiz</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Test Date</label>
                  <input
                    type="date"
                    value={markForm.test_date}
                    onChange={(e) => setMarkForm({...markForm, test_date: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Score</label>
                  <input
                    type="number"
                    step="0.1"
                    value={markForm.score}
                    onChange={(e) => setMarkForm({...markForm, score: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="0.0"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Max Score</label>
                  <input
                    type="number"
                    step="0.1"
                    value={markForm.max_score}
                    onChange={(e) => setMarkForm({...markForm, max_score: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="100"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Weight</label>
                  <input
                    type="number"
                    step="0.1"
                    value={markForm.weight}
                    onChange={(e) => setMarkForm({...markForm, weight: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="1.0"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Remarks</label>
                  <input
                    type="text"
                    value={markForm.remarks}
                    onChange={(e) => setMarkForm({...markForm, remarks: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Optional remarks"
                  />
                </div>
                <div className="md:col-span-4 flex justify-end">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Enter Mark
                  </button>
                </div>
              </form>
            </div>

            {/* Marks Table */}
            <div className="bg-white rounded-lg shadow-soft">
              <div className="px-6 py-4 border-b border-secondary-200">
                <h3 className="text-lg font-medium text-secondary-900">Examination Marks ({examinationMarks.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-secondary-200">
                  <thead className="bg-secondary-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Student</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Subject</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Test Type</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Score</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Weight</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Remarks</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-secondary-200">
                    {examinationMarks.map((mark) => (
                      <tr key={mark.id} className="hover:bg-secondary-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">{mark.student_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">{mark.subject_name}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{mark.test_type}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{mark.test_date}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-900">
                          {mark.score}/{mark.max_score}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{mark.weight}</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{mark.remarks || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Result Formulas Modal */}
      {showFormulasModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold text-secondary-900">Result Formulas Management</h2>
              <button
                onClick={() => setShowFormulasModal(false)}
                className="text-secondary-400 hover:text-secondary-600"
              >
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Create Formula Form */}
            <div className="mb-6 p-4 bg-secondary-50 rounded-lg">
              <h3 className="text-lg font-medium text-secondary-900 mb-3">Create New Result Formula</h3>
              <form onSubmit={handleCreateFormula} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">Formula Name</label>
                    <input
                      type="text"
                      value={formulaForm.name}
                      onChange={(e) => setFormulaForm({...formulaForm, name: e.target.value})}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      placeholder="e.g., Standard Formula"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-secondary-700 mb-1">Active</label>
                    <select
                      value={formulaForm.is_active}
                      onChange={(e) => setFormulaForm({...formulaForm, is_active: e.target.value === 'true'})}
                      className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                      required
                    >
                      <option value="true">Active</option>
                      <option value="false">Inactive</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Description</label>
                  <input
                    type="text"
                    value={formulaForm.description}
                    onChange={(e) => setFormulaForm({...formulaForm, description: e.target.value})}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder="Brief description of the formula"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-1">Formula (JSON)</label>
                  <textarea
                    value={formulaForm.formula}
                    onChange={(e) => setFormulaForm({...formulaForm, formula: e.target.value})}
                    rows={4}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
                    placeholder='{"midterm_weight": 0.3, "endterm_weight": 0.7, "passing_score": 50}'
                    required
                  />
                </div>
                <div className="flex justify-end">
                  <button
                    type="submit"
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                  >
                    Create Formula
                  </button>
                </div>
              </form>
            </div>

            {/* Formulas Table */}
            <div className="bg-white rounded-lg shadow-soft">
              <div className="px-6 py-4 border-b border-secondary-200">
                <h3 className="text-lg font-medium text-secondary-900">Result Formulas ({resultFormulas.length})</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-secondary-200">
                  <thead className="bg-secondary-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Name</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Description</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Formula</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Status</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-secondary-500 uppercase tracking-wider">Created By</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-secondary-200">
                    {resultFormulas.map((formula) => (
                      <tr key={formula.id} className="hover:bg-secondary-50">
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-secondary-900">{formula.name}</td>
                        <td className="px-6 py-4 text-sm text-secondary-500">{formula.description}</td>
                        <td className="px-6 py-4 text-sm text-secondary-500">
                          <code className="bg-secondary-100 px-2 py-1 rounded text-xs">{formula.formula}</code>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                            formula.is_active 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {formula.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-500">{formula.created_by_name}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Teachers; 