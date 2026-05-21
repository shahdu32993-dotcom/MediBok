/* ═══════════════════════════════════════
   MediBook — Main JavaScript
   ═══════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  // ── Auto-scroll chat to bottom ─────────
  const chatBody = document.getElementById('chat-body');
  if (chatBody) chatBody.scrollTop = chatBody.scrollHeight;

  // ── Doctor filter by department (book page) ──
  const deptSel = document.getElementById('dept-sel');
  const docSel  = document.getElementById('doc-sel');

  if (deptSel && docSel) {
    const allOpts = Array.from(docSel.options).slice(1);
    deptSel.addEventListener('change', () => {
      const val = deptSel.value;
      docSel.innerHTML = '<option value="">— Select Doctor —</option>';
      allOpts.forEach(o => {
        if (!val || o.dataset.dept === val) {
          docSel.appendChild(o.cloneNode(true));
        }
      });
    });
  }

  // ── Flash alerts auto-dismiss (4s) ────────
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(el => {
      el.style.transition = 'opacity .5s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 500);
    });
  }, 4000);

});
