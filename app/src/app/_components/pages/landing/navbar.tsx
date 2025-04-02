import { type Session } from "better-auth";
import Link from "next/link";
import { Button } from "../../ui/button";

export default function NavBar({ session }: { session: Session | undefined }) {
    return (
        <div className="flex px-4 py-3 gap-4 left-0 right-0 m-auto items-center fixed top-0 bg-stone-900/80 border-b border-white backdrop-blur-lg">
            <Link href="/" prefetch={false} className="font-mono font-bold">Sentiment analyser</Link>

            <div className="flex-grow flex justify-end items-center">
                {session && (
                    <Link href="/dashboard">
                        <Button className="cursor-pointer hover:bg-primary/80 duration-300">
                            Dashboard
                        </Button>
                    </Link>
                )}
                {!session && (
                    <Link href="/login">
                        <Button className="cursor-pointer hover:bg-primary/80 duration-300">
                            Login
                        </Button>
                    </Link>
                )}
            </div>
        </div>
    )
}
