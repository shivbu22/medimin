import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Medimin — India's Smartest Medicine Price Comparison Engine",
  description:
    "Compare medicine prices across Tata 1mg, Apollo Pharmacy, PharmEasy, Netmeds, Truemeds & MedPlusmart. Save up to 85% with generic substitutes.",
  keywords:
    "medicine price comparison, generic substitutes, cheap medicines India, pharmacy comparison, drug prices",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased`}>
      <body className="min-h-full flex flex-col bg-[#F0FDFA]">{children}</body>
    </html>
  );
}
