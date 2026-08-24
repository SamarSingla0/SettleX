import React from "react";

export const StatusBadge: React.FC<{ status: string }> = ({ status }) => {
  switch (status) {
    case "MATCHED":
    case "MATCHED_DELAYED":
      return (
        <span className="bg-emerald-50 text-emerald-700 font-semibold px-2.5 py-0.5 rounded text-[11px]">
          {status === "MATCHED_DELAYED" ? "Matched (delayed)" : "Matched"}
        </span>
      );
    case "RESOLVED":
      return (
        <span className="bg-teal-50 text-teal-700 font-semibold px-2.5 py-0.5 rounded text-[11px]">
          Resolved
        </span>
      );
    case "EXCEPTION":
      return (
        <span className="bg-red-50 text-red-600 font-semibold px-2.5 py-0.5 rounded text-[11px]">
          Exception
        </span>
      );
    case "UNRESOLVED":
      return (
        <span className="bg-slate-100 text-slate-600 font-semibold px-2.5 py-0.5 rounded text-[11px]">
          Unresolved
        </span>
      );
    default:
      return (
        <span className="bg-slate-100 text-slate-600 font-semibold px-2.5 py-0.5 rounded text-[11px]">
          {status || "Unknown"}
        </span>
      );
  }
};
