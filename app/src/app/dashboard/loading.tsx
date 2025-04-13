import { LoaderCircleIcon } from "lucide-react";

export default function LoadingPage() {
    return (
        <main className="flex-1 flex items-center justify-center min-h-65hv">
            <LoaderCircleIcon className="animate-spin" size={48} />
        </main>
    )
}
