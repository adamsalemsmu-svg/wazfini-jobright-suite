import type { Metadata } from "next";
import type { ReactNode } from "react";
import { Inter } from "next/font/google";
import Script from "next/script";
import { defaultLocale } from "@/i18n/config";
import "./globals.css";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://wazifni.ai";
const plausibleDomain = process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN;
const plausibleSrc = process.env.NEXT_PUBLIC_PLAUSIBLE_SRC ?? "https://plausible.io/js/script.tagged-events.js";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: "Wazifni Beta Launch",
  description: "Automate applications, track analytics, and stay on top of your job search with Wazifni.",
  openGraph: {
    title: "Wazifni Beta Launch",
    description: "Automate applications, track analytics, and stay on top of your job search with Wazifni.",
    url: siteUrl,
    images: [
      {
        url: "/og-launch.svg",
        width: 1200,
        height: 630,
        alt: "Wazifni Beta Launch",
      },
    ],
  },
  twitter: {
    card: "summary_large_image",
    title: "Wazifni Beta Launch",
    description: "Automate applications, track analytics, and stay on top of your job search with Wazifni.",
    images: ["/og-launch.svg"],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: ReactNode;
}>) {
  return (
    <html lang={defaultLocale} suppressHydrationWarning>
      <body className={`${inter.variable} font-sans min-h-screen bg-background text-foreground`}>
        {plausibleDomain ? (
          <Script
            src={plausibleSrc}
            data-domain={plausibleDomain}
            strategy="afterInteractive"
          />
        ) : null}
        {children}
      </body>
    </html>
  );
}
