export function verdict(run, deadline) {
  if (!Number.isFinite(deadline) || deadline <= 0 || deadline > 120) return 'Enter a target between 0 and 120 seconds.';
  if (!run.valid) return 'Insufficient evidence: this run failed its checks.';
  const m = run.measurement;
  if (m.reached && m.remained_above_at_later_samples) return m.arrival_time_s <= deadline ? 'Target met at all nine sampled positions.' : 'Target not met at all nine sampled positions.';
  return m.observed_through_s < deadline ? 'Insufficient observation time.' : 'Target not met within the observed history.';
}
export const number = (x,d=2) => x == null ? 'Not established' : x.toFixed(d);
