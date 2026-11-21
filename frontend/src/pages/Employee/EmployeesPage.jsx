import { useEffect, useState } from 'react';

export default function EmployeesPage({ user, request, onNavigate, onUserChange }) {
  const admin = user.role === 'admin';
  const [employees, setEmployees] = useState(null);
  const [selected, setSelected] = useState(null);
  const [invitation, setInvitation] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    request(admin ? '/employees' : `/employees/${user.employee_id}`, { signal: controller.signal }).then(data => {
      setEmployees(admin ? data : [data]);
      if (!admin) setSelected(data);
    }).catch(error => {
      if (error.name !== 'AbortError') { setMessage(error.message); setEmployees([]); }
    });
    return () => controller.abort();
  }, [request, admin, user.employee_id, revision]);

  async function invite(event) {
    event.preventDefault();
    const body = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true);
    setMessage('');
    try {
      setInvitation(await request('/employees', { method: 'POST', body }));
      setMessage('Employee invitation generated.');
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function save(event) {
    event.preventDefault();
    const body = Object.fromEntries(new FormData(event.currentTarget));
    setBusy(true);
    setMessage('');
    try {
      const data = await request(`/employees/${selected.employee_id}`, { method: 'PUT', body });
      if (data.employee_id === user.employee_id) onUserChange({ ...user, ...data });
      setSelected(data);
      setRevision(value => value + 1);
      setMessage('Employee username updated.');
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(employee) {
    if (!window.confirm(`Delete employee ${employee.username}? This cannot be undone.`)) return;
    setBusy(true);
    setMessage('');
    try {
      const data = await request(`/employees/${employee.employee_id}`, { method: 'DELETE' });
      if (selected?.employee_id === employee.employee_id) setSelected(null);
      setRevision(value => value + 1);
      setMessage(data.message);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>{admin ? 'Employee management' : 'My employee profile'}</h1>
      <button onClick={() => onNavigate('/employeeHome')}>Back home</button>
      <p role="status">{message}</p>
      {admin && (
        <form onSubmit={invite}>
          <fieldset disabled={busy}>
            <legend>Create employee invitation</legend>
            <label htmlFor="employeeRole">Role:</label>
            <select id="employeeRole" name="role"><option value="teller">Teller</option><option value="admin">Admin</option></select>
            <button type="submit">Generate invitation token</button>
          </fieldset>
        </form>
      )}
      {invitation && (
        <section aria-label="Employee invitation">
          <p>Invitation for role {invitation.role}. Copy the token now; it cannot be retrieved again.</p>
          <label htmlFor="employeeSetupToken">Employee setup token:</label>
          <input id="employeeSetupToken" readOnly value={invitation.setup_token} />
          <p>Expires: {new Date(invitation.expires_at).toLocaleString()}</p>
        </section>
      )}
      {selected && (
        <form key={`${selected.employee_id}-${selected.username}`} onSubmit={save}>
          <fieldset disabled={busy}>
            <legend>Edit employee {selected.employee_id}</legend>
            <label htmlFor="employeeUsername">Username:</label>
            <input id="employeeUsername" name="username" defaultValue={selected.username} maxLength={50} autoComplete="off" required />
            <button type="submit">Save username</button>
          </fieldset>
        </form>
      )}
      {employees === null ? <p>Loading employees…</p> : employees.length === 0 ? <p>No employees found.</p> : (
        <table>
          <thead><tr><th>ID</th><th>Username</th><th>Role</th><th>Actions</th></tr></thead>
          <tbody>{employees.map(employee => (
            <tr key={employee.employee_id}>
              <td>{employee.employee_id}</td><td>{employee.username}</td><td>{employee.role}</td>
              <td><button disabled={busy} onClick={() => setSelected(employee)}>Edit</button>{admin && <button disabled={busy || employee.employee_id === user.employee_id} onClick={() => remove(employee)}>Delete</button>}</td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </>
  );
}
