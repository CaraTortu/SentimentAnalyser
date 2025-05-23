/* eslint-disable react/no-children-prop */
/* eslint-disable react-hooks/exhaustive-deps */
"use client";

import React, { use, useEffect, useState } from "react";
import { ReactFlow, Background, useNodesState, useEdgesState, type Node, Controls, MiniMap, type Edge } from "@xyflow/react";
import * as d3 from "d3-force";
import "@xyflow/react/dist/style.css";
import EmailNode from "~/app/_components/pages/dashboard/email-node";
import EmailEdge from "~/app/_components/pages/dashboard/email-edge";
import { api } from "~/trpc/react";
import { useIsMobile } from "~/hooks/use-mobile";
import { type z } from "zod";
import { useForm } from '@tanstack/react-form'
import { Input } from "~/app/_components/ui/input";
import { Button } from "~/app/_components/ui/button";
import toast from "react-hot-toast";
import { Accordion, AccordionItem, AccordionTrigger, AccordionContent } from "~/app/_components/ui/accordion";
import { TooltipProvider } from "~/app/_components/ui/tooltip";
import { type QueryPayload, searchSchema } from "~/lib/types";
import { LoaderCircleIcon, StarIcon } from "lucide-react";

const nodeTypes = {
    emailNode: EmailNode
}

const edgeTypes = {
    emailEdge: EmailEdge
}

const defaultFormValues = {
    limit: 10,
    emailSearch: "",
    emailsEndWith: ""
} satisfies QueryPayload

const calculateValue = (sentiment: number, emailsSent: number) => 0.2 * Math.log(emailsSent) + sentiment

