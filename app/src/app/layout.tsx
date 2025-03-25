import "~/styles/globals.css";

import { Toaster } from "react-hot-toast";

import { GeistSans } from "geist/font/sans";
import { type Metadata } from "next";

import { TRPCReactProvider } from "~/trpc/react";

export const metadata: Metadata = {
    title: "Email relationship generator",
    icons: [{ rel: "icon", url: "/favicon.ico" }],
};

export default function RootLayout({
    children,
}: Readonly<{ children: React.ReactNode }>) {
    return (
        <html lang="en" className={`${GeistSans.variable} dark`}>
            <body>
                <TRPCReactProvider>{children}</TRPCReactProvider>
                <Toaster />
            </body>
        </html>
    );
}
