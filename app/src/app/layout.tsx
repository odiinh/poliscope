import Link from "next/link";
import type { Metadata } from "next";
import type { CSSProperties, ReactNode } from "react";
import { theme } from "../styles/theme";
import "./globals.css";

export const metadata: Metadata = {
  title: "PoliScope",
  description: "Policy fingerprints and historical precedents.",
};

const styles = {
  "--poliscope-font": theme.font,
  "--poliscope-background": theme.background,
  "--poliscope-foreground": theme.foreground,
  "--poliscope-muted": theme.muted,
  "--poliscope-muted-foreground": theme.mutedForeground,
  "--poliscope-border": theme.border,
  "--poliscope-radius": theme.radius,
  "--poliscope-spacing": theme.spacing,
  "--poliscope-accent": theme.accent,
} as CSSProperties;

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" style={styles}>
      <body className="bg-background font-sans text-foreground">
        <header className="border-b border-border bg-card">
          <nav aria-label="Main navigation" className="mx-auto max-w-5xl px-4 py-3">
            <Link className="font-semibold tracking-tight" href="/">PoliScope</Link>
          </nav>
        </header>
        {children}
      </body>
    </html>
  );
}
