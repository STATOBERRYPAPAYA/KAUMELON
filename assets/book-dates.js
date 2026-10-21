export function badgeWindow(publicationDate) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(publicationDate || '')) return null;
  const [year, month, day] = publicationDate.split('-').map(Number);
  const start = new Date(Date.UTC(year, month - 1, day));
  if (start.getUTCFullYear() !== year || start.getUTCMonth() !== month - 1 || start.getUTCDate() !== day) return null;
  const lastDay = new Date(Date.UTC(year, month + 1, 0)).getUTCDate();
  return {start: start.getTime() - 19800000, end: Date.UTC(year, month, Math.min(day, lastDay)) - 19800000};
}
export function isNewBook(publicationDate, now = Date.now()) {
  const window = badgeWindow(publicationDate);
  return !!window && now >= window.start && now < window.end;
}