export default function LayoutFlow({
    params,
}: {
    params: Promise<{ datasetName: string }>
}) {
    // Get params
    const { datasetName } = use(params)

    // Reactflow
    const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
    const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

    // History
    const searchHistory = api.search.getSearches.useQuery({ datasetName, limit: 10 })
    const savedHistoryApi = api.search.getSavedSearches.useQuery({ datasetName })
    const [savedHistory, setSavedHistory] = useState<(z.infer<typeof searchSchema> & { id: string, saved: boolean })[]>([])
    const addSearchHistoryMutation = api.search.addSearch.useMutation()
    const [history, setHistory] = useState<(z.infer<typeof searchSchema> & { id: string, saved: boolean })[]>([])

    useEffect(() => {
        if (!searchHistory.data) { return; }
        setHistory(searchHistory.data.data)
    }, [searchHistory.data])

    useEffect(() => {
        if (!savedHistoryApi.data) { return; }
        setSavedHistory(savedHistoryApi.data.data)
    }, [savedHistoryApi.data])

    // Saving queries
    const saveSearchMutation = api.search.saveSearch.useMutation();

    const saveSearch = async (entry: typeof history[number]) => {
        entry.saved = !entry.saved

        setHistory((old) => {
            const entryIdx = old.findIndex(v => v.id === entry.id)
            old[entryIdx] = entry
            return old
        })

        if (entry.saved) {
            setSavedHistory((old) => [entry, ...old])
        } else {
            setSavedHistory((old) => old.filter(v => v.id !== entry.id))
        }

        const result = await saveSearchMutation.mutateAsync(entry)

        if (!result.success) {
            toast.error(result.reason!)
            return;
        }

    }

    // Data fetching
    const relationships = api.graphs.getRelationships.useMutation();
    const [newData, setNewData] = useState(false)
    const form = useForm({
        defaultValues: defaultFormValues,
        validators: {
            onSubmit: searchSchema
        },
        onSubmit: async ({ value }) => {
            relationships.mutate({ email: value.emailSearch, endsWith: value.emailsEndWith, datasetName })
            await addSearchHistoryMutation.mutateAsync({ datasetName, ...value })
            await searchHistory.refetch()
        }
    });

    // Layout rendering
    const isPhone = useIsMobile()

    // Run simulation
    const simulate = () => {
        // Convert nodes to D3 format
        const d3Nodes = nodes.map((node) => ({
            ...node,
            x: node.position.x,
            y: node.position.y,

            // Fix center node at (0,0)
            fx: node.id === "1" ? 0 : undefined,
            fy: node.id === "1" ? 0 : undefined
        }));

        // Convert edges to D3 format
        const d3Edges = edges.map((edge) => ({ ...edge }));

        const simulation = d3
            .forceSimulation(d3Nodes)
            .force(
                "link",
                d3
                    .forceLink(d3Edges)
                    .id((d) => nodes[d.index ?? 0]?.id ?? 0)
                    .strength(-1 * (1 / d3Edges.length))
            )
            .force("charge", d3.forceManyBody().strength(-200))
            .force("radial", d3.forceRadial(d3Nodes.length / Math.sqrt(d3Nodes.length) * 100).strength(1))
            .force("collide", d3.forceCollide(1.2).radius(100))
            .on("tick", () => {
                setNodes((prevNodes) =>
                    prevNodes.map((node) => {
                        const simNode = d3Nodes.find((n) => n.id === node.id);
                        if (!simNode) return node;
                        return {
                            ...node,
                            position: { x: simNode.x || 0, y: simNode.y || 0 },
                        };
                    })
                );
            });

        setTimeout(() => {
            simulation.stop();
        }, 4000);

        return () => { simulation.stop() }
    }

    // Custom search
    const search = (fields: string | z.infer<typeof searchSchema>) => {
        if (typeof fields === "string") {
            form.setFieldValue("emailSearch", fields)
        } else {
            form.setFieldValue("emailsEndWith", fields.emailsEndWith)
            form.setFieldValue("emailSearch", fields.emailSearch)
            form.setFieldValue("limit", fields.limit)
        }

        form.handleSubmit().catch(() => { return })
    }

    useEffect(() => {
        if (!relationships.isSuccess) {
            return;
        }

        if (relationships.data.length === 0) {
            toast.error("No users found with that email")
            return
        }

        const relationshipData = relationships.data
            .filter(d => d[0] === relationships.data[0]?.[0])

        relationshipData.sort((a, b) => calculateValue(b[1].sentiment, b[1].emailsSent) - calculateValue(a[1].sentiment, a[1].emailsSent))

        const newNodes: Node[] = [{
            id: "1",
            data: {
                label: relationshipData[0]?.[0],
            },
            position: { x: 0, y: 0 },
            type: "emailNode"
        }]

        const newEdges: Edge[] = []

        for (const relation of relationshipData.slice(0, form.state.values.limit)) {
            // Since we can return multiple users, ensure we only choose the ones from the first query we got
            if (relation[0] !== newNodes[0]?.data.label) continue;

            const id = (newNodes.length + 1).toString()
            newNodes.push({
                id,
                data: {
                    label: relation[2],
                    onClick: (data: Record<string, unknown>) => search(data.label as string)
                },
                position: { x: 0, y: 0 },
                type: "emailNode"
            })

            newEdges.push({
                id: `e1-${id}`,
                source: "1",
                target: id,
                data: relation[1],
                type: "emailEdge"
            })
        }


        setNodes(newNodes)
        setEdges(newEdges)
        setNewData(true)
    }, [relationships.data])

    useEffect(() => {
        if (!setNewData) { return }

        setNewData(false)

        return simulate()
    }, [newData])

    return (
        <TooltipProvider>
            <div className="flex-grow h-full gap-4 grid grid-cols-4">
                <ReactFlow
                    colorMode="dark"
                    className="flex-grow h-full text-wrap break-words col-span-3"
                    nodeTypes={nodeTypes}
                    edgeTypes={edgeTypes}
                    nodes={nodes}
                    edges={edges}
                    onNodesChange={onNodesChange}
                    onEdgesChange={onEdgesChange}
                    fitView
                    fitViewOptions={{
                        duration: 1000,
                        maxZoom: 1
                    }}
                    defaultViewport={{ x: 0, y: 0, zoom: 1 }}
                >
                    <Controls />
                    {!isPhone && <MiniMap />}
                    <Background />
                </ReactFlow>
                <div className="px-4 flex flex-col gap-12">
                    <form className="flex-col gap-4 items-center" onSubmit={async (e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        await form.handleSubmit()
                    }}>
                        <h1 className="text-lg font-bold pb-4">User search for graph &quot;{datasetName}&quot;</h1>
                        <form.Field
                            name="limit"
                            children={(field) => (
                                <div className="flex gap-2 flex-col">
                                    <p>Team Size</p>
                                    <Input type="text" value={field.state.value} onChange={(e) => field.handleChange(Number(e.target.value))} placeholder="20" />
                                    <p className="text-xs text-red-400">{field.state.meta.errors[0]?.message}</p>
                                </div>
                            )}
                        />
                        <form.Field
                            name="emailSearch"
                            children={(field) => (
                                <div className="flex gap-2 flex-col">
                                    <p>Email</p>
                                    <Input value={field.state.value} onChange={(e) => field.handleChange(e.target.value)} placeholder="example@example.com" />
                                    <p className="text-xs text-red-400">{field.state.meta.errors[0]?.message}</p>
                                </div>
                            )}
                        />

                        <Accordion type="single" collapsible>
                            <AccordionItem value="Advanced">
                                <AccordionTrigger className="text-stone-400">Advanced options</AccordionTrigger>
                                <AccordionContent className="px-1">
                                    <form.Field
                                        name="emailsEndWith"
                                        children={(field) => (
                                            <div className="flex gap-2 flex-col">
                                                <p>Email ends with</p>
                                                <Input value={field.state.value} onChange={(e) => field.handleChange(e.target.value)} placeholder="example.com" />
                                                <p className="text-xs text-red-400">{field.state.meta.errors[0]?.message}</p>
                                            </div>
                                        )}
                                    />
                                </AccordionContent>
                            </AccordionItem>
                        </Accordion>

                        <div className="mt-2">
                            <Button type="submit" className="hover:cursor-pointer">Search</Button>
                        </div>
                    </form>
                    <div className="flex flex-col gap-4">
                        <div className="flex flex-col">
                            <h1 className="text-lg font-bold">Saved Searches</h1>
                            {savedHistoryApi.isLoading && (
                                <LoaderCircleIcon className="animate-spin mt-4" size={24} />
                            )}
                            {savedHistoryApi.isSuccess && history.length === 0 && (
                                <p className="mt-2 text-gray-400">No saved searches yet!</p>
                            )}
                            {savedHistoryApi.isSuccess && savedHistory.map((itm, idx) => (
                                <div key={idx} className="flex gap-2">
                                    <StarIcon fill={itm.saved ? "#fff" : undefined} onClick={() => saveSearch(itm)} />
                                    <p className="flex gap-2 text-blue-500 hover:underline hover:cursor-pointer" onClick={() => search(itm)}>{itm.emailSearch} ({itm.limit})</p>
                                </div>
                            ))}

                        </div>
                        <div className="flex flex-col">
                            <h1 className="text-lg font-bold">Latest Searches</h1>
                            {searchHistory.isLoading && (
                                <LoaderCircleIcon className="animate-spin mt-4" size={24} />
                            )}
                            {searchHistory.isSuccess && history.length === 0 && (
                                <p className="mt-2 text-gray-400">No searches yet!</p>
                            )}
                            {searchHistory.isSuccess && history.map((itm, idx) => (
                                <div key={idx} className="flex gap-2">
                                    <StarIcon fill={itm.saved ? "#fff" : undefined} onClick={() => saveSearch(itm)} />
                                    <p className="flex gap-2 text-blue-500 hover:underline hover:cursor-pointer" onClick={() => search(itm)}>{itm.emailSearch} ({itm.limit})</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </TooltipProvider>
    );
};

