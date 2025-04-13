import {
    ChartNetworkIcon,
    ChevronRight,
    ChevronsUpDown,
} from "lucide-react"

import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupContent,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarInset,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarProvider,
    SidebarRail,
    SidebarSeparator,
    SidebarTrigger,
} from "~/app/_components/ui/sidebar"
import { auth } from "~/server/auth";
import { LogoutButton } from "~/app/_components/pages/dashboard/logoutButton";
import { DropdownMenu, DropdownMenuContent, DropdownMenuTrigger } from "../_components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "../_components/ui/avatar";
import { NavbarItems, SidebarGraphItem } from "../_components/pages/dashboard/navbarItems";
import { headers } from "next/headers";
import { api } from "~/trpc/server";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "../_components/ui/collapsible";

export default async function DashboardLayout({ children }: Readonly<{ children: React.ReactNode }>) {
    const user = await auth.api.getSession({
        headers: await headers()
    });

    const graphNames = await api.graphs.getGraphs()

    return (
        <SidebarProvider>
            <Sidebar>
                <SidebarHeader>
                    <div className="flex items-center gap-2 px-4">
                        <span className="text-lg font-semibold">Sentiment Analyser</span>
                    </div>
                </SidebarHeader>
                <SidebarSeparator />
                <SidebarContent>
                    <SidebarMenu className="pt-5">
                        <NavbarItems />
                    </SidebarMenu>
                    <Collapsible title="Graphs" defaultOpen className="group/collapsible px-2 py-0">
                        <SidebarGroup className="py-0">
                            <SidebarGroupLabel
                                asChild
                                className="group/label text-sm text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground"
                            >
                                <CollapsibleTrigger className="flex gap-2">
                                    <ChartNetworkIcon />
                                    Graphs
                                    <ChevronRight className="ml-auto transition-transform group-data-[state=open]/collapsible:rotate-90" />
                                </CollapsibleTrigger>
                            </SidebarGroupLabel>
                            <CollapsibleContent>
                                <SidebarGroupContent>
                                    <SidebarMenu>
                                        {graphNames.map((item) => (
                                            <SidebarGraphItem key={item} item={item} />
                                        ))}
                                    </SidebarMenu>
                                </SidebarGroupContent>
                            </CollapsibleContent>
                        </SidebarGroup>
                    </Collapsible>
                </SidebarContent>
                <SidebarFooter>
                    <SidebarMenu>
                        <SidebarMenuItem>
                            <DropdownMenu>
                                <DropdownMenuTrigger asChild>
                                    <SidebarMenuButton
                                        size="lg"
                                        className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                                    >
                                        <Avatar className="h-8 w-8 rounded-lg">
                                            <AvatarFallback className="rounded-lg">
                                                {user?.user.email?.charAt(0).toUpperCase() ?? "U"}
                                            </AvatarFallback>
                                        </Avatar>
                                        <div className="grid flex-1 text-left text-sm leading-tight">
                                            <span className="truncate text-xs">
                                                {user?.user.email}
                                            </span>
                                        </div>
                                        <ChevronsUpDown className="ml-auto size-4" />
                                    </SidebarMenuButton>
                                </DropdownMenuTrigger>
                                <DropdownMenuContent
                                    className="w-(--radix-dropdown-menu-trigger-width) min-w-56 rounded-lg"
                                    side="bottom"
                                    align="end"
                                    sideOffset={4}
                                >
                                    <LogoutButton />
                                </DropdownMenuContent>
                            </DropdownMenu>
                        </SidebarMenuItem>
                    </SidebarMenu>
                </SidebarFooter>
                <SidebarRail />
            </Sidebar >
            <SidebarInset>
                <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
                    <div className="flex items-center gap-2 px-4">
                        <SidebarTrigger className="-ml-1" />
                    </div>
                </header>
                <div className="grow flex flex-col px-4 gap-y-2">
                    {children}
                </div>
            </SidebarInset>
        </SidebarProvider >
    )
}
