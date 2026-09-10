(() => {
  const root = document.querySelector('[data-listing-filters]');
  if (!root) return;

  const search = root.querySelector('[data-listing-search]');
  const buttons = Array.from(root.querySelectorAll('[data-listing-kind]'));
  const periodButtons = Array.from(root.querySelectorAll('[data-listing-period]'));
  const cards = Array.from(document.querySelectorAll('[data-listing-card]'));
  const sections = Array.from(document.querySelectorAll('[data-listing-section]'));
  const count = root.querySelector('[data-listing-count]');
  const empty = root.querySelector('[data-listing-empty]');

  let activeKind = 'all';
  let activePeriod = 'all';

  const normalize = (value) => String(value || '')
    .toLocaleLowerCase('ja')
    .replace(/\s+/g, ' ')
    .trim();

  const parseISODate = (value) => {
    if (!value) return null;
    const [year, month, day] = value.split('-').map(Number);
    if (!year || !month || !day) return null;
    return new Date(year, month - 1, day);
  };

  const startOfDay = (value) => {
    const copy = new Date(value);
    copy.setHours(0, 0, 0, 0);
    return copy;
  };

  const today = () => startOfDay(new Date());

  const endOfWeek = (base) => {
    const copy = new Date(base);
    const daysUntilSunday = (7 - copy.getDay()) % 7;
    copy.setDate(copy.getDate() + daysUntilSunday);
    return copy;
  };

  const endOfMonth = (base) => new Date(base.getFullYear(), base.getMonth() + 1, 0);

  const getPeriodEnd = (period, base) => {
    if (period === 'week') return endOfWeek(base);
    if (period === 'month') return endOfMonth(base);
    return null;
  };

  const matchesPeriod = (card, period) => {
    if (period === 'all') return true;

    const start = today();
    const end = getPeriodEnd(period, start);

    const occurrenceRaw = card.dataset.occurrenceDates;
    if (occurrenceRaw) {
      const dates = occurrenceRaw
        .split(',')
        .map((value) => parseISODate(value.trim()))
        .filter(Boolean);
      return dates.some((date) => date >= start && date <= end);
    }

    const startDate = parseISODate(card.dataset.startDate);
    const endDate = parseISODate(card.dataset.endDate);
    if (!startDate && !endDate) return false;

    const effectiveStart = startDate || endDate;
    const effectiveEnd = endDate || startDate;
    return effectiveStart <= end && effectiveEnd >= start;
  };

  const setActiveKindUI = (kind) => {
    activeKind = kind;
    buttons.forEach((candidate) => {
      const selected = candidate.dataset.listingKind === kind;
      candidate.classList.toggle('is-active', selected);
      candidate.setAttribute('aria-pressed', String(selected));
    });
  };

  const setActivePeriodUI = (period) => {
    activePeriod = period;
    periodButtons.forEach((candidate) => {
      const selected = candidate.dataset.listingPeriod === period;
      candidate.classList.toggle('is-active', selected);
      candidate.setAttribute('aria-pressed', String(selected));
    });
  };

  const update = () => {
    const query = normalize(search?.value);
    let visibleCount = 0;

    cards.forEach((card) => {
      const kindMatches = activeKind === 'all' || card.dataset.kind === activeKind;
      const periodMatches = matchesPeriod(card, activePeriod);
      const textMatches = !query || normalize(card.textContent).includes(query);
      const visible = kindMatches && periodMatches && textMatches;

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
      const kind = button.dataset.listingKind || 'all';
      setActiveKindUI(kind);

      if (kind === 'resource') {
        setActivePeriodUI('all');
      }

      update();
    });
  });

  periodButtons.forEach((button) => {
    button.addEventListener('click', () => {
      const period = button.dataset.listingPeriod || 'all';
      setActivePeriodUI(period);

      if (period !== 'all') {
        setActiveKindUI('event');
      }

      update();
    });
  });

  search?.addEventListener('input', update);
  update();
})();
