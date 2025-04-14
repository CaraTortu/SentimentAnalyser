"use client"

import { HouseIcon, type LucideIcon } from "lucide-react";
import { SidebarMenuButton, SidebarMenuItem } from "../../ui/sidebar";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "~/lib/utils";

export interface NavOption {
    name: string;
    url: string;
    icon: LucideIcon;
}

export const NAV_OPTIONS: NavOption[] = [
    {
        name: 'Home',
        url: '/dashboard',
        icon: HouseIcon,
    },
];

export const NavbarItems: React.FC = () => {
    const location = usePathname();

    return (
        <>
            {NAV_OPTIONS.map((item) => (
                <SidebarMenuItem key={item.name} className="px-4 rounded-md">
                    <SidebarMenuButton asChild>
                        <Link href={item.url} className={cn(location == item.url && "bg-sidebar-accent text-sidebar-accent-foreground", "flex gap-2")}>
                            <item.icon />
                            <span className="text-md">{item.name}</span>
                        </Link>
                    </SidebarMenuButton>
                </SidebarMenuItem>
            ))}
        </>
    )
}

export const SidebarGraphItem = ({ item }: { item: string }) => {
    const location = usePathname()

    return (
        <SidebarMenuItem key={item} >
            <SidebarMenuButton asChild>
                <Link href={`/dashboard/graph/${item}`} className={cn(location.endsWith(item) && "bg-sidebar-accent text-sidebar-accent-foreground", "px-2 rounded-md")}>- {item}</Link>
            </SidebarMenuButton>
        </SidebarMenuItem>

    )
}
