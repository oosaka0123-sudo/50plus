(() => {
  const root = document.querySelector('[data-listing-filters]');
  if (!root) return;

  const search = root.querySelector('[data-listing-search]');
  const buttons = Array.from(root.querySelectorAll('[data-listing-kind]'));
  const cards = Array.from(document.querySelectorAll('[data-listing-card]'));
  const sections = Array.from(document.querySelectorAll('[data-listing-section]'));
  const count = root.querySelector('[data-listing-count]');
  const empty = root.querySelector('[data-listing-empty]');

  let activeKind = 'all';

  const normalize = (value) => String(value || '')
    .toLocaleLowerCase('ja')
    .replace(/\s+/g, ' ')
    .trim();

  const update = () => {
    const query = normalize(search?.value);
    let visibleCount = 0;

    cards.forEach((card) => {
      const kindMatches = activeKind === 'all' || card.dataset.kind === activeKind;
      const textMatches = !query || normalize(card.textContent).includes(query);
      const visible = kindMatches && textMatches;

      card.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    sections.forEach((section) => {
      const sectionCards = Array.from(section.querySelectorAll('[data-listing-card]'));
      section.hidden = sectionCards.length > 0 && sectionCards.every((card) => card.hidden);
    });

    if (count) count.textContent = `${visibleCount}件を表示中`;
    if (empty) empty.hidden = visibleCount !== 0;
  };

  buttons.forEach((button) => {
    button.addEventListener('click', () => {
      activeKind = button.dataset.listingKind || 'all';

      buttons.forEach((candidate) => {
        const selected = candidate === button;
        candidate.classList.toggle('is-active', selected);
        candidate.setAttribute('aria-pressed', String(selected));
      });

      update();
    });
  });

  search?.addEventListener('input', update);
  update();
})();
