export function formatNumber(value) {
  if (value === null || value === undefined || value === "") {
    return "0";
  }

  return new Intl.NumberFormat("en-US").format(Number(value) || 0);
}

export function formatPercent(value) {
  if (value === null || value === undefined || value === "") {
    return "—";
  }

  const number = Number(value);
  const normalized = number <= 1 ? number * 100 : number;

  return `${normalized.toFixed(1)}%`;
}

export function formatDate(value) {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return new Intl.DateTimeFormat("en-US", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(date);
}

export function safeValue(value, fallback = "—") {
  return value === null || value === undefined || value === "" ? fallback : value;
}
