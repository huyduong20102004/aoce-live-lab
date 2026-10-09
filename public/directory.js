const $ = (selector) => document.querySelector(selector);
let role = null;
async function refresh() {
  $('#directory-error').textContent = '';
  try {
    const me = await fetch('/api/me');
    if (!me.ok) return;
    role = (await me.json()).role;
    const response = await fetch(`/api/employees?id=${encodeURIComponent($('#search-id').value.trim())}`);
    if (!response.ok) throw new Error('Cannot load directory');
    const result = await response.json(); $('#rows').replaceChildren();
    for (const record of result.records) {
      const row = document.createElement('tr');
      for (const text of [record.employeeId, record.department, record.owner ? 'Lab owned' : 'Local record']) {
        const cell = document.createElement('td'); cell.textContent = text; row.append(cell);
      }
      const actions = document.createElement('td'); const edit = document.createElement('button');
      edit.textContent = 'Edit'; edit.disabled = role !== 'HR Admin';
      edit.addEventListener('click', () => parent.postMessage({ type: 'edit', employeeId: record.employeeId }, location.origin));
      actions.append(edit); row.append(actions); $('#rows').append(row);
    }
    $('#empty').hidden = result.records.length > 0;
    $('#search-state').textContent = `${result.total} record${result.total === 1 ? '' : 's'}${result.total > 20 ? ' · Showing first 20. Search exact ID to locate another record.' : ''}`;
  } catch (error) { $('#directory-error').textContent = error.message; }
}
$('#search-form').addEventListener('submit', (event) => { event.preventDefault(); refresh(); });
$('#clear-search').addEventListener('click', () => { $('#search-id').value = ''; refresh(); });
window.addEventListener('message', (event) => {
  if (event.origin !== location.origin || event.source !== parent) return;
  if (event.data?.type === 'search') $('#search-id').value = event.data.employeeId;
  if (event.data?.type === 'refresh' || event.data?.type === 'search') refresh();
});
refresh();
