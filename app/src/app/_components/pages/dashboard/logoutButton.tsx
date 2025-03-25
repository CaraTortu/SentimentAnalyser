"use client"

import toast from "react-hot-toast";
import {
    DropdownMenuItem,
} from "~/app/_components/ui/dropdown-menu"
import { LogOutIcon } from "lucide-react";
import { authClient } from "~/lib/auth-client";
import { useRouter } from "next/navigation";

export function LogoutButton() {
    const router = useRouter()

    const signOutClicked = async () => {
        await authClient.signOut();
        toast.success("See you again soon!")
        router.refresh()
    }

    return (
        <DropdownMenuItem onClick={signOutClicked}>
            <LogOutIcon />
            Log Out
        </DropdownMenuItem>
    )
}
