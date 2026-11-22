import { useState } from 'react';

const searchTypes = [
  { key: 'customers', label: 'Customers', parameter: 'name', searchField: 'first_name' },
  { key: 'accounts', label: 'Accounts', parameter: 'name', searchField: 'account_number' },
  { key: 'employees', label: 'Employees', parameter: 'name', searchField: 'username' },
];

export default function DemoSearchPage({ request, onNavigate }) {
  const [activeType, setActiveType] = useState(searchTypes[0]);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [message, setMessage] = useState('');
  const [busy, setBusy] = useState(false);

  async function search(event) {
    event.preventDefault();
    setBusy(true);
    setMessage('');
    setResults([]);
    try {
      const data = await request(
        `/${activeType.key}/vulnerable/search?${activeType.parameter}=${encodeURIComponent(query.trim())}`
      );
      setResults(data);
      setMessage(data.length === 0 ? 'No matching records found.' : `${data.length} record(s) returned.`);
    } catch (error) {
      setMessage(error.message);
    } finally {
      setBusy(false);
    }
  }

  function selectType(type) {
    setActiveType(type);
    setQuery('');
    setResults([]);
    setMessage('');
  }

  return (
    <>
      <h1>Database demo search</h1>
      <button onClick={() => onNavigate('/employeeHome')}>Back home</button>
      <fieldset>
        <legend>Search type</legend>
        {searchTypes.map(type => (
          <label key={type.key}>
            <input
              type="radio"
              name="searchType"
              checked={activeType.key === type.key}
              onChange={() => selectType(type)}
            />
            {type.label}
          </label>
        ))}
      </fieldset>
      <form onSubmit={search}>
        <fieldset disabled={busy}>
          <label htmlFor="demoSearch">Search value:</label>
          <input
            id="demoSearch"
            value={query}
            onChange={event => setQuery(event.target.value)}
            placeholder={activeType.searchField}
            required
          />
          <button type="submit">Search</button>
        </fieldset>
      </form>
      <p role="status">{busy ? 'Searching…' : message}</p>
      {results.length > 0 && (
        <table>
          <thead>
            <tr>{Object.keys(results[0]).map(key => <th key={key}>{key}</th>)}</tr>
          </thead>
          <tbody>
            {results.map((row, index) => (
              <tr key={Object.values(row).join('-') || index}>
                {Object.values(row).map((value, columnIndex) => (
                  <td key={columnIndex}>{String(value)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </>
  );
}
