const publicEndpoints = new Set([
  '/auth/employees/login', '/auth/employees/register',
  '/auth/customers/login', '/auth/customers/register',
]);

export async function apiRequest(path, { sessionToken, body, ...options } = {}) {
  const headers = new Headers(options.headers);
  if (!publicEndpoints.has(path)) {
    if (!sessionToken) throw new Error('Please log in before continuing.');
    headers.set('Authorization', `Bearer ${sessionToken}`);
  }
  if (body !== undefined) headers.set('Content-Type', 'application/json');
  let response;
  try {
    response = await fetch(`/api${path}`, {
      ...options, headers,
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
    });
  } catch (error) {
    if (error.name === 'AbortError') throw error;
    throw new Error('Unable to reach the server.');
  }
  const data = await response.json().catch(error => {
    if (error.name === 'AbortError') throw error;
    return null;
  });
  if (!response.ok || data === null) {
    const error = new Error(data?.error || `Request failed (${response.status}).`);
    error.status = response.status;
    throw error;
  }
  return data;
}
