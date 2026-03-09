import { createElement } from "react";
import { DashboardLayout } from "@/layouts/DashboardLayout";

export default function ToolsRoute() {
  const content = createElement(
    "main",
    { className: "space-y-4 p-2" },
    createElement("h1", { className: "text-2xl font-semibold" }, "Tools"),
    createElement("p", { className: "text-sm text-slate-300" }, "Module under development."),
  );

  return createElement(DashboardLayout, { children: content });
}
