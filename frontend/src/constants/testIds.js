// Central testid registry so tests and code stay in sync.
export const HOME = { emergentLink: "emergent-link" };

export const DASH = {
  header: "dashboard-header",
  sourceBadge: "system-source-badge",
  statusBadge: "system-status-badge",
  card: (name) => `summary-card-${name}`,
  cardValue: (name) => `summary-card-value-${name}`,
  table: "stock-table",
  row: (sym) => `stock-row-${sym}`,
  screenBadge: (sym) => `screen-badge-${sym}`,
  detailPanel: "stock-detail-panel",
};
