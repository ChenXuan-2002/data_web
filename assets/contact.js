async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`加载失败: ${url}`);
  return response.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [site, datasets] = await Promise.all([
      loadJSON('data/site.json'),
      loadJSON('data/datasets-zh.json')
    ]);

    const brand = document.querySelector('#brand');
    if (brand) brand.textContent = site.site_title || '李菁華教授实验室数据库';

    const footer = document.querySelector('#footerMeta');
    if (footer) {
      const owner = site.owner_zh || site.owner || '李菁華教授实验室';
      footer.textContent = `© ${new Date().getFullYear()} ${owner}`;
    }

    const contactPerson = document.querySelector('#contactPerson');
    if (contactPerson) contactPerson.textContent = site.contact_person_zh || site.contact_person_en || '李菁華 副教授';

    const contactTitle = document.querySelector('#contactTitle');
    if (contactTitle) contactTitle.textContent = site.contact_title_zh || site.contact_title_en || '澳门大学健康科学学院 副教授';

    const contactAffiliation = document.querySelector('#contactAffiliation');
    if (contactAffiliation) contactAffiliation.textContent = site.contact_affiliation_zh || site.contact_affiliation_en || site.affiliation_zh || site.affiliation || '澳门大学健康科学学院';

    const email = site.contact_email || 'lijinghua@um.edu.mo';
    const emailLink = document.querySelector('#contactEmail');
    if (emailLink) {
      emailLink.textContent = email;
      emailLink.href = `mailto:${email}`;
    }

    const wrap = document.querySelector('#datasetChecks');
    if (wrap) {
      datasets.forEach(dataset => {
        const label = document.createElement('label');
        label.innerHTML = `<input type="checkbox" value="${dataset.slug}" /> ${dataset.title}`;
        wrap.appendChild(label);
      });
    }

    const form = document.querySelector('#applyForm');
    if (!form) return;

    form.addEventListener('submit', (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const data = Object.fromEntries(formData.entries());
      const selected = Array.from(document.querySelectorAll('#datasetChecks input[type="checkbox"]:checked')).map(el => el.value);

      if (!selected.length) {
        alert('请至少选择一个数据集。');
        return;
      }

      if (!data.agree) {
        alert('请勾选同意数据使用条款。');
        return;
      }

      const subject = `[数据申请] ${data.name || '未署名'} - ${selected.join(', ')}`;
      const body = [
        `姓名：${data.name || ''}`,
        `单位 / 院系：${data.org || ''}`,
        `邮箱：${data.email || ''}`,
        `申请数据集：${selected.join(', ')}`,
        '',
        '用途说明：',
        data.purpose || '',
        '',
        '我承诺仅用于科研目的，不再分发数据，并在成果中致谢与引用来源。'
      ].join('\n');

      window.location.href = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  } catch (error) {
    console.error(error);
    alert('表单初始化失败，请稍后重试。');
  }
});
