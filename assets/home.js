async function loadJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error('加载失败: ' + url);
  return res.json();
}

function el(tag, cls) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  return e;
}

document.addEventListener('DOMContentLoaded', async () => {
  const [site, datasets] = await Promise.all([
    loadJSON('data/site.json'),
    loadJSON('data/datasets.json')
  ]);

  document.title = site.site_title;
  document.querySelector('#brand').textContent = site.site_title;
  document.querySelector('#siteTitle').textContent = site.site_title;
  document.querySelector('#footerMeta').textContent =
    `© ${new Date().getFullYear()} ${site.owner} · ${site.affiliation || ''}`;

  const list = document.querySelector('#dsList');
  const render = (items) => {
    list.innerHTML = '';
    items.forEach(d => {
      const card = el('a', 'card-item');
      card.href = `datasets/${d.slug}.html`;
      card.innerHTML = `
        <h3>${d.title}</h3>
        <p>${(d.summary || '').slice(0, 120)}</p>
      `;
      list.appendChild(card);
    });
  };
  render(datasets);

  const search = document.querySelector('#dsSearch');
  search.addEventListener('input', () => {
    const q = search.value.trim().toLowerCase();
    const filtered = datasets.filter(d =>
      (d.title || '').toLowerCase().includes(q) ||
      (d.summary || '').toLowerCase().includes(q)
    );
    render(filtered);
  });
});
