async function loadJSON(url){ const r=await fetch(url); if(!r.ok) throw new Error('加载失败'); return r.json(); }

document.addEventListener('DOMContentLoaded', async () => {
  const [site, datasets] = await Promise.all([
    loadJSON('data/site.json'),
    loadJSON('data/datasets.json')
  ]);
  document.querySelector('#brand').textContent = site.site_title;
  document.querySelector('#footerMeta').textContent = `© ${new Date().getFullYear()} ${site.owner}`;
  const email = site.contact_email || 'data-admin@example.edu';
  const emailLink = document.querySelector('#contactEmail');
  emailLink.textContent = email;
  emailLink.href = `mailto:${email}`;

  // 数据集多选
  const wrap = document.querySelector('#datasetChecks');
  datasets.forEach(d => {
    const id = `ds-${d.slug}`;
    const label = document.createElement('label');
    label.innerHTML = `<input type="checkbox" value="${d.slug}" /> ${d.title}`;
    wrap.appendChild(label);
  });

  // 生成邮件
  const form = document.querySelector('#applyForm');
  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    const selected = Array.from(wrap.querySelectorAll('input[type="checkbox"]:checked')).map(x => x.value);
    if (!selected.length) { alert('请至少选择一个数据集'); return; }
    if (!data.agree) { alert('请勾选同意条款'); return; }

    const subject = `[数据申请] ${data.name} - ${selected.join(', ')}`;
    const body = [
      `姓名：${data.name}`,
      `单位/院系：${data.org}`,
      `邮箱：${data.email}`,
      `申请数据集：${selected.join(', ')}`,
      '',
      `用途说明：`,
      data.purpose,
      '',
      '我承诺仅用于科研目的，不再分发数据，并在成果中致谢与引用来源。'
    ].join('\n');

    const mailto = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    window.location.href = mailto;
  });
});
