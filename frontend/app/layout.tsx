import type { Metadata } from "next";
import { Orbitron, Space_Grotesk } from "next/font/google";

import "./globals.css";

const bodyFont = Space_Grotesk({
  variable: "--font-sans",
  subsets: ["latin"],
});

const displayFont = Orbitron({
  variable: "--font-display",
  subsets: ["latin"],
  weight: ["500", "700"],
});

export const metadata: Metadata = {
  title: "AgentOrchestrator Console",
  description: "Cyberpunk multi-agent orchestration workspace for research, analysis, and report generation.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${bodyFont.variable} ${displayFont.variable} font-[family-name:var(--font-sans)]`}
      >
        {children}
      </body>
    </html>
  );
}
