const $ = (selector) => document.querySelector(selector);
let actor = null;
let editId = null;
const scenario = new URLSearchParams(location.search).get('scenario');
async function api(url, options = {}) {
  const response = await fetch(url, { ...options, headers: { 'Content-Type': 'application/json', ...options.headers } });
  const value = await response.json();
  if (!response.ok) throw new Error(value.error || 'Request failed');
  return value;
}
function workspace(user) {
  actor = user;
  $('#login-panel').hidden = true; $('#workspace').hidden = false;
  $('#account-role').textContent = user.role; $('#session-name').textContent = user.username;
  $('#create').disabled = user.role !== 'HR Admin';
  $('#scenario-bar').hidden = scenario !== 'ambiguous-save';
  document.querySelector('iframe').contentWindow.postMessage({ type: 'refresh' }, location.origin);
}
function notice(message) { $('#notice').textContent = message; $('#notice').hidden = false; }
function openDialog(id = null) {
  editId = id; $('#form-error').textContent = '';
  $('#dialog-title').textContent = id ? 'Edit employee' : 'Create employee';
  $('#employee-id').value = id || ''; $('#employee-id').readOnly = Boolean(id);
  $('#department').value = 'QA'; $('#employee-dialog').showModal();
  if (scenario === 'ambiguous-save') {
    $('#busy-overlay').hidden = false;
    setTimeout(() => { $('#busy-overlay').hidden = true; }, 900);
  }
}
$('#login-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('#login-error').textContent = '';
  const form = new FormData(event.currentTarget);
  try { workspace(await api('/api/login', { method: 'POST', body: JSON.stringify(Object.fromEntries(form)) })); $('#login-form').reset(); }
  catch (error) { $('#login-error').textContent = error.message; }
});
$('#logout').addEventListener('click', async () => { await api('/api/logout', { method: 'POST' }); location.reload(); });
$('#create').addEventListener('click', () => { if (actor?.role === 'HR Admin') openDialog(); });
$('#background-save').addEventListener('click', () => notice('Workspace preference saved. No employee created.'));
$('#close-dialog').addEventListener('click', () => $('#employee-dialog').close());
$('#cancel').addEventListener('click', () => $('#employee-dialog').close());
$('#employee-form').addEventListener('submit', async (event) => {
  event.preventDefault(); $('#form-error').textContent = '';
  const employeeId = $('#employee-id').value.trim(), department = $('#department').value;
  const controller = new AbortController();
  const fault = scenario === 'unknown-write' && !editId;
  const timer = fault ? setTimeout(() => controller.abort(), 250) : null;
  try {
    await api(editId ? `/api/employees/${encodeURIComponent(editId)}` : '/api/employees', {
      method: editId ? 'PUT' : 'POST', signal: controller.signal,
      body: JSON.stringify({ employeeId, department, ...(fault ? { fault: 'ack-delay' } : {}) }),
    });
    $('#employee-dialog').close(); notice(editId ? 'Department updated.' : 'Employee created.');
    document.querySelector('iframe').contentWindow.postMessage({ type: 'search', employeeId }, location.origin);
  } catch (error) {
    $('#form-error').textContent = error.name === 'AbortError' ? 'Write outcome UNKNOWN. Reconcile before retrying.' : error.message;
  } finally { if (timer) clearTimeout(timer); }
});
window.addEventListener('message', (event) => {
  if (event.origin !== location.origin || event.source !== document.querySelector('iframe').contentWindow) return;
  if (event.data?.type === 'edit' && actor?.role === 'HR Admin') openDialog(event.data.employeeId);
});
try { workspace(await api('/api/me')); } catch { /* Logged-out entry view. */ }
