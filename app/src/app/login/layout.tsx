import { headers } from "next/headers";
import { redirect } from "next/navigation";
import { auth } from "~/server/auth";

export default async function LoginLayout({
    children,
}: Readonly<{ children: React.ReactNode }>) {
    const session = await auth.api.getSession({
        headers: await headers()
    });

    if (session) {
        redirect("/dashboard");
    }

    return (
        <div className="flex min-h-screen flex-col items-center justify-center">
            {children}
        </div>
    );
}
