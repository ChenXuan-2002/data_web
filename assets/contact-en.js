async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Failed to load ${url}`);
  return response.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [site, datasets] = await Promise.all([
      loadJSON('data/site.json'),
      loadJSON('data/datasets-en.json')
    ]);

    const brand = document.querySelector('#brand');
    if (brand) brand.textContent = site.site_title_en || site.site_title || 'Professor Jinghua Li Laboratory Databases';

    const footer = document.querySelector('#footerMeta');
    if (footer) {
      const owner = site.owner_en || site.owner || 'Professor Jinghua Li Laboratory';
      footer.textContent = `© ${new Date().getFullYear()} ${owner}`;
    }

    const contactPerson = document.querySelector('#contactPerson');
    if (contactPerson) contactPerson.textContent = site.contact_person_en || site.contact_person_zh || 'Associate Professor Jinghua LI';

    const contactTitle = document.querySelector('#contactTitle');
    if (contactTitle) contactTitle.textContent = site.contact_title_en || site.contact_title_zh || 'Associate Professor, Faculty of Health Sciences, University of Macau';

    const contactAffiliation = document.querySelector('#contactAffiliation');
    if (contactAffiliation) contactAffiliation.textContent = site.contact_affiliation_en || site.contact_affiliation_zh || site.affiliation_en || site.affiliation || 'Faculty of Health Sciences, University of Macau';

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
      const selections = Array.from(document.querySelectorAll('#datasetChecks input[type="checkbox"]:checked')).map(el => el.value);

      if (!selections.length) {
        alert('Please select at least one dataset.');
        return;
      }

      if (!data.agree) {
        alert('Please confirm that you agree to the data use terms.');
        return;
      }

      const subject = `[Data Request] ${data.name || 'Unnamed'} - ${selections.join(', ')}`;
      const body = [
        `Name: ${data.name || ''}`,
        `Affiliation / Department: ${data.org || ''}`,
        `Email: ${data.email || ''}`,
        `Requested datasets: ${selections.join(', ')}`,
        '',
        'Purpose of use:',
        data.purpose || '',
        '',
        'I confirm the data will only be used for research, will not be redistributed, and all outputs will acknowledge the source.'
      ].join('\n');

      window.location.href = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    });
  } catch (error) {
    console.error(error);
    alert('Failed to initialise the contact form. Please try again later.');
  }
});
