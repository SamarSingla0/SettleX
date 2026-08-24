import React from "react";

export const EmptyState: React.FC<{ title: string; detail?: string }> = ({
  title,
  detail,
}) => (
  <div className="bg-white border border-slate-200 rounded-xl p-10 text-center">
    <p className="font-bold text-slate-900">{title}</p>
    {detail && <p className="text-sm text-slate-500 mt-2">{detail}</p>}
  </div>
);

export const ErrorBanner: React.FC<{ message: string }> = ({ message }) => (
  <div className="bg-red-50 border border-red-200 text-red-700 text-sm font-medium rounded-lg px-4 py-3">
    {message}
  </div>
);
