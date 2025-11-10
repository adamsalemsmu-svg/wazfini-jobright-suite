"use client";

import { useEffect, useState } from 'react';

interface MetricsSummary {
  total: number;
  success: number;
  failure: number;
}

interface AnalyticsData {
  total: number;
  success: number;
  failure: number;
  average_duration: number;
}

export default function AnalyticsSummary() {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchData() {
      try {
        const baseUrl = process.env.NEXT_PUBLIC_API_URL;
        const [metricsRes, analyticsRes] = await Promise.all([
          fetch(`${baseUrl}/metrics/summary`),
          fetch(`${baseUrl}/analytics/summary`),
        ]);

        if (!metricsRes.ok || !analyticsRes.ok) {
          throw new Error('Failed to fetch analytics data');
        }

        const metricsData: MetricsSummary = await metricsRes.json();
        const analyticsData: AnalyticsData = await analyticsRes.json();

        setMetrics(metricsData);
        setAnalytics(analyticsData);
        setLoading(false);
      } catch (err: unknown) {
        console.error(err);
        if (err instanceof Error) {
          setError(err.message);
        } else {
          setError('An error occurred');
        }
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) {
    return <div className="p-4">Loading analytics...</div>;
  }

  if (error || !metrics || !analytics) {
    return <div className="p-4 text-red-600">{error ?? 'Failed to load analytics'}</div>;
  }

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h2 className="text-xl font-semibold mb-2">Analytics Summary</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded">
          <div className="text-sm text-gray-500">Total jobs processed</div>
          <div className="text-lg font-bold">{metrics.total}</div>
        </div>
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded">
          <div className="text-sm text-gray-500">Successful</div>
          <div className="text-lg font-bold">{metrics.success}</div>
        </div>
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded">
          <div className="text-sm text-gray-500">Failed</div>
          <div className="text-lg font-bold">{metrics.failure}</div>
        </div>
        <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded col-span-2 md:col-span-1">
          <div className="text-sm text-gray-500">Average Duration (s)</div>
          <div className="text-lg font-bold">{analytics.average_duration?.toFixed(2)}</div>
        </div>
      </div>
    </div>
  );
}
