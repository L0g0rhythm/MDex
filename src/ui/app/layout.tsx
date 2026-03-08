import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
    title: "MDex Singularity Omni-v5",
    description: "Advanced Manga Downloader with IA Translation",
};

import { Inter } from "next/font/google";
import { LanguageProvider } from '../context/LanguageContext'

const inter = Inter({ subsets: ["latin"] });

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="dark">
            <body className={`${inter.className} bg-[#020617] text-slate-200 antialiased selection:bg-[#00f2ff]/30 selection:text-[#00f2ff]`}>
                <LanguageProvider>
                    {children}
                </LanguageProvider>
            </body>
        </html>
    );
}
