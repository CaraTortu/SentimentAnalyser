import { headers } from "next/headers";
import Link from "next/link";
import { redirect } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/app/_components/ui/card";
import { auth } from "~/server/auth";
import GoogleSignin from "../_components/pages/login/google-signin";

export default async function Login() {
    const session = await auth.api.getSession({
        headers: await headers()
    })

    if (session) {
        redirect("/dashboard")
    }

    return (
        <div className="flex min-h-screen flex-col items-center justify-center">
            <div className="grow flex flex-col items-center justify-center gap-6 p-6 md:p-10">
                <div className="flex w-full max-w-sm flex-col gap-6">
                    <div className="flex flex-col gap-6">
                        <Card>
                            <CardHeader className="text-center">
                                <CardTitle className="text-xl">Welcome back</CardTitle>
                                <CardDescription>
                                    Login with your Google account
                                </CardDescription>
                            </CardHeader>
                            <CardContent>
                                <div className="flex flex-col gap-4">
                                    <GoogleSignin />
                                </div>
                            </CardContent>
                        </Card>
                        <div className="text-balance text-center text-xs text-muted-foreground [&_a]:underline [&_a]:underline-offset-4 hover:[&_a]:text-primary  ">
                            By clicking continue, you agree to our <Link href="/terms">Terms of Service</Link>{" "}
                            and <Link href="/terms">Privacy Policy</Link>.
                        </div>
                    </div>
                </div>
            </div >
        </div >
    )
}
