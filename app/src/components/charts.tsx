"use client";

import {
  CartesianGrid, ReferenceArea, ReferenceLine, ResponsiveContainer, Scatter,
  ScatterChart, Tooltip, XAxis, YAxis,
} from "recharts";
import { percent, pp } from "../lib/data";
import { theme } from "../styles/theme";
import type { Forecast, MapData, Signal } from "../types/contracts";

export type MapPoint = MapData["points"][number] & {
  name: string;
  state: string;
  years: string;
  actual: number | null;
  subject: boolean;
  neighbour: boolean;
};

export function PrecedentMap({ points, explained }: {
  points: MapPoint[];
  explained: MapData["explained"];
}) {
  const extent = Math.max(0, ...points.map((point) => Math.abs(point.actual ?? 0)));
  const ordered = [...points].sort((a, b) => Number(a.subject) - Number(b.subject));

  function pointShape({ cx, cy, payload }: { cx?: number; cy?: number; payload?: MapPoint }) {
    if (cx === undefined || cy === undefined || !payload) return <g />;
    if (payload.subject) {
      return <text x={cx} y={cy} dominantBaseline="central" textAnchor="middle" fill={theme.accent} fontSize={22}>★</text>;
    }
    const actual = payload.actual;
    const tone = actual === null ? theme.missing
      : `color-mix(in srgb, ${actual < 0 ? theme.negative : theme.positive} ${extent ? Math.abs(actual / extent) * 100 : 0}%, ${theme.midpoint})`;
    return <circle cx={cx} cy={cy} r={payload.neighbour ? 6 : 4} fill={tone}
      stroke={payload.neighbour ? theme.foreground : "none"} strokeWidth={2} />;
  }

  return (
    <>
      <div className="h-80 min-w-0" aria-label="Scatter plot of historical policy fingerprints">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 12, right: 16, bottom: 28, left: 20 }}>
            <CartesianGrid stroke={theme.border} />
            <XAxis type="number" dataKey="x" domain={["auto", "auto"]} tick={false}
              label={{ value: `PC1 · ${percent(explained[0])} of variance`, position: "insideBottom", offset: -12 }} />
            <YAxis type="number" dataKey="y" domain={["auto", "auto"]} tick={false}
              label={{ value: `PC2 · ${percent(explained[1])} of variance`, angle: -90, position: "insideLeft" }} />
            <Tooltip cursor={false} content={({ active, payload }) => {
              const point = payload?.[0]?.payload as MapPoint | undefined;
              return active && point ? (
                <div className="rounded-lg border border-border bg-card p-3 text-sm shadow-sm">
                  <strong>{point.name}</strong>
                  <div>{point.state} · {point.years}</div>
                  <div>{point.actual === null ? "Outcome unavailable" : pp(point.actual)}</div>
                </div>
              ) : null;
            }} />
            <Scatter data={ordered} shape={pointShape} isAnimationActive={false} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <p className="text-sm text-muted-foreground">
        ★ Subject · Outlined points are forecast neighbours ·
        <span style={{ color: theme.negative }}> Below</span> / <span style={{ color: theme.positive }}>above</span> benchmark · Grey points have no outcome
      </p>
    </>
  );
}

export function ForecastPlot({ forecast }: { forecast: Forecast }) {
  const { baseline, forecast: estimate, p10, p90 } = forecast;
  const low = Math.min(0, baseline, estimate, p10);
  const high = Math.max(0, baseline, estimate, p90);
  const padding = Math.max((high - low) * 0.08, 0.0001);
  return (
    <div className="h-36 min-w-0" aria-label="Baseline, forecast and 80% precedent band">
      <ResponsiveContainer width="100%" height="100%">
        <ScatterChart margin={{ top: 8, right: 25, bottom: 8, left: 25 }}>
          <XAxis type="number" dataKey="value" domain={[low - padding, high + padding]}
            tickFormatter={pp} tickCount={4} tick={{ fontSize: 11 }} />
          <YAxis type="number" dataKey="row" hide domain={[0, 1]} />
          <ReferenceLine x={0} stroke={theme.missing} strokeDasharray="4 3" />
          <ReferenceArea x1={p10} x2={p90} y1={0.15} y2={0.5} fill={theme.accent} fillOpacity={0.17} />
          <Scatter name="Baseline" data={[{ value: baseline, row: 0.72 }]} fill={theme.mutedForeground} isAnimationActive={false} />
          <Scatter name="Forecast" data={[{ value: estimate, row: 0.325 }]} fill={theme.accent} isAnimationActive={false} />
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
}

export function Calibration({ bins }: { bins: Signal["calibration"] }) {
  return (
    <figure>
      <figcaption className="text-sm font-medium">Calibration · observed vs predicted probability</figcaption>
      <div className="h-52 min-w-0">
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 12, right: 20, bottom: 4, left: 0 }}>
            <CartesianGrid stroke={theme.border} />
            <XAxis type="number" dataKey="predicted" domain={[0, 1]} tickFormatter={percent} />
            <YAxis type="number" dataKey="observed" domain={[0, 1]} tickFormatter={percent} />
            <ReferenceLine segment={[{ x: 0, y: 0 }, { x: 1, y: 1 }]} stroke={theme.missing} strokeDasharray="4 3" />
            <Tooltip content={({ active, payload }) => {
              const bin = payload?.[0]?.payload as Signal["calibration"][number] | undefined;
              return active && bin ? (
                <div className="rounded-lg border border-border bg-card p-3 text-sm">
                  Predicted {percent(bin.predicted)} · observed {percent(bin.observed)} · {bin.n} terms
                </div>
              ) : null;
            }} />
            <Scatter data={bins} fill={theme.accent} isAnimationActive={false} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </figure>
  );
}
