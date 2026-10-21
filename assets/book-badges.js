import {badgeWindow, isNewBook} from './book-dates.js?v=20261021-1';
const badges = [...document.querySelectorAll('.new-badge[data-published]')];
let timer;
function refreshBadges() {
  clearTimeout(timer);
  const now = Date.now();
  let next = now + 86400000;
  for (const badge of badges) {
    const date = badge.dataset.published, window = badgeWindow(date);
    badge.hidden = !isNewBook(date, now);
    if (window) for (const boundary of [window.start, window.end]) if (boundary > now) next = Math.min(next, boundary);
  }
  if (badges.length) timer = setTimeout(refreshBadges, Math.max(100, next - now + 10));
}
refreshBadges();
document.addEventListener('visibilitychange', refreshBadges);
window.addEventListener('pageshow', refreshBadges);
