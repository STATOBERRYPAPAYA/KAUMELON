/** Human-readable estimated reading time. Source measurements remain in seconds. */
export function formatReadingTime(seconds, {includeSeconds = false} = {}) {
  const value = Number.isFinite(seconds) && seconds > 0 ? seconds : 0;
  if (includeSeconds && value < 60) return `${Math.round(value)} sec`;
  const hours = value >= 3600;
  const amount = new Intl.NumberFormat('en-IN', {maximumFractionDigits: 1}).format(value / (hours ? 3600 : 60));
  return `${amount} ${hours ? 'hr' : 'min'}`;
}
