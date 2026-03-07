import type { ReactNode } from "react";

interface TableProps {
  headers: string[];
  rows: Array<Array<ReactNode>>;
}

export function Table({ headers, rows }: TableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800">
      <table className="min-w-full border-collapse">
        <thead>
          <tr className="bg-slate-900/70">
            {headers.map((header) => (
              <th key={header} className="px-4 py-3 text-left text-xs uppercase tracking-wider text-slate-400">
                {header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={rowIndex} className="border-t border-slate-800">
              {row.map((cell, cellIndex) => (
                <td key={cellIndex} className="px-4 py-3 text-sm text-slate-200">
                  {cell}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
