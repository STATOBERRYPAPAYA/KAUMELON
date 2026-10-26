// Me-LON revision sheets: render maths and wire the print button.
document.addEventListener('DOMContentLoaded', () => {
  if (window.renderMathInElement) {
    renderMathInElement(document.body, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
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

// Keep longer formulae across both subcolumns when printing.
window.addEventListener('beforeprint', () => {
  document.querySelectorAll('.fxgrid .fx').forEach(box => {
    const math = box.querySelector('.katex-display');
    if (math && math.scrollWidth > math.clientWidth + 2) box.classList.add('wide');
  });
});
window.addEventListener('afterprint', () => document.querySelectorAll('.fx.wide').forEach(box => box.classList.remove('wide')));

window.addEventListener('beforeprint', () => {
  document.querySelectorAll('.katex-display').forEach(display => {
    const math = display.querySelector('.katex');
    if (!math) return;
    const available = display.clientWidth, natural = Math.max(math.scrollWidth, math.getBoundingClientRect().width);
    if (natural > available && available > 0) {
      math.dataset.printFit = 'true';
      math.style.fontSize = (parseFloat(getComputedStyle(math).fontSize) * (available - 4) / natural) + 'px';
    }
  });
});
window.addEventListener('afterprint', () => document.querySelectorAll('[data-print-fit]').forEach(math => { math.style.removeProperty('font-size'); delete math.dataset.printFit; }));
