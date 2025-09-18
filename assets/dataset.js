document.addEventListener('DOMContentLoaded', () => {
  const search = document.querySelector('#varSearch');
  const table = document.querySelector('table[data-kind="vars"]');
  if (!table || !search) return;

  const rows = Array.from(table.tBodies[0].rows);

  // 搜索过滤
  search.addEventListener('input', () => {
    const q = search.value.trim().toLowerCase();
    rows.forEach(tr => {
      const text = tr.innerText.toLowerCase();
      tr.style.display = text.includes(q) ? '' : 'none';
    });
  });

  // 简单排序（点击可排序）
  table.querySelectorAll('th.sortable').forEach((th, idx) => {
    let asc = true;
    th.addEventListener('click', () => {
      const sorted = rows.slice().sort((a, b) => {
        const A = a.cells[idx].innerText.trim().toLowerCase();
        const B = b.cells[idx].innerText.trim().toLowerCase();
        if (!isNaN(parseFloat(A)) && !isNaN(parseFloat(B))) {
          return asc ? (parseFloat(A) - parseFloat(B)) : (parseFloat(B) - parseFloat(A));
        }
        return asc ? A.localeCompare(B) : B.localeCompare(A);
      });
      asc = !asc;
      const tbody = table.tBodies[0];
      sorted.forEach(tr => tbody.appendChild(tr));
    });
  });
});
