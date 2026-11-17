const $ = selector => document.querySelector(selector);
const escapeHtml = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
let state, filter = 'all', busy = false, timer;

async function api(path,data) {
  let response;
  try { response = await fetch(path,data === undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)}); }
  catch { throw new Error('The local grade manager is offline. Start its server and refresh.'); }
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'The class could not be updated.');
  return result;
}

function toast(message,error = false) {
  clearTimeout(timer); $('#toast').textContent = message; $('#toast').className = error ? 'error' : ''; $('#toast').hidden = false; AppUI.feedback('#toast');
  timer = setTimeout(() => { $('#toast').hidden = true; },7000);
}

function render() {
  const count = state.records.length;
  $('#nav-count').textContent = count;
  $('#student-count').innerHTML = `${count}<span> / 30</span>`;
  $('#class-average').innerHTML = count ? `${state.average.toFixed(1)}<span> / 100</span>` : '—';
  $('#pass-rate').innerHTML = count ? `${Math.round(state.passed / count * 100)}<span>%</span>` : '—';
  $('#pass-description').textContent = count ? `${state.passed} passing · ${state.failed} below 50` : 'Add records to see performance.';
  $('#record-summary').textContent = `${count} student ${count === 1 ? 'record' : 'records'}`;
  $('#capacity-note').textContent = `${30-count} ${30-count === 1 ? 'place' : 'places'} available`;
  $('#add-student').disabled = count >= 30;
  const query = $('#search').value.trim().toLocaleLowerCase();
  const visible = state.records.filter(record => `${record.name} ${record.id}`.toLocaleLowerCase().includes(query) && (filter === 'all' || (filter === 'pass' ? record.grade !== 'F' : record.grade === 'F')));
  if (!visible.length) {
    $('#records').innerHTML = `<div class="empty"><span>▤</span><h3>${count ? 'No matching records.' : 'A fresh page for your class.'}</h3><p>${count ? 'Try another name, ID, or result filter.' : 'Add your first student, or load the fictional sample class to explore.'}</p></div>`;
  } else {
    $('#records').innerHTML = `<div class="table-scroll"><table><thead><tr><th>Student</th><th>Quiz <small>/20</small></th><th>Mid-sem <small>/30</small></th><th>Exam <small>/50</small></th><th>Total</th><th>Grade</th><th>Actions</th></tr></thead><tbody>${visible.map(record => `<tr><td><span class="student-avatar">${escapeHtml(record.name[0].toUpperCase())}</span><span><strong>${escapeHtml(record.name)}</strong><small>ID ${record.id}</small></span></td><td>${record.quiz}</td><td>${record.mid}</td><td>${record.exam}</td><td class="total">${record.total.toFixed(1)}</td><td><span class="grade grade-${record.grade}">${record.grade}</span></td><td><div class="row-actions"><button data-edit="${record.id}" aria-label="Edit ${escapeHtml(record.name)}">Edit ↗</button><button data-delete="${record.id}" aria-label="Remove ${escapeHtml(record.name)}">Remove</button></div></td></tr>`).join('')}</tbody></table></div>`;
    document.querySelectorAll('[data-edit]').forEach(button => button.onclick = () => openStudent(state.records.find(record => record.id === Number(button.dataset.edit))));
    document.querySelectorAll('[data-delete]').forEach(button => button.onclick = () => {
      const record = state.records.find(item => item.id === Number(button.dataset.delete));
      if (confirm(`Remove ${record.name} from this local class?`)) action('/api/delete',{id:String(record.id)},button);
    });
  }
  $('#distribution').innerHTML = ['A','B','C','D','F'].map(grade => {
    const number = state.records.filter(record => record.grade === grade).length;
    return `<div class="distribution-row"><span class="grade grade-${grade}">${grade}</span><meter class="meter-${grade}" min="0" max="${Math.max(count,1)}" value="${number}" aria-label="Grade ${grade}: ${number} students"></meter><strong>${number}</strong></div>`;
  }).join('');
  const high = state.records.find(record => record.id === state.highest_id), low = state.records.find(record => record.id === state.lowest_id);
  $('#highest-score').innerHTML = high ? `${high.total.toFixed(1)}<span> / 100</span>` : '—';
  $('#lowest-score').innerHTML = low ? `${low.total.toFixed(1)}<span> / 100</span>` : '—';
  $('#highest-name').textContent = high ? high.name : 'Your class is waiting.';
  $('#lowest-name').textContent = low ? low.name : 'Add a student to begin.';
}

function openStudent(record) {
  const form = $('#student-form'); form.reset(); $('#form-error').textContent = '';
  $('#dialog-title').textContent = record ? 'A record, refined.' : 'Add a student.';
  $('#save-student').textContent = record ? 'Save changes ↗' : 'Save student ↗';
  form.elements.original_id.value = record ? String(record.id) : '';
  if (record) ['name','id','quiz','mid','exam'].forEach(key => { form.elements[key].value = record[key]; });
  $('#student-dialog').showModal(); AppUI.reveal('#student-dialog .identity-fields,#student-dialog .score-fields');
}

async function action(path,data,button) {
  if (busy) return false;
  busy = true; if (button) button.disabled = true; $('#form-error').textContent = '';
  try {
    const result = await api(path,data); state = result.state; render(); AppUI.feedback('.summary-card'); AppUI.reveal('#records tbody tr'); toast(result.message); return true;
  } catch (error) {
    if ($('#student-dialog').open) $('#form-error').textContent = error.message;
    else toast(error.message,true);
    return false;
  } finally { busy = false; if (button?.isConnected) button.disabled = false; }
}

$('#add-student').onclick = () => openStudent();
$('#close-dialog').onclick = () => $('#student-dialog').close();
$('#student-form').onsubmit = async event => { event.preventDefault(); if (await action('/api/student',Object.fromEntries(new FormData(event.target)),$('#save-student'))) $('#student-dialog').close(); };
$('#load-sample').onclick = () => { if (!state || busy) return; if (!state.records.length || confirm('Replace this session’s current records with the fictional sample class?')) action('/api/sample',{replace:true},$('#load-sample')); };
$('#search').oninput = () => state && render();
document.querySelectorAll('[data-filter]').forEach(button => button.onclick = () => {
  filter = button.dataset.filter; document.querySelectorAll('[data-filter]').forEach(item => { item.classList.toggle('active',item === button); item.setAttribute('aria-pressed',String(item === button)); }); render();
});
document.querySelectorAll('nav a').forEach(link => link.onclick = () => { document.querySelectorAll('nav a').forEach(item => item.classList.toggle('active',item === link)); });
api('/api/state').then(result => { state = result; render(); }).catch(error => toast(error.message,true));
