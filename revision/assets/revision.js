// Me-LON revision sheets: render maths and wire the print button.
document.addEventListener('DOMContentLoaded', () => {
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\(', right: '\\)', display: false },
        { left: '$', right: '$', display: false }
      ],
      throwOnError: false
    });
  }
  document.querySelectorAll('[data-print]').forEach(btn =>
    btn.addEventListener('click', () => window.print()));
  const jump = document.querySelector('[data-jump]');
  if (jump) jump.addEventListener('change', () => {
    const t = document.getElementById(jump.value);
    if (t) t.scrollIntoView({ behavior: 'smooth' });
    jump.value = '';
  });
  document.querySelectorAll('[data-fib-toggle]').forEach(btn => btn.addEventListener('click', () => {
    const box = btn.closest('.fib'); const on = box.classList.toggle('show');
    btn.textContent = on ? 'Hide answers' : 'Show answers';
  }));
  document.documentElement.classList.add('math-ready');
});
