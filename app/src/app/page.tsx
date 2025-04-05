import { auth } from "~/server/auth";
import NavBar from "./_components/pages/landing/navbar";
import { headers } from "next/headers";

export default async function Home() {
    const session = await auth.api.getSession({
        headers: await headers()
    })

    return (
        <main className="flex min-h-screen flex-col p-4">
            <NavBar session={session?.session} />

            <div className="pt-14 flex flex-col gap-4">
            </div>
        </main>
    );
}
