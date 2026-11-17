import { useEffect, useState } from 'react';

export default function CustomersPage({ request, onNavigate }) {
  const [customers, setCustomers] = useState(null);
  const [selected, setSelected] = useState(null);
  const [setup, setSetup] = useState(null);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);
  const [revision, setRevision] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    request('/customers', { signal: controller.signal }).then(setCustomers).catch(error => {
      if (error.name !== 'AbortError') { setMessage(error.message); setCustomers([]); }
    });
    return () => controller.abort();
  }, [request, revision]);

  async function save(event) {
    event.preventDefault();
    const form = event.currentTarget;
    const body = Object.fromEntries(new FormData(form));
    if (selected && !body.ssn) delete body.ssn;
    setBusy(true);
    setMessage('');
    try {
      const data = await request(selected ? `/customers/${selected.customer_id}` : '/customers', {
        method: selected ? 'PATCH' : 'POST', body,
      });
      if (data.setup_token) setSetup(data);
      setMessage(selected ? 'Customer updated.' : data.message);
      setSelected(null);
      form.reset();
      setRevision(value => value + 1);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  async function remove(customer) {
    if (!window.confirm(`Delete customer ${customer.customer_id}? This cannot be undone.`)) return;
    setBusy(true);
    setMessage('');
    try {
      const data = await request(`/customers/${customer.customer_id}`, { method: 'DELETE' });
      if (selected?.customer_id === customer.customer_id) setSelected(null);
      if (setup?.customer.customer_id === customer.customer_id) setSetup(null);
      setMessage(data.message);
      setRevision(value => value + 1);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Customers</h1>
      <button onClick={() => onNavigate('/employeeHome')}>Back home</button>
      <p role="status">{message}</p>
      {setup && (
        <section aria-label="Customer setup token">
          <p>Setup token for customer {setup.customer.customer_id} ({setup.customer.email}). Copy it now; it cannot be retrieved again.</p>
          <label htmlFor="customerSetupToken">Customer setup token:</label>
          <input id="customerSetupToken" readOnly value={setup.setup_token} />
          <p>Expires: {new Date(setup.expires_at).toLocaleString()}</p>
        </section>
      )}
      <h2>{selected ? `Edit customer ${selected.customer_id}` : 'Create customer and setup token'}</h2>
      <form key={selected?.customer_id ?? 'new'} onSubmit={save}>
        <fieldset disabled={busy}>
          <label htmlFor="firstName">First name:</label>
          <input id="firstName" name="first_name" maxLength={100} defaultValue={selected?.first_name ?? ''} required />
          <label htmlFor="lastName">Last name:</label>
          <input id="lastName" name="last_name" maxLength={100} defaultValue={selected?.last_name ?? ''} required /><br /><br />
          <label htmlFor="ssn">{selected ? 'New SSN (leave blank to keep existing)' : 'SSN (XXX-XX-XXXX)'}:</label>
          <input id="ssn" name="ssn" pattern="[0-9]{3}-[0-9]{2}-[0-9]{4}" maxLength={11} required={!selected} autoComplete="off" />
          <label htmlFor="customerEmail">Email:</label>
          <input id="customerEmail" name="email" type="email" maxLength={255} defaultValue={selected?.email ?? ''} required /><br /><br />
          <button type="submit">{selected ? 'Save customer' : 'Create customer'}</button>
          {selected && <button type="button" onClick={() => setSelected(null)}>Cancel editing</button>}
        </fieldset>
      </form>
      {customers === null ? <p>Loading customers…</p> : customers.length === 0 ? <p>No customers found.</p> : (
        <table>
          <thead><tr><th>ID</th><th>Name</th><th>Email</th><th>SSN</th><th>Actions</th></tr></thead>
          <tbody>{customers.map(customer => (
            <tr key={customer.customer_id}>
              <td>{customer.customer_id}</td><td>{customer.first_name} {customer.last_name}</td><td>{customer.email}</td><td>{customer.ssn}</td>
              <td><button disabled={busy} onClick={() => setSelected(customer)}>Edit</button><button disabled={busy} onClick={() => remove(customer)}>Delete</button></td>
            </tr>
          ))}</tbody>
        </table>
      )}
    </>
  );
}
