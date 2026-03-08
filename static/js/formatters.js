/**
 * Format a number as currency: -$123,456 (not $-123,456).
 */
function formatDollar(value) {
  if (value < 0) {
    return '-$' + Math.abs(value).toLocaleString();
  }
  return '$' + value.toLocaleString();
}
