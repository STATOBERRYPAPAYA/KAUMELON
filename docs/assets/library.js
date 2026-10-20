<script>
document.addEventListener('DOMContentLoaded', () => {
  const input = document.querySelector('#book-search');
  if (!input) return;
  document.querySelector('.library-tools').hidden = false;
  const books = [...document.querySelectorAll('[data-search]')];
  input.addEventListener('input', () => {
    const terms = input.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    let count = 0;
    books.forEach(book => {
      book.hidden = !terms.every(term => (book.dataset.search + ' ' + book.textContent).toLowerCase().includes(term));
      if (!book.hidden) count++;
    });
    document.querySelector('#book-count').textContent = `${count} ${count === 1 ? 'book' : 'books'} available`;
    document.querySelector('#no-books').hidden = count !== 0;
  });
});
</script>


<script src="/assets/melon-tracker.js" defer></script>
<script src="/assets/public-usage.js?v=20261020-1" defer></script>
