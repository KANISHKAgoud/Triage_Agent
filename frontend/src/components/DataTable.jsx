import { safeValue } from "../utils/formatters.js";

export default function DataTable({ columns, rows, emptyMessage = "No records found." }) {
  return (
    <div className="panel overflow-hidden rounded-lg">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-white/10">
          <thead className="bg-white/[0.04]">
            <tr>
              {columns.map((column) => (
                <th
                  className="px-5 py-3 text-left text-xs font-semibold uppercase tracking-wider text-slate-400"
                  key={column.key}
                  scope="col"
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/10">
            {rows.length === 0 ? (
              <tr>
                <td className="px-5 py-8 text-center text-sm text-slate-400" colSpan={columns.length}>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              rows.map((row, index) => (
                <tr className="transition hover:bg-white/[0.035]" key={row.id || row.key || row.issueKey || index}>
                  {columns.map((column) => (
                    <td className="max-w-lg px-5 py-4 text-sm text-slate-200" key={column.key}>
                      {column.render ? column.render(row) : safeValue(row[column.key])}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
