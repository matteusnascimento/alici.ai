import { MetricCard } from "./MetricCard";
import type { UsageMetric } from "@/types/dashboard";

interface UsageCardProps {
  usage: UsageMetric;
}

export function UsageCard({ usage }: UsageCardProps) {
  return <MetricCard metric={usage} />;
}
