"use client"

import { LoaderCircleIcon, Mail, Users } from "lucide-react"
import {
    Bar,
    BarChart as RechartsBarChart,
    CartesianGrid,
    Cell,
    Legend,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "~/app/_components/ui/card"
import { api } from "~/trpc/react"

const SENTIMENT_COLORS = ["#4ade80", "#f59e0b", "#ef4444"]

export default function EmailSentimentDashboard() {
    const stats = api.graphs.getSentimentStats.useQuery()
    const topCommunicators = api.graphs.getTopCommunicators.useQuery()

    if (stats.isLoading && topCommunicators.isLoading) {
        return (
            <main className="flex-1 flex items-center justify-center min-h-65hv">
                <LoaderCircleIcon className="animate-spin" size={48} />
            </main>
        )
    }

    return (
        <main className="flex-1 space-y-4 p-4 pt-6 md:p-8">
            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight">Email Sentiment Analysis</h1>
                    <p className="text-muted-foreground">
                        Monitor team communication patterns and sentiment based on email analysis
                    </p>
                </div>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Emails Analyzed</CardTitle>
                        <Mail className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.data?.emailsAnalysed.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">From all datasets</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Team Members</CardTitle>
                        <Users className="h-4 w-4 text-muted-foreground" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.data?.chatters.toLocaleString()}</div>
                        <p className="text-xs text-muted-foreground">Active communicators</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Positive Sentiment</CardTitle>
                        <div className="h-4 w-4 rounded-full bg-green-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.data?.sentimentDistribution.positive}%</div>
                        <p className="text-xs text-muted-foreground">Overall positive tone</p>
                    </CardContent>
                </Card>
                <Card>
                    <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Negative Sentiment</CardTitle>
                        <div className="h-4 w-4 rounded-full bg-red-500" />
                    </CardHeader>
                    <CardContent>
                        <div className="text-2xl font-bold">{stats.data?.sentimentDistribution.negative}%</div>
                        <p className="text-xs text-muted-foreground">Overall negative tone</p>
                    </CardContent>
                </Card>
            </div>

            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7">
                <Card className="lg:col-span-3">
                    <CardHeader>
                        <CardTitle>Overall Sentiment Distribution</CardTitle>
                        <CardDescription>Email tone analysis across all team communications</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={Object.entries(stats.data?.sentimentDistribution ?? []).map((e) => ({ name: e[0], value: e[1] }))}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={true}
                                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                    outerRadius={80}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {Object.entries(stats.data?.sentimentDistribution ?? []).map((e) => ({ name: e[0], value: e[1] })).map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={SENTIMENT_COLORS[index % SENTIMENT_COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend />
                            </PieChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
                <Card className="lg:col-span-4">
                    <CardHeader>
                        <CardTitle>Top Communicators</CardTitle>
                        <CardDescription>Team members with highest email volume</CardDescription>
                    </CardHeader>
                    <CardContent className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <RechartsBarChart
                                data={topCommunicators.data ?? []}
                                layout="vertical"
                                margin={{ top: 5, right: 30, left: 200, bottom: 5 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" />
                                <Tooltip />
                                <Legend />
                                <Bar dataKey="emails" fill="#3244dd" />
                            </RechartsBarChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>
            </div>
        </main >
    )
}

