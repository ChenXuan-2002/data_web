async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to load ' + url);
  return response.json();
}

document.addEventListener('DOMContentLoaded', async () => {
  try {
    const [site, datasets] = await Promise.all([
      loadJSON('data/site.json'),
      loadJSON('data/datasets-en.json')
    ]);

    const brand = document.querySelector('#brand');
    if (brand) {
      const title = site.site_title_en || 'XX Laboratory Databases';
      brand.textContent = title;
    }

    const footer = document.querySelector('#footerMeta');
    if (footer) {
      const ownerText = site.owner_en || site.owner || 'XX Laboratory';
      footer.textContent = `© ${new Date().getFullYear()} ${ownerText}`;
    }

    const email = site.contact_email || 'data-admin@example.edu';
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
      const data = Object.fromEntries(new FormData(form).entries());
      const selections = Array.from(document.querySelectorAll('#datasetChecks input[type="checkbox"]:checked'))
        .map(input => input.value);

      if (!selections.length) {
        alert('Please select at least one dataset.');
        return;
      }
      if (!data.agree) {
        alert('Please confirm that you agree to the data use terms.');
        return;
      }

      const subject = `[Data Request] ${data.name || 'Unnamed'} - ${selections.join(', ')}`;
      const bodyLines = [
        `Name: ${data.name || ''}`,
        `Affiliation / Department: ${data.org || ''}`,
        `Email: ${data.email || ''}`,
        `Requested datasets: ${selections.join(', ')}`,
        '',
        'Purpose of use:',
        data.purpose || '',
        '',
        'I confirm the data will only be used for research, will not be redistributed, and all outputs will acknowledge the source.'
      ];

      const mailto = `mailto:${encodeURIComponent(email)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(bodyLines.join('\n'))}`;
      window.location.href = mailto;
    });
  } catch (error) {
    console.error(error);
    alert('Failed to initialise the contact form. Please try again later.');
  }
});
