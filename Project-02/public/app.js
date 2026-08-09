const API_BASE = '/api';

async function fetchAPI(endpoint, options = {}) {
    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        }
    });
    if (!response.ok && response.status !== 204) {
        const error = await response.json();
        throw new Error(error.error || 'Request failed');
    }
    return response.status === 204 ? null : response.json();
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => page.style.display = 'none');
    document.getElementById(pageId).style.display = 'block';
}

async function showDashboard() {
    showPage('dashboard');
    try {
        const employees = await fetchAPI('/employees');
        document.getElementById('totalEmployees').textContent = employees.length;

        const departments = new Set(employees.map(e => e.department).filter(Boolean));
        document.getElementById('totalDepartments').textContent = departments.size;

        const locations = new Set(employees.map(e => e.location).filter(Boolean));
        document.getElementById('totalLocations').textContent = locations.size;

        const recent = employees.slice(0, 5);
        const tbody = document.getElementById('recentEmployees');
        tbody.innerHTML = recent.map(emp => `
            <tr>
                <td>${emp.id}</td>
                <td>${emp.first_name} ${emp.last_name}</td>
                <td>${emp.email}</td>
                <td>${emp.job_title || '-'}</td>
                <td>${emp.department || '-'}</td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Dashboard error:', error);
    }
}

async function showEmployees() {
    showPage('employees');
    await loadEmployees();
}

async function loadEmployees() {
    try {
        const employees = await fetchAPI('/employees');
        const tbody = document.getElementById('employeeList');
        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>${emp.id}</td>
                <td>${emp.first_name} ${emp.last_name}</td>
                <td>${emp.email}</td>
                <td>${emp.job_title || '-'}</td>
                <td>${emp.department || '-'}</td>
                <td>${emp.location || '-'}</td>
                <td>
                    <button class="action-btn view" onclick="viewEmployee(${emp.id})">View</button>
                    <button class="action-btn edit" onclick="editEmployee(${emp.id})">Edit</button>
                    <button class="action-btn delete" onclick="deleteEmployee(${emp.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Load employees error:', error);
    }
}

async function searchEmployees() {
    const searchTerm = document.getElementById('searchInput').value;
    if (!searchTerm) {
        await loadEmployees();
        return;
    }
    try {
        const employees = await fetchAPI(`/employees/search?name=${encodeURIComponent(searchTerm)}`);
        const tbody = document.getElementById('employeeList');
        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>${emp.id}</td>
                <td>${emp.first_name} ${emp.last_name}</td>
                <td>${emp.email}</td>
                <td>${emp.job_title || '-'}</td>
                <td>${emp.department || '-'}</td>
                <td>${emp.location || '-'}</td>
                <td>
                    <button class="action-btn view" onclick="viewEmployee(${emp.id})">View</button>
                    <button class="action-btn edit" onclick="editEmployee(${emp.id})">Edit</button>
                    <button class="action-btn delete" onclick="deleteEmployee(${emp.id})">Delete</button>
                </td>
            </tr>
        `).join('');
    } catch (error) {
        console.error('Search error:', error);
    }
}

function clearSearch() {
    document.getElementById('searchInput').value = '';
    loadEmployees();
}

function showAddEmployee() {
    showPage('addEmployee');
    document.getElementById('addForm').reset();
}

async function addEmployee(event) {
    event.preventDefault();
    const employee = {
        firstName: document.getElementById('firstName').value,
        lastName: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value,
        jobTitle: document.getElementById('jobTitle').value,
        department: document.getElementById('department').value,
        location: document.getElementById('location').value,
        joiningDate: document.getElementById('joiningDate').value
    };
    try {
        await fetchAPI('/employees', {
            method: 'POST',
            body: JSON.stringify(employee)
        });
        showEmployees();
    } catch (error) {
        alert(error.message);
    }
}

async function editEmployee(id) {
    try {
        const emp = await fetchAPI(`/employees/${id}`);
        document.getElementById('editId').value = emp.id;
        document.getElementById('editFirstName').value = emp.first_name;
        document.getElementById('editLastName').value = emp.last_name;
        document.getElementById('editEmail').value = emp.email;
        document.getElementById('editPhone').value = emp.phone || '';
        document.getElementById('editJobTitle').value = emp.job_title || '';
        document.getElementById('editDepartment').value = emp.department || '';
        document.getElementById('editLocation').value = emp.location || '';
        document.getElementById('editJoiningDate').value = emp.joining_date || '';
        showPage('editEmployee');
    } catch (error) {
        alert(error.message);
    }
}

async function updateEmployee(event) {
    event.preventDefault();
    const id = document.getElementById('editId').value;
    const employee = {
        firstName: document.getElementById('editFirstName').value,
        lastName: document.getElementById('editLastName').value,
        email: document.getElementById('editEmail').value,
        phone: document.getElementById('editPhone').value,
        jobTitle: document.getElementById('editJobTitle').value,
        department: document.getElementById('editDepartment').value,
        location: document.getElementById('editLocation').value,
        joiningDate: document.getElementById('editJoiningDate').value
    };
    try {
        await fetchAPI(`/employees/${id}`, {
            method: 'PUT',
            body: JSON.stringify(employee)
        });
        showEmployees();
    } catch (error) {
        alert(error.message);
    }
}

async function deleteEmployee(id) {
    if (!confirm('Are you sure you want to delete this employee?')) return;
    try {
        await fetchAPI(`/employees/${id}`, { method: 'DELETE' });
        await loadEmployees();
    } catch (error) {
        alert(error.message);
    }
}

async function viewEmployee(id) {
    try {
        const emp = await fetchAPI(`/employees/${id}`);
        const content = document.getElementById('detailsContent');
        content.innerHTML = `
            <p><strong>ID:</strong> ${emp.id}</p>
            <p><strong>Name:</strong> ${emp.first_name} ${emp.last_name}</p>
            <p><strong>Email:</strong> ${emp.email}</p>
            <p><strong>Phone:</strong> ${emp.phone || '-'}</p>
            <p><strong>Job Title:</strong> ${emp.job_title || '-'}</p>
            <p><strong>Department:</strong> ${emp.department || '-'}</p>
            <p><strong>Location:</strong> ${emp.location || '-'}</p>
            <p><strong>Joining Date:</strong> ${emp.joining_date || '-'}</p>
            <p><strong>Created:</strong> ${emp.created_at || '-'}</p>
            <p><strong>Updated:</strong> ${emp.updated_at || '-'}</p>
        `;
        showPage('employeeDetails');
    } catch (error) {
        alert(error.message);
    }
}

showDashboard();