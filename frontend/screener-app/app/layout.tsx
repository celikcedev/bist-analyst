import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "BIST Analyst - Pine Screener",
  description: "Otonom Trading Sinyal Tarayıcı - TradingView Pine Script tabanlı BIST tarama platformu",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
