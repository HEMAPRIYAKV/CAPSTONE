import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import { Link, Route, Switch, Router as WouterRouter, useLocation } from 'wouter';
import { useEffect, useMemo, useState } from 'react';
import {
  Activity, AlertCircle, AlertTriangle, ArrowRight, Bell, BrainCircuit, Building2, Check,
  CheckCircle2, ChevronDown, CircleDot, CloudRain, Crosshair, Download, Flame, Gauge,
  HeartPulse, Home as HomeIcon, Layers3, LocateFixed, Map as MapIcon, Menu, MessageSquare,
  Navigation2, Network, PanelLeftClose, PanelLeftOpen, Phone, Play, Radio, RefreshCw,
  Route as RouteIcon, Settings as SettingsIcon, Shield, ShieldAlert, SlidersHorizontal,
  Sparkles, SquareArrowOutUpRight, Target, Thermometer, Users, Waves, Wind, X, Zap
} from 'lucide-react';
import {
  Area, AreaChart, Bar, BarChart, CartesianGrid, Cell, Line, LineChart, Pie, PieChart,
  ResponsiveContainer, Tooltip as ChartTooltip, XAxis, YAxis
} from 'recharts';
import { motion } from 'framer-motion';
import { fetchEvacuationData, fetchLivePrediction } from './api';

const queryClient = new QueryClient();

type Severity = 'critical' | 'high' | 'medium' | 'low';
type AlertItem = { id: number; title: string; location: string; time: string; severity: Severity; state: 'Active' | 'Acknowledged' | 'Resolved'; detail: string };

const alerts: AlertItem[] = [
  { id: 1, title: 'River crest above threshold', location: 'Northbank district', time: '2 min ago', severity: 'critical', state: 'Active', detail: 'Water level projected to reach 4.8m by 18:40. 12,640 residents in impact zone.' },
  { id: 2, title: 'Bridge closure confirmed', location: 'Kestrel Bridge · Route 14', time: '8 min ago', severity: 'high', state: 'Active', detail: 'Structural inspection has closed both lanes. Diversion route is being monitored.' },
  { id: 3, title: 'Shelter intake nearing capacity', location: 'Civic Arena', time: '14 min ago', severity: 'high', state: 'Acknowledged', detail: 'Capacity has reached 82%. Dispatch 2 additional transport units.' },
  { id: 4, title: 'Wind advisory updated', location: 'West ridge corridor', time: '31 min ago', severity: 'medium', state: 'Acknowledged', detail: 'Gusts may exceed 75 km/h after 20:00. Secure temporary structures.' },
  { id: 5, title: 'Power restored', location: 'East industrial zone', time: '46 min ago', severity: 'low', state: 'Resolved', detail: 'Grid operator confirms restoration across all priority facilities.' },
];

const trendData = [
  { time: '12:00', risk: 34, population: 8 }, { time: '13:00', risk: 42, population: 12 },
  { time: '14:00', risk: 48, population: 18 }, { time: '15:00', risk: 57, population: 27 },
  { time: '16:00', risk: 63, population: 35 }, { time: '17:00', risk: 68, population: 43 },
  { time: '18:00', risk: 74, population: 51 },
];

const navItems = [
  { href: '/dashboard', label: 'Command overview', icon: HomeIcon },
  { href: '/prediction', label: 'Predictive intelligence', icon: BrainCircuit },
  { href: '/navigation', label: 'Evacuation navigation', icon: Navigation2 },
  { href: '/simulation', label: 'Live simulation', icon: Activity },
  { href: '/agents', label: 'Agent workflow', icon: Network },
];
const supportItems = [
  { href: '/alerts', label: 'Emergency alerts', icon: Bell, count: 4 },
  { href: '/shelters', label: 'Shelter network', icon: Building2 },
  { href: '/reports', label: 'Operations reports', icon: Download },
  { href: '/settings', label: 'System settings', icon: SettingsIcon },
];

function cx(...classes: Array<string | false | undefined>) { return classes.filter(Boolean).join(' '); }

function SeverityBadge({ severity }: { severity: Severity }) {
  const labels = { critical: 'Critical', high: 'High', medium: 'Advisory', low: 'Informational' };
  return <span className={cx('inline-flex items-center gap-1.5 border px-2 py-1 text-[10px] uppercase tracking-[.14em] font-mono-ui', `severity-${severity}`)}><span className="h-1.5 w-1.5 rounded-full bg-current" />{labels[severity]}</span>;
}

function SectionHeading({ eyebrow, title, action }: { eyebrow: string; title: string; action?: React.ReactNode }) {
  return <div className="mb-5 flex items-end justify-between gap-4"><div><div className="font-mono-ui text-[10px] uppercase tracking-[.22em] text-primary">{eyebrow}</div><h2 className="mt-1 font-display text-3xl uppercase tracking-wide text-foreground">{title}</h2></div>{action}</div>;
}

function StatCard({ label, value, delta, icon: Icon, tone = 'cyan', note }: { label: string; value: string; delta?: string; icon: React.ElementType; tone?: string; note?: string }) {
  return <div className="glass relative overflow-hidden border border-border p-4" data-testid={`stat-${label.toLowerCase().replace(/\s/g, '-')}`}>
    <div className={cx('absolute right-3 top-3 opacity-70', tone === 'red' && 'text-accent', tone === 'gold' && 'text-yellow-300', tone === 'green' && 'text-emerald-300', tone === 'cyan' && 'text-primary')}><Icon size={19} /></div>
    <div className="font-mono-ui text-[10px] uppercase tracking-[.16em] text-muted-foreground">{label}</div>
    <div className="mt-3 flex items-end gap-2"><span className="font-display text-4xl tracking-wide text-foreground">{value}</span>{delta && <span className={cx('mb-1 text-xs font-mono-ui', tone === 'red' ? 'text-accent' : 'text-emerald-300')}>{delta}</span>}</div>
    {note && <div className="mt-1 text-xs text-muted-foreground">{note}</div>}
  </div>;
}

function OperationalMap({ route = false, layers = true }: { route?: boolean; layers?: boolean }) {
  return <div className="scanlines relative min-h-[330px] overflow-hidden border border-border bg-[#0b1a2b]" data-testid="map-operational">
    <div className="absolute left-4 top-4 z-10 border border-border bg-[#0e2235e8] px-3 py-2 backdrop-blur"><div className="font-mono-ui text-[10px] uppercase tracking-[.17em] text-primary">Live geospatial feed</div><div className="mt-1 text-xs text-muted-foreground">Northbank operational sector · 16:42:08 UTC</div></div>
    <svg viewBox="0 0 800 430" className="absolute inset-0 h-full w-full" preserveAspectRatio="none">
      <defs><pattern id="mapgrid" width="42" height="42" patternUnits="userSpaceOnUse"><path d="M 42 0 L 0 0 0 42" fill="none" stroke="#6d9daf" strokeOpacity=".09" /></pattern><filter id="glow"><feGaussianBlur stdDeviation="3" result="coloredBlur"/><feMerge><feMergeNode in="coloredBlur"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
      <rect width="800" height="430" fill="url(#mapgrid)" />
      <path d="M-20 296 C95 248 122 315 203 271 S346 255 411 199 S537 158 624 187 S732 174 820 107" fill="none" stroke="#286b7e" strokeWidth="18" strokeOpacity=".33" />
      <path d="M-20 296 C95 248 122 315 203 271 S346 255 411 199 S537 158 624 187 S732 174 820 107" fill="none" stroke="#67cbd0" strokeWidth="1.5" strokeDasharray="4 7" strokeOpacity=".75" />
      <g fill="none" stroke="#84aab2" strokeOpacity=".4" strokeWidth="2"><path d="M22 96 L198 150 L315 109 L500 141 L778 47" /><path d="M69 390 L122 271 L198 150 L284 22" /><path d="M315 109 L412 198 L462 396" /><path d="M500 141 L620 190 L686 384" /><path d="M412 198 L620 190" /></g>
      <g fill="#9bb5bb" fillOpacity=".17"><path d="M85 54 l142 16 30 83-102 58-86-43z" /><path d="M480 55 l194-13 80 92-54 94-157-29z" /><path d="M201 287 l172-25 62 94-92 55-163-44z" /></g>
      <path d="M126 353 C174 310 214 279 268 262 S370 240 419 201 S513 157 594 178 S685 211 753 116" fill="none" stroke="#e95763" strokeWidth="3" strokeDasharray={route ? '10 7' : '2 12'} filter="url(#glow)" />
      {route && <><circle cx="126" cy="353" r="7" fill="#66dfe1" /><circle cx="753" cy="116" r="7" fill="#e95763" /><circle cx="126" cy="353" r="17" fill="none" stroke="#66dfe1" strokeOpacity=".5" className="animate-pulse-soft" /><path d="M126 353 C174 310 214 279 268 262 S370 240 419 201 S513 157 594 178 S685 211 753 116" fill="none" stroke="#66dfe1" strokeWidth="2.5" strokeDasharray="8 12" className="animate-dash" /></>}
      <g>{[[188,128],[316,105],[425,202],[568,178],[677,193],[728,109],[250,300],[350,347]].map(([x,y], i) => <g key={i}><circle cx={x} cy={y} r="5" fill={i < 3 ? '#e95763' : '#f2c75c'} /><circle cx={x} cy={y} r="12" fill="none" stroke={i < 3 ? '#e95763' : '#f2c75c'} strokeOpacity=".3" /></g>)}</g>
    </svg>
    {layers && <div className="absolute bottom-4 right-4 z-10 flex gap-2 text-[10px] font-mono-ui uppercase tracking-wider text-muted-foreground"><span className="flex items-center gap-1.5 border border-border bg-[#0e2235e8] px-2 py-1"><i className="h-2 w-2 rounded-full bg-accent" /> Risk zone</span><span className="flex items-center gap-1.5 border border-border bg-[#0e2235e8] px-2 py-1"><i className="h-2 w-2 rounded-full bg-yellow-300" /> Shelter</span></div>}
    <div className="absolute bottom-4 left-4 z-10 font-mono-ui text-[10px] text-muted-foreground">GRID 42 · 18.533 N / 73.847 E · SCALE 1:12,500</div>
  </div>;
}

function Topbar({ onMenu, title }: { onMenu: () => void; title: string }) {
  return <header className="flex h-[72px] items-center justify-between border-b border-border bg-[#0b192ae8] px-4 md:px-8">
    <div className="flex items-center gap-3"><button className="text-muted-foreground md:hidden" onClick={onMenu} data-testid="button-open-menu"><Menu size={21} /></button><div><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">Operations / Active incident</div><h1 className="font-display text-2xl uppercase tracking-wide">{title}</h1></div></div>
    <div className="flex items-center gap-3"><div className="hidden items-center gap-2 border border-border bg-card px-3 py-2 text-[10px] font-mono-ui uppercase tracking-widest text-muted-foreground sm:flex"><span className="status-dot h-1.5 w-1.5 rounded-full bg-emerald-400 text-emerald-400" /> Systems nominal</div><button className="relative border border-border p-2 text-muted-foreground hover:text-primary" data-testid="button-header-alerts"><Bell size={17}/><span className="absolute -right-1 -top-1 h-3 w-3 bg-accent text-[8px] text-white text-center">4</span></button><div className="hidden border-l border-border pl-3 text-right sm:block"><div className="text-xs font-semibold text-foreground">M. Alvarez</div><div className="font-mono-ui text-[9px] uppercase tracking-widest text-muted-foreground">Incident commander</div></div><div className="flex h-8 w-8 items-center justify-center bg-primary/15 font-display text-sm text-primary">MA</div></div>
  </header>;
}

function Sidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const [location] = useLocation();
  const NavGroup = ({ items }: { items: Array<{ href: string; label: string; icon: React.ElementType; count?: number }> }) => <div className="space-y-1">{items.map(({ href, label, icon: Icon, count }) => <Link key={href} href={href} onClick={onClose} className={cx('group flex items-center gap-3 border-l-2 px-3 py-2.5 text-sm transition-colors', location === href ? 'border-primary bg-primary/10 text-primary' : 'border-transparent text-muted-foreground hover:border-primary/50 hover:bg-secondary hover:text-foreground')} data-testid={`link-${label.toLowerCase().replace(/\s/g, '-')}`}><Icon size={16} strokeWidth={1.8}/><span className="flex-1">{label}</span>{count && <span className="bg-accent px-1.5 py-0.5 text-[9px] font-mono-ui text-white">{count}</span>}</Link>)}</div>;
  return <><div className={cx('fixed inset-0 z-30 bg-black/60 md:hidden', open ? 'block' : 'hidden')} onClick={onClose}/><aside className={cx('fixed inset-y-0 left-0 z-40 flex w-[260px] flex-col border-r border-border bg-[#091625] transition-transform md:static md:translate-x-0', open ? 'translate-x-0' : '-translate-x-full')}>
    <div className="flex h-[72px] items-center justify-between border-b border-border px-5"><Link href="/" className="flex items-center gap-3" data-testid="link-brand"><div className="flex h-9 w-9 items-center justify-center border border-primary/40 bg-primary/10 text-primary"><Crosshair size={20}/></div><div><div className="font-display text-lg tracking-[.08em] text-foreground">INTEGRATED DISASTER</div><div className="font-mono-ui text-[8px] tracking-[.16em] text-primary">INTELLIGENCE & EMERGENCY COORDINATION</div></div></Link><button className="text-muted-foreground md:hidden" onClick={onClose} data-testid="button-close-menu"><X size={18}/></button></div>
    <div className="flex-1 overflow-y-auto p-4"><div className="mb-3 px-3 font-mono-ui text-[9px] uppercase tracking-[.2em] text-muted-foreground">Command center</div><NavGroup items={navItems}/><div className="my-5 border-t border-border"/><div className="mb-3 px-3 font-mono-ui text-[9px] uppercase tracking-[.2em] text-muted-foreground">Coordination</div><NavGroup items={supportItems}/></div>
    <div className="border-t border-border p-4"><div className="mb-3 flex items-center gap-2"><div className="h-2 w-2 rounded-full bg-emerald-400 status-dot text-emerald-400"/><span className="font-mono-ui text-[10px] uppercase tracking-wider text-emerald-300">Command link secure</span></div><div className="border border-border bg-card/50 p-3"><div className="flex justify-between font-mono-ui text-[9px] uppercase text-muted-foreground"><span>Sector 07</span><span className="text-primary">V 2.4.1</span></div><div className="mt-2 h-1 bg-secondary"><div className="h-full w-[87%] bg-primary"/></div></div></div>
  </aside></>;
}

function Shell({ children, title }: { children: React.ReactNode; title: string }) {
  const [menu, setMenu] = useState(false);
  return <div className="min-h-[100dvh] bg-background"><div className="flex min-h-[100dvh]"><Sidebar open={menu} onClose={() => setMenu(false)}/><main className="min-w-0 flex-1"><Topbar onMenu={() => setMenu(true)} title={title}/><div className="p-4 md:p-7 lg:p-8">{children}</div></main></div></div>;
}

function Landing() {
  const [, setLocation] = useLocation();
  const [role, setRole] = useState('Incident commander');
  return <div className="min-h-[100dvh] overflow-hidden bg-[#081321] text-foreground">
    <div className="absolute inset-0 opacity-30" style={{ backgroundImage: 'radial-gradient(circle at 72% 32%, rgba(77,211,220,.18), transparent 27%), radial-gradient(circle at 18% 80%, rgba(233,87,99,.09), transparent 24%)' }}/><div className="relative mx-auto flex min-h-[100dvh] max-w-[1500px] flex-col px-6 py-7 md:px-12">
      <header className="flex items-center justify-between"><Link href="/" className="flex items-center gap-3" data-testid="link-landing-brand"><div className="flex h-10 w-10 items-center justify-center border border-primary/50 bg-primary/10 text-primary"><Crosshair size={23}/></div><div><div className="font-display text-xl tracking-[.08em]">INTEGRATED DISASTER</div><div className="font-mono-ui text-[9px] tracking-[.2em] text-primary">INTELLIGENCE AND EMERGENCY COORDINATION SYSTEM</div></div></Link><div className="hidden items-center gap-6 font-mono-ui text-[10px] uppercase tracking-[.16em] text-muted-foreground md:flex"><span>Government Operations Network</span><span className="flex items-center gap-2 text-emerald-300"><i className="status-dot h-1.5 w-1.5 rounded-full bg-emerald-400 text-emerald-400"/> Secure connection</span></div></header>
      <div className="grid flex-1 items-center gap-14 py-16 lg:grid-cols-[1.05fr_.95fr]"><motion.div initial={{ opacity: 0, y: 18 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .6 }}><div className="mb-5 flex items-center gap-3 font-mono-ui text-[11px] uppercase tracking-[.2em] text-accent"><span className="h-px w-10 bg-accent"/> Sector 07 · Emergency coordination</div><h1 className="max-w-3xl font-display text-[clamp(4.4rem,10vw,9.4rem)] uppercase leading-[.78] tracking-[.02em]">Predict.<br/><span className="text-primary">Protect.</span><br/>Navigate.</h1><p className="mt-8 max-w-xl border-l border-primary/40 pl-5 text-base leading-relaxed text-muted-foreground">A unified command surface for the moments when every decision carries weight. See risk before it arrives, coordinate response, and move people toward safety.</p><div className="mt-10 flex flex-col gap-3 sm:flex-row"><button onClick={() => setLocation('/dashboard')} className="flex items-center justify-center gap-3 bg-primary px-6 py-3.5 text-sm font-bold uppercase tracking-[.12em] text-primary-foreground transition-transform hover:-translate-y-0.5" data-testid="button-enter-command"><span>Enter command center</span><ArrowRight size={17}/></button><button onClick={() => document.getElementById('access')?.scrollIntoView({ behavior: 'smooth' })} className="border border-border px-6 py-3.5 text-sm uppercase tracking-[.12em] text-muted-foreground hover:border-primary hover:text-primary" data-testid="button-access-options">Access options</button></div></motion.div>
        <motion.div initial={{ opacity: 0, scale: .97 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: .7, delay: .15 }} className="relative"><div className="absolute -inset-8 bg-primary/5 blur-3xl"/><div className="glass scanlines relative border border-primary/20 p-4"><div className="flex items-center justify-between border-b border-border pb-3"><div className="font-mono-ui text-[10px] uppercase tracking-[.17em] text-primary">Operational picture</div><div className="font-mono-ui text-[10px] text-muted-foreground">LIVE · 16:42 UTC</div></div><OperationalMap/><div className="grid grid-cols-3 gap-px border-t border-border bg-border"><div className="bg-card p-3"><div className="font-mono-ui text-[9px] uppercase text-muted-foreground">Risk index</div><div className="mt-1 font-display text-3xl text-accent">74<span className="text-base">/100</span></div></div><div className="bg-card p-3"><div className="font-mono-ui text-[9px] uppercase text-muted-foreground">At risk</div><div className="mt-1 font-display text-3xl">51.2K</div></div><div className="bg-card p-3"><div className="font-mono-ui text-[9px] uppercase text-muted-foreground">Shelters</div><div className="mt-1 font-display text-3xl text-primary">18/22</div></div></div></div></motion.div></div>
      <div id="access" className="flex flex-col justify-between gap-4 border-t border-border pt-5 text-xs text-muted-foreground md:flex-row"><div className="font-mono-ui uppercase tracking-wider">Academic prototype · Simulated data · Not a replacement for official instructions</div><div className="flex gap-5 font-mono-ui uppercase tracking-wider"><span>Predictive models</span><span>Route intelligence</span><span>Multi-agent response</span></div></div>
    </div>
  </div>;
}

function Dashboard() {
  return <Shell title="Command overview"><div className="mb-7 flex flex-col justify-between gap-3 lg:flex-row lg:items-end"><div><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-accent">Active incident · Rivercrest event 24-071</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide md:text-5xl">Northbank response picture</h2><p className="mt-2 text-sm text-muted-foreground">Model synchronized 42 seconds ago · Next forecast window in 18 min</p></div><div className="flex items-center gap-2 border border-accent/30 bg-accent/5 px-3 py-2 text-xs text-accent"><AlertTriangle size={15}/> Elevated response posture</div></div>
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4"><StatCard label="Active risk index" value="74" delta="+8.6%" icon={Gauge} tone="red" note="High confidence · rising"/><StatCard label="Population at risk" value="51.2K" delta="+4.1K" icon={Users} tone="gold" note="Within projected 6h impact"/><StatCard label="Roads blocked" value="14" delta="+3" icon={RouteIcon} tone="red" note="6 primary corridors"/><StatCard label="Shelter capacity" value="82%" delta="18 open" icon={Building2} tone="green" note="Network utilization"/></div>
    <div className="mt-6 grid gap-6 xl:grid-cols-[1.35fr_.65fr]"><div className="glass border border-border p-4 md:p-5"><SectionHeading eyebrow="Geospatial command layer" title="Impact and movement" action={<Link href="/navigation" className="flex items-center gap-2 text-xs uppercase tracking-wider text-primary hover:text-foreground" data-testid="link-open-navigation">Open navigation <ArrowRight size={14}/></Link>}/><OperationalMap/></div><div className="space-y-6"><div className="glass border border-border p-4"><SectionHeading eyebrow="Attention queue" title="Priority alerts" action={<Link href="/alerts" className="text-xs text-primary" data-testid="link-view-alerts">View all</Link>}/><div className="space-y-1">{alerts.slice(0, 4).map(a => <div key={a.id} className="flex items-start gap-3 border-b border-border/70 py-3 last:border-0"><div className={cx('mt-1 h-2 w-2 shrink-0 rounded-full', a.severity === 'critical' ? 'bg-accent status-dot text-accent' : a.severity === 'high' ? 'bg-yellow-300' : 'bg-primary')}/><div className="min-w-0 flex-1"><div className="truncate text-sm font-medium">{a.title}</div><div className="mt-1 flex justify-between gap-2 text-[11px] text-muted-foreground"><span>{a.location}</span><span className="font-mono-ui">{a.time}</span></div></div></div>)}</div></div></div></div>
    <div className="mt-6 grid gap-6 lg:grid-cols-[.9fr_1.1fr]"><div className="glass border border-border p-5"><SectionHeading eyebrow="Evacuation operations" title="Movement progress"/><div className="flex items-center justify-between"><div><div className="font-display text-6xl text-primary">63<span className="text-2xl text-muted-foreground">%</span></div><div className="text-sm text-muted-foreground">of priority population routed</div></div><div className="relative h-24 w-24"><svg viewBox="0 0 100 100" className="-rotate-90"><circle cx="50" cy="50" r="41" fill="none" stroke="#20344a" strokeWidth="10"/><circle cx="50" cy="50" r="41" fill="none" stroke="#66dfe1" strokeWidth="10" strokeDasharray="258" strokeDashoffset="95" strokeLinecap="square"/></svg><span className="absolute inset-0 flex items-center justify-center font-mono-ui text-xs text-primary">ON PLAN</span></div></div><div className="mt-7 space-y-4">{[['Northbank → Civic Arena', 78, '12,840 / 16,400'], ['Lowland → Hillcrest School', 52, '7,920 / 15,200'], ['East quay → Central Library', 41, '4,280 / 10,300']].map(([name, val, meta]) => <div key={name as string}><div className="mb-1.5 flex justify-between text-xs"><span>{name}</span><span className="font-mono-ui text-muted-foreground">{meta}</span></div><div className="h-1.5 bg-secondary"><div className="h-full bg-primary" style={{ width: `${val}%` }}/></div></div>)}</div></div><div className="glass border border-border p-5"><SectionHeading eyebrow="Model telemetry" title="Risk trend · next 6 hours" action={<span className="flex items-center gap-2 text-[10px] font-mono-ui uppercase text-muted-foreground"><i className="h-2 w-2 bg-accent"/>Risk <i className="ml-2 h-2 w-2 bg-primary"/>Population</span>}/><div className="h-[225px]"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trendData}><defs><linearGradient id="riskFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#e95763" stopOpacity=".3"/><stop offset="100%" stopColor="#e95763" stopOpacity="0"/></linearGradient></defs><CartesianGrid stroke="#294053" strokeDasharray="2 4" vertical={false}/><XAxis dataKey="time" tick={{ fill: '#728999', fontSize: 10 }} axisLine={false} tickLine={false}/><YAxis yAxisId="left" tick={{ fill: '#728999', fontSize: 10 }} axisLine={false} tickLine={false}/><YAxis yAxisId="right" orientation="right" tick={{ fill: '#728999', fontSize: 10 }} axisLine={false} tickLine={false}/><ChartTooltip contentStyle={{ background: '#102236', border: '1px solid #2b4356', fontSize: 11 }}/><Area yAxisId="left" type="monotone" dataKey="risk" stroke="#e95763" fill="url(#riskFill)" strokeWidth={2}/><Line yAxisId="right" type="monotone" dataKey="population" stroke="#66dfe1" strokeWidth={2} dot={false}/></AreaChart></ResponsiveContainer></div></div></div>
  </Shell>;
}

function Prediction() {
  const [refresh, setRefresh] = useState(0);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadPrediction() {
      setLoading(true);
      setError('');

      try {
        const result = await fetchLivePrediction();

        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError('Unable to retrieve live prediction data');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadPrediction();

    return () => {
      cancelled = true;
    };
  }, [refresh]);

  const prediction = data?.prediction;
  const weather = data?.weather;

  const probability = prediction?.probability ?? 0;
  const risk = prediction?.risk ?? 'UNKNOWN';

  const rainfall7 = weather?.rainfall_7day ?? 0;
  const humidity = weather?.humidity ?? 0;
  const windSpeed = weather?.wind_speed ?? 0;
  const temperature = weather?.temperature ?? 0;

  const signalData: Array<[string, string, number, React.ElementType, string]> = [
    ['7-day rainfall', `${rainfall7} mm`, Math.min(rainfall7, 100), CloudRain, 'primary'],
    ['Humidity', `${humidity}%`, humidity, Waves, 'red'],
    ['Wind velocity', `${windSpeed} km/h`, Math.min(windSpeed, 100), Wind, 'gold'],
    ['Temperature', `${temperature} �C`, Math.min((temperature / 50) * 100, 100), Thermometer, 'red'],
  ];

  return <Shell title="Predictive intelligence">
    <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">
          Prediction agent � XGBoost flood model
        </div>
        <h2 className="mt-1 font-display text-4xl uppercase tracking-wide">
          Damage intelligence
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Live flood probability generated from current weather conditions and the trained XGBoost model.
        </p>
      </div>

      <button
        onClick={() => setRefresh(refresh + 1)}
        className="flex items-center justify-center gap-2 border border-primary/40 px-4 py-2 text-xs uppercase tracking-wider text-primary hover:bg-primary/10"
        data-testid="button-refresh-prediction"
      >
        <RefreshCw size={14} className={loading ? 'animate-spin' : ''}/>
        Recalculate model
      </button>
    </div>

    {error && (
      <div className="mb-6 border border-accent/40 bg-accent/5 p-4 text-sm text-accent">
        {error}
      </div>
    )}

    <div className="grid gap-6 xl:grid-cols-[.8fr_1.2fr]">
      <div className="glass scanlines flex flex-col items-center justify-center border border-accent/30 bg-accent/[.03] p-7 text-center">
        <div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-muted-foreground">
          Projected flood probability
        </div>

        <div className="relative my-8 flex h-52 w-52 items-center justify-center">
          <svg viewBox="0 0 220 220" className="absolute inset-0 -rotate-90">
            <circle
              cx="110"
              cy="110"
              r="94"
              fill="none"
              stroke="#22374b"
              strokeWidth="10"
            />
            <circle
              cx="110"
              cy="110"
              r="94"
              fill="none"
              stroke="#e95763"
              strokeWidth="10"
              strokeDasharray="590"
              strokeDashoffset={590 - (590 * probability / 100)}
              strokeLinecap="square"
              className="transition-all duration-700"
            />
          </svg>

          <div>
            <div className="font-display text-7xl text-accent">
              {loading ? '--' : probability}
              {!loading && <span className="text-3xl">%</span>}
            </div>

            <div className="font-mono-ui text-[10px] uppercase tracking-wider text-muted-foreground">
              Risk {risk}
            </div>
          </div>
        </div>

        <div className="grid w-full grid-cols-3 gap-2 border-t border-border pt-4">
          <div>
            <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
              Model
            </div>
            <div className="mt-1 text-sm">XGBoost</div>
          </div>

          <div>
            <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
              Location
            </div>
            <div className="mt-1 text-sm">Chennai</div>
          </div>

          <div>
            <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
              Status
            </div>
            <div className="mt-1 text-sm">
              {loading ? 'Loading' : 'LIVE'}
            </div>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="glass border border-border p-5">
          <SectionHeading eyebrow="Environmental inputs" title="Signal matrix"/>

          <div className="grid gap-3 sm:grid-cols-2">
            {signalData.map(([label, value, progress, Icon, tone]) => (
              <div
                key={label}
                className="border border-border bg-secondary/40 p-3"
              >
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Icon
                    size={14}
                    className={
                      tone === 'red'
                        ? 'text-accent'
                        : tone === 'gold'
                          ? 'text-yellow-300'
                          : 'text-primary'
                    }
                  />
                  {label}
                </div>

                <div className="mt-2 flex items-baseline justify-between">
                  <span className="font-display text-2xl">
                    {loading ? '--' : value}
                  </span>
                  <span className="font-mono-ui text-[10px] text-muted-foreground">
                    LIVE
                  </span>
                </div>

                <div className="mt-2 h-1 bg-background">
                  <div
                    className={cx(
                      'h-full',
                      tone === 'red'
                        ? 'bg-accent'
                        : tone === 'gold'
                          ? 'bg-yellow-300'
                          : 'bg-primary'
                    )}
                    style={{ width: `${loading ? 0 : progress}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="glass border border-border p-5">
          <SectionHeading
            eyebrow="Model classification"
            title="Current flood risk"
            action={
              <span className="font-mono-ui text-[10px] text-muted-foreground">
                Live XGBoost output
              </span>
            }
          />

          <div className="mt-4 border border-border bg-secondary/40 p-5">
            <div className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">
                Flood probability
              </span>
              <span className="font-display text-3xl text-accent">
                {loading ? '--' : `${probability}%`}
              </span>
            </div>

            <div className="mt-4 h-2 bg-background">
              <div
                className="h-full bg-accent transition-all duration-700"
                style={{ width: `${loading ? 0 : probability}%` }}
              />
            </div>

            <div className="mt-4 flex items-center justify-between text-xs">
              <span className="text-muted-foreground">
                Risk classification
              </span>
              <span className="font-mono-ui text-primary">
                {loading ? 'LOADING' : risk}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div className="mt-6 grid gap-6 md:grid-cols-3">
      <StatCard
        label="1-day rainfall"
        value={loading ? '--' : `${weather?.rainfall_1day ?? 0} mm`}
        icon={CloudRain}
        tone="red"
        note="Live weather input"
      />

      <StatCard
        label="3-day rainfall"
        value={loading ? '--' : `${weather?.rainfall_3day ?? 0} mm`}
        icon={Waves}
        tone="gold"
        note="Live weather input"
      />

      <StatCard
        label="Flood risk"
        value={loading ? '--' : risk}
        icon={ShieldAlert}
        tone="red"
        note="XGBoost classification"
      />
    </div>
  </Shell>;
}
function NavigationPage() {
  const [refresh, setRefresh] = useState(0);
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    let cancelled = false;

    async function loadEvacuation() {
      setLoading(true);
      setError('');

      try {
        const result = await fetchEvacuationData(13.0827, 80.2707, 5000);

        if (!cancelled) {
          setData(result);
        }
      } catch (err) {
        if (!cancelled) {
          setError('Unable to retrieve evacuation recommendation');
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadEvacuation();

    return () => {
      cancelled = true;
    };
  }, [refresh]);

  const prediction = data?.prediction;
  const shelter = data?.shelter;
  const routing = data?.routing;
  const weather = data?.weather;

  const probability = prediction?.probability ?? 0;
  const risk = prediction?.risk ?? 'UNKNOWN';
  const action = prediction?.action ?? 'No evacuation action available';

  const shelterName = shelter?.name ?? 'No shelter recommendation';
  const shelterDistance = shelter?.distance_km;
  const shelterCapacity = shelter?.capacity;
  const availableCapacity = shelter?.available_capacity;
  const occupancyAvailable = shelter?.occupancy_data_available;

  const routeFound = routing?.route_found ?? false;
  const routeNodes = routing?.route_nodes ?? 0;
  const routeCost = routing?.route_cost;
  const route = routing?.route ?? [];

  const routeExposure =
    shelter?.average_flood_exposure ??
    routing?.average_flood_exposure ??
    null;

  const routeRisk =
    routeExposure === null
      ? 'UNKNOWN'
      : routeExposure >= 0.70
        ? 'HIGH'
        : routeExposure >= 0.30
          ? 'MEDIUM'
          : 'LOW';

  return <Shell title="Evacuation navigation">
    <div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end">
      <div>
        <div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">
          Evacuation agent � Risk-aware routing
        </div>
        <h2 className="mt-1 font-display text-4xl uppercase tracking-wide">
          Safe movement
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Recommended evacuation route based on flood probability, road exposure, and GCC relief-centre data.
        </p>
      </div>

      <button
        onClick={() => setRefresh(refresh + 1)}
        className="flex items-center justify-center gap-2 border border-primary/40 px-4 py-2 text-xs uppercase tracking-wider text-primary hover:bg-primary/10"
      >
        <RefreshCw size={14} className={loading ? 'animate-spin' : ''}/>
        Recalculate route
      </button>
    </div>

    {error && (
      <div className="mb-6 border border-accent/40 bg-accent/5 p-4 text-sm text-accent">
        {error}
      </div>
    )}

    <div className="grid gap-6 xl:grid-cols-[1.2fr_.8fr]">
      <div className="glass border border-border p-5">
        <SectionHeading
          eyebrow="Recommended evacuation route"
          title="Risk-aware A* navigation"
          action={
            <span className="font-mono-ui text-[10px] text-primary">
              {loading ? 'CALCULATING' : routeFound ? 'ROUTE FOUND' : 'NO ROUTE'}
            </span>
          }
        />

        <div className="mt-5 border border-border bg-secondary/40 p-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center border border-primary/30 bg-primary/5 text-primary">
              <Navigation2 size={18}/>
            </div>

            <div>
              <div className="font-mono-ui text-[9px] uppercase tracking-wider text-muted-foreground">
                Current location
              </div>
              <div className="mt-1 text-sm">
                Chennai command location
              </div>
            </div>
          </div>

          <div className="my-5 ml-5 h-8 border-l border-dashed border-primary/40"/>

          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center border border-accent/30 bg-accent/5 text-accent">
              <Building2 size={18}/>
            </div>

            <div>
              <div className="font-mono-ui text-[9px] uppercase tracking-wider text-muted-foreground">
                Recommended shelter
              </div>
              <div className="mt-1 text-sm font-medium">
                {loading ? 'Calculating...' : shelterName}
              </div>
            </div>
          </div>
        </div>

        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <div className="border border-border bg-secondary/40 p-4">
            <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
              Distance
            </div>
            <div className="mt-2 font-display text-2xl">
              {loading || shelterDistance == null
                ? '--'
                : `${shelterDistance} km`}
            </div>
          </div>

          <div className="border border-border bg-secondary/40 p-4">
            <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
              Route exposure
            </div>
            <div className="mt-2 font-display text-2xl">
              {loading || routeExposure == null
                ? '--'
                : routeExposure.toFixed(2)}
            </div>
          </div>

          <div className="border border-border bg-secondary/40 p-4">
            <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
              Route risk
            </div>
            <div className="mt-2 font-display text-2xl">
              {loading ? '--' : routeRisk}
            </div>
          </div>
        </div>

        <div className="mt-4 border border-border bg-secondary/40 p-4">
          <div className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              Route nodes
            </span>
            <span className="font-mono-ui text-xs text-primary">
              {loading ? '--' : routeNodes}
            </span>
          </div>

          <div className="mt-3 flex items-center justify-between">
            <span className="text-xs text-muted-foreground">
              Routing cost
            </span>
            <span className="font-mono-ui text-xs">
              {loading || routeCost == null ? '--' : routeCost}
            </span>
          </div>

          <div className="mt-3 text-[11px] text-muted-foreground">
            High-risk road segments receive increased routing cost so the A* algorithm can prefer lower-exposure alternatives where available.
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <div className="glass border border-border p-5">
          <SectionHeading
            eyebrow="Flood intelligence"
            title="Current evacuation status"
          />

          <div className="mt-4 border border-accent/30 bg-accent/[.03] p-5">
            <div className="flex items-center justify-between">
              <span className="font-mono-ui text-[10px] uppercase text-muted-foreground">
                Flood probability
              </span>
              <span className="font-display text-3xl text-accent">
                {loading ? '--' : `${probability}%`}
              </span>
            </div>

            <div className="mt-4 h-2 bg-background">
              <div
                className="h-full bg-accent transition-all duration-700"
                style={{ width: `${loading ? 0 : probability}%` }}
              />
            </div>

            <div className="mt-4 flex items-center justify-between">
              <span className="text-xs text-muted-foreground">
                Risk level
              </span>
              <span className="font-mono-ui text-xs text-primary">
                {loading ? 'LOADING' : risk}
              </span>
            </div>
          </div>

          <div className="mt-4 border border-border bg-secondary/40 p-4">
            <div className="flex gap-3">
              <AlertTriangle size={16} className="mt-0.5 text-accent"/>
              <div>
                <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
                  Recommended action
                </div>
                <div className="mt-1 text-sm">
                  {loading ? 'Calculating...' : action}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="glass border border-border p-5">
          <SectionHeading
            eyebrow="Shelter intelligence"
            title="Relief-centre status"
          />

          <div className="grid gap-3 sm:grid-cols-2">
            <div className="border border-border bg-secondary/40 p-4">
              <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
                Shelter capacity
              </div>
              <div className="mt-2 font-display text-2xl">
                {loading || shelterCapacity == null
                  ? '--'
                  : shelterCapacity}
              </div>
              <div className="mt-1 text-[10px] text-muted-foreground">
                GCC reported capacity
              </div>
            </div>

            <div className="border border-border bg-secondary/40 p-4">
              <div className="font-mono-ui text-[9px] uppercase text-muted-foreground">
                Occupancy
              </div>
              <div className="mt-2 font-display text-2xl">
                {loading
                  ? '--'
                  : occupancyAvailable && availableCapacity != null
                    ? availableCapacity
                    : 'Unknown'}
              </div>
              <div className="mt-1 text-[10px] text-muted-foreground">
                {occupancyAvailable
                  ? 'GCC occupancy information'
                  : 'GCC occupancy not reported'}
              </div>
            </div>
          </div>
        </div>

        <div className="glass border border-border p-5">
          <SectionHeading
            eyebrow="Weather inputs"
            title="Live conditions"
          />

          <div className="grid grid-cols-3 gap-2">
            <div className="border border-border bg-secondary/40 p-3 text-center">
              <CloudRain size={14} className="mx-auto text-primary"/>
              <div className="mt-2 font-display text-lg">
                {weather?.rainfall_1day ?? '--'}
              </div>
              <div className="font-mono-ui text-[8px] uppercase text-muted-foreground">
                1-day mm
              </div>
            </div>

            <div className="border border-border bg-secondary/40 p-3 text-center">
              <Waves size={14} className="mx-auto text-primary"/>
              <div className="mt-2 font-display text-lg">
                {weather?.rainfall_3day ?? '--'}
              </div>
              <div className="font-mono-ui text-[8px] uppercase text-muted-foreground">
                3-day mm
              </div>
            </div>

            <div className="border border-border bg-secondary/40 p-3 text-center">
              <CloudRain size={14} className="mx-auto text-primary"/>
              <div className="mt-2 font-display text-lg">
                {weather?.rainfall_7day ?? '--'}
              </div>
              <div className="font-mono-ui text-[8px] uppercase text-muted-foreground">
                7-day mm
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div className="mt-6 glass border border-border p-5">
      <SectionHeading
        eyebrow="Dynamic routing"
        title="Route adaptation"
        action={
          <span className="font-mono-ui text-[10px] text-muted-foreground">
            Backend routing engine
          </span>
        }
      />

      <div className="mt-4 grid gap-3 md:grid-cols-3">
        <div className="border border-border bg-secondary/40 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <RouteIcon size={14} className="text-primary"/>
            Current route
          </div>
          <div className="mt-2 text-sm">
            {loading
              ? 'Calculating...'
              : routeFound
                ? 'Active risk-aware route'
                : 'No route available'}
          </div>
        </div>

        <div className="border border-border bg-secondary/40 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <RefreshCw size={14} className="text-primary"/>
            Recalculation
          </div>
          <div className="mt-2 text-sm">
            Manual refresh available
          </div>
        </div>

        <div className="border border-border bg-secondary/40 p-4">
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <ShieldAlert size={14} className="text-accent"/>
            Risk avoidance
          </div>
          <div className="mt-2 text-sm">
            High-exposure segments penalized
          </div>
        </div>
      </div>
    </div>
  </Shell>;
}
function Simulation() {
  const [type, setType] = useState('Flood'); const [intensity, setIntensity] = useState(68); const [running, setRunning] = useState(true);
  const types: Array<{ label: string; icon: React.ElementType }> = [{ label: 'Flood', icon: Waves }, { label: 'Cyclone', icon: Wind }, { label: 'Earthquake', icon: Activity }, { label: 'Landslide', icon: MountainIcon }, { label: 'Wildfire', icon: Flame }];
  return <Shell title="Live simulation"><div className="mb-7 flex flex-col justify-between gap-4 lg:flex-row lg:items-end"><div><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-accent">Simulation lab · sandbox controls</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide">Stress the response</h2><p className="mt-2 text-sm text-muted-foreground">Adjust scenario conditions and observe how the operational picture changes.</p></div><button onClick={() => setRunning(!running)} className={cx('flex items-center justify-center gap-2 border px-4 py-2 text-xs uppercase tracking-wider', running ? 'border-accent/50 text-accent' : 'border-primary text-primary')} data-testid="button-toggle-simulation">{running ? <><span className="h-2 w-2 bg-accent animate-pulse-soft"/> Simulation running</> : <><Play size={14}/> Resume simulation</>}</button></div>
    <div className="grid gap-6 xl:grid-cols-[.66fr_1.34fr]"><div className="glass border border-border p-5"><SectionHeading eyebrow="Scenario control" title="Select event"/><div className="grid grid-cols-2 gap-2">{types.map(({ label, icon: Icon }) => <button key={label} onClick={() => setType(label)} className={cx('flex items-center gap-2 border p-3 text-left text-xs transition-colors', type === label ? 'border-primary bg-primary/10 text-primary' : 'border-border text-muted-foreground hover:border-primary/50')} data-testid={`button-scenario-${label.toLowerCase()}`}><Icon size={15}/>{label}</button>)}</div><div className="mt-7 border-t border-border pt-5"><div className="mb-3 flex justify-between"><span className="font-mono-ui text-[10px] uppercase tracking-wider text-muted-foreground">Event intensity</span><span className="font-display text-2xl text-accent">{intensity}<span className="text-sm">%</span></span></div><input type="range" min="10" max="100" value={intensity} onChange={e => setIntensity(Number(e.target.value))} className="w-full accent-[#e95763]" data-testid="input-event-intensity"/><div className="mt-2 flex justify-between font-mono-ui text-[9px] text-muted-foreground"><span>Nominal</span><span>Severe</span><span>Catastrophic</span></div></div><div className="mt-6 grid grid-cols-2 gap-3"><div className="border border-border bg-secondary/40 p-3"><div className="font-mono-ui text-[9px] uppercase text-muted-foreground">Rainfall</div><div className="mt-1 font-display text-2xl">{Math.round(intensity * 1.24)} mm/h</div></div><div className="border border-border bg-secondary/40 p-3"><div className="font-mono-ui text-[9px] uppercase text-muted-foreground">Duration</div><div className="mt-1 font-display text-2xl">{Math.round(intensity / 14 + 2.3)} hrs</div></div></div></div><div className="space-y-6"><div className="glass border border-border p-4"><SectionHeading eyebrow={`Scenario: ${type} · ${running ? 'live' : 'paused'}`} title="Projected impact"/><OperationalMap/><div className="mt-4 grid gap-3 sm:grid-cols-3"><StatCard label="Risk index" value={String(Math.min(99, intensity + 8))} delta="+12" icon={Gauge} tone="red"/><StatCard label="Roads affected" value={String(Math.round(intensity / 4.2))} delta="+4" icon={RouteIcon} tone="gold"/><StatCard label="At-risk residents" value={`${(intensity * .81).toFixed(1)}K`} delta="+8.3%" icon={Users} tone="red"/></div></div><div className="glass border border-border p-5"><SectionHeading eyebrow="Simulation telemetry" title="Response curve"/><div className="h-[160px]"><ResponsiveContainer width="100%" height="100%"><LineChart data={trendData.map((d, i) => ({ ...d, simulated: Math.min(100, d.risk + intensity / 5 + i * 1.5) }))}><CartesianGrid stroke="#294053" strokeDasharray="2 4" vertical={false}/><XAxis dataKey="time" tick={{ fill: '#849aa5', fontSize: 10 }} axisLine={false} tickLine={false}/><YAxis domain={[0,100]} tick={{ fill: '#849aa5', fontSize: 10 }} axisLine={false} tickLine={false}/><ChartTooltip contentStyle={{ background: '#102236', border: '1px solid #2b4356', fontSize: 11 }}/><Line type="monotone" dataKey="simulated" stroke="#e95763" strokeWidth={2} dot={false}/><Line type="monotone" dataKey="risk" stroke="#66dfe1" strokeWidth={2} dot={false} strokeDasharray="4 4"/></LineChart></ResponsiveContainer></div></div></div></div>
  </Shell>;
}

function MountainIcon(props: { size?: number }) { return <Activity {...props}/>; }

function Agents() {
  const agents = [{ name: 'Prediction agent', role: 'Forecasts hazard impact', icon: BrainCircuit, status: 'Running', metric: '94.2%', color: 'cyan', detail: 'Processing rainfall and river gauge signals' }, { name: 'Damage intelligence', role: 'Maps structural exposure', icon: Building2, status: 'Running', metric: '8,440', color: 'red', detail: 'Grid cells classified in last cycle' }, { name: 'Navigation agent', role: 'Finds safest movement', icon: Navigation2, status: 'Running', metric: '18', color: 'cyan', detail: 'Routes recalculated across sector 07' }, { name: 'Decision agent', role: 'Coordinates action', icon: Shield, status: 'Standby', metric: '06', color: 'gold', detail: 'Recommended actions awaiting review' }];
  return <Shell title="Agent workflow"><div className="mb-7"><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">Multi-agent orchestration · synchronized</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide">Response intelligence mesh</h2><p className="mt-2 text-sm text-muted-foreground">Four specialized agents work in sequence, sharing one operational picture.</p></div><div className="relative grid gap-4 lg:grid-cols-4">{agents.map(({ name, role, icon: Icon, status, metric, color, detail }, index) => <div key={name} className="relative"><div className={cx('glass h-full border p-5', color === 'red' ? 'border-accent/40' : color === 'gold' ? 'border-yellow-300/30' : 'border-primary/30')}><div className="flex items-center justify-between"><div className={cx('flex h-10 w-10 items-center justify-center border', color === 'red' ? 'border-accent/40 bg-accent/10 text-accent' : color === 'gold' ? 'border-yellow-300/40 bg-yellow-300/10 text-yellow-300' : 'border-primary/40 bg-primary/10 text-primary')}><Icon size={20}/></div><span className={cx('flex items-center gap-1.5 font-mono-ui text-[9px] uppercase', status === 'Running' ? 'text-emerald-300' : 'text-yellow-300')}><i className={cx('h-1.5 w-1.5 rounded-full', status === 'Running' ? 'bg-emerald-400 status-dot text-emerald-400' : 'bg-yellow-300')}/>{status}</span></div><div className="mt-6 font-display text-2xl uppercase">{name}</div><div className="mt-1 text-xs text-muted-foreground">{role}</div><div className={cx('mt-6 font-display text-4xl', color === 'red' ? 'text-accent' : color === 'gold' ? 'text-yellow-300' : 'text-primary')}>{metric}</div><div className="mt-1 text-[11px] text-muted-foreground">{detail}</div><div className="mt-5 flex items-center gap-2 border-t border-border pt-3 font-mono-ui text-[9px] uppercase tracking-wider text-muted-foreground"><Activity size={12}/> Last cycle 42 sec ago</div></div>{index < 3 && <ArrowRight className="absolute -right-4 top-1/2 z-10 hidden text-primary lg:block" size={20}/>}</div>)}</div><div className="mt-6 grid gap-6 lg:grid-cols-[1.1fr_.9fr]"><div className="glass border border-border p-5"><SectionHeading eyebrow="Agent transcript" title="Latest decisions"/><div className="space-y-4">{['Prediction agent raised Northbank impact probability to 78%.','Damage intelligence marked Kestrel Bridge as non-passable.','Navigation agent promoted Route A after flood depth update.','Decision agent recommends opening Civic Arena overflow intake.'].map((item, i) => <div key={item} className="flex gap-3 border-l border-primary/40 pl-3"><span className="font-mono-ui text-[10px] text-primary">0{i + 1}</span><div><div className="text-sm">{item}</div><div className="mt-1 font-mono-ui text-[9px] uppercase text-muted-foreground">{i + 1} min ago · confidence {91 - i * 3}%</div></div></div>)}</div></div><div className="glass border border-border p-5"><SectionHeading eyebrow="System health" title="Mesh integrity"/><div className="flex items-center gap-6"><div className="relative h-28 w-28"><svg viewBox="0 0 100 100" className="-rotate-90"><circle cx="50" cy="50" r="39" fill="none" stroke="#20344a" strokeWidth="9"/><circle cx="50" cy="50" r="39" fill="none" stroke="#66dfe1" strokeWidth="9" strokeDasharray="245" strokeDashoffset="12" /></svg><span className="absolute inset-0 flex items-center justify-center font-display text-2xl text-primary">95%</span></div><div className="space-y-2 text-xs"><div className="flex gap-2"><CheckCircle2 size={14} className="text-emerald-300"/> Inference latency nominal</div><div className="flex gap-2"><CheckCircle2 size={14} className="text-emerald-300"/> Data streams healthy</div><div className="flex gap-2"><AlertCircle size={14} className="text-yellow-300"/> Decision review queue: 6</div></div></div></div></div></Shell>;
}

function AlertsPage() {
  const [items, setItems] = useState(alerts); const [filter, setFilter] = useState('All');
  const filtered = filter === 'All' ? items : items.filter(a => a.severity === filter.toLowerCase() || a.state === filter);
  const acknowledge = (id: number) => setItems(prev => prev.map(a => a.id === id ? { ...a, state: 'Acknowledged' } : a));
  return <Shell title="Emergency alerts"><div className="mb-7 flex flex-col justify-between gap-4 md:flex-row md:items-end"><div><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-accent">Alert desk · 4 require attention</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide">Emergency signal queue</h2><p className="mt-2 text-sm text-muted-foreground">Incoming alerts from field units, sensors, and partner agencies.</p></div><button className="flex items-center justify-center gap-2 border border-primary/40 px-4 py-2 text-xs uppercase tracking-wider text-primary" data-testid="button-refresh-alerts"><RefreshCw size={14}/> Sync signals</button></div><div className="mb-4 flex gap-2 overflow-x-auto border-b border-border pb-3">{['All','Critical','High','Acknowledged','Resolved'].map(item => <button key={item} onClick={() => setFilter(item)} className={cx('whitespace-nowrap px-3 py-2 text-xs uppercase tracking-wider', filter === item ? 'bg-primary text-primary-foreground' : 'text-muted-foreground hover:text-foreground')} data-testid={`button-filter-${item.toLowerCase()}`}>{item}</button>)}</div><div className="space-y-3">{filtered.map(a => <div key={a.id} className={cx('glass flex flex-col gap-4 border p-4 md:flex-row md:items-center', a.severity === 'critical' ? 'border-accent/50' : 'border-border')} data-testid={`alert-card-${a.id}`}><div className={cx('flex h-10 w-10 shrink-0 items-center justify-center border', a.severity === 'critical' ? 'border-accent/40 bg-accent/10 text-accent' : a.severity === 'high' ? 'border-yellow-300/40 bg-yellow-300/10 text-yellow-300' : 'border-primary/40 bg-primary/10 text-primary')}>{a.severity === 'critical' ? <AlertTriangle size={19}/> : <Radio size={19}/>}</div><div className="min-w-0 flex-1"><div className="mb-2 flex flex-wrap items-center gap-2"><SeverityBadge severity={a.severity}/><span className={cx('font-mono-ui text-[10px] uppercase', a.state === 'Resolved' ? 'text-emerald-300' : a.state === 'Acknowledged' ? 'text-primary' : 'text-accent')}>{a.state}</span></div><div className="text-base font-semibold">{a.title}</div><div className="mt-1 text-xs text-muted-foreground">{a.location} · {a.time}</div><div className="mt-2 text-xs leading-relaxed text-muted-foreground">{a.detail}</div></div><div className="flex shrink-0 gap-2">{a.state === 'Active' && <button onClick={() => acknowledge(a.id)} className="flex items-center gap-2 border border-primary/50 px-3 py-2 text-xs uppercase tracking-wider text-primary hover:bg-primary/10" data-testid={`button-acknowledge-${a.id}`}><Check size={14}/> Acknowledge</button>}<button className="border border-border px-3 py-2 text-xs text-muted-foreground hover:text-foreground" data-testid={`button-alert-detail-${a.id}`}>Details</button></div></div>)}</div></Shell>;
}

function Shelters() {
  const shelters = [{ name: 'Civic Arena', district: 'Northbank', capacity: 12000, occupied: 9840, status: 'Open' }, { name: 'Hillcrest School', district: 'West ridge', capacity: 8200, occupied: 4280, status: 'Open' }, { name: 'Central Library', district: 'East quay', capacity: 5600, occupied: 4010, status: 'Open' }, { name: 'St. Agnes Community Hall', district: 'Lowland', capacity: 3400, occupied: 3320, status: 'Near capacity' }, { name: 'Upland Sports Complex', district: 'Upland', capacity: 15000, occupied: 920, status: 'Open' }];
  return <Shell title="Shelter network"><div className="mb-7"><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">Shelter network · capacity monitoring</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide">Places of safety</h2><p className="mt-2 text-sm text-muted-foreground">Live intake, resources, and accessibility across the response network.</p></div><div className="grid gap-3 sm:grid-cols-3"><StatCard label="Total capacity" value="40.2K" icon={Building2} note="5 facilities online"/><StatCard label="Occupied now" value="22.4K" delta="55.7%" icon={Users} tone="gold" note="17,780 places remaining"/><StatCard label="Transport units" value="28" delta="6 active" icon={Navigation2} tone="green" note="Next dispatch 16:50"/></div><div className="mt-6 grid gap-6 xl:grid-cols-[1.15fr_.85fr]"><div className="glass border border-border p-5"><SectionHeading eyebrow="Facility status" title="Shelter capacity"/><div className="overflow-x-auto"><table className="w-full min-w-[580px] text-left"><thead><tr className="border-b border-border font-mono-ui text-[9px] uppercase tracking-wider text-muted-foreground"><th className="pb-3">Facility</th><th className="pb-3">District</th><th className="pb-3">Occupancy</th><th className="pb-3">Status</th><th className="pb-3 text-right">Action</th></tr></thead><tbody>{shelters.map((s, i) => <tr key={s.name} className="border-b border-border/70 text-xs last:border-0"><td className="py-4 font-medium">{s.name}</td><td className="py-4 text-muted-foreground">{s.district}</td><td className="py-4"><div className="flex items-center gap-3"><div className="h-1.5 w-20 bg-secondary"><div className={cx('h-full', s.occupied / s.capacity > .9 ? 'bg-accent' : 'bg-primary')} style={{ width: `${s.occupied / s.capacity * 100}%` }}/></div><span className="font-mono-ui text-[10px]">{Math.round(s.occupied / s.capacity * 100)}%</span></div></td><td className={s.status === 'Near capacity' ? 'text-accent' : 'text-emerald-300'}>{s.status}</td><td className="py-4 text-right"><button className="text-primary hover:text-foreground" data-testid={`button-shelter-${i}`}>View</button></td></tr>)}</tbody></table></div></div><div className="glass border border-border p-5"><SectionHeading eyebrow="Network distribution" title="Shelter map"/><OperationalMap layers={false}/></div></div></Shell>;
}

function Reports() {
  const [generated, setGenerated] = useState<string | null>(null);
  const reports = [{ title: 'Northbank impact forecast', type: 'Prediction report', time: 'Updated 16:40', icon: BrainCircuit }, { title: 'Sector 07 structural exposure', type: 'Damage intelligence', time: 'Updated 16:37', icon: Building2 }, { title: 'Priority evacuation movement', type: 'Navigation report', time: 'Updated 16:31', icon: Navigation2 }];
  return <Shell title="Operations reports"><div className="mb-7"><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">Reports desk · incident 24-071</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide">Evidence for action</h2><p className="mt-2 text-sm text-muted-foreground">Generate a clean operational brief for command, partners, and field teams.</p></div><div className="grid gap-4 md:grid-cols-3">{reports.map(({ title, type, time, icon: Icon }) => <div key={title} className="glass flex min-h-[240px] flex-col border border-border p-5"><div className="flex items-start justify-between"><div className="flex h-10 w-10 items-center justify-center border border-primary/30 bg-primary/10 text-primary"><Icon size={19}/></div><span className="font-mono-ui text-[9px] uppercase text-muted-foreground">PDF / CSV</span></div><div className="mt-8 font-display text-2xl uppercase">{title}</div><div className="mt-1 text-xs text-muted-foreground">{type} · {time}</div><div className="mt-auto flex gap-2 pt-7"><button onClick={() => setGenerated(title)} className="flex flex-1 items-center justify-center gap-2 bg-primary py-2.5 text-xs font-bold uppercase tracking-wider text-primary-foreground" data-testid={`button-generate-${type.toLowerCase().replace(/\s/g, '-')}`}><Sparkles size={14}/> Generate</button><button className="border border-border px-3 text-muted-foreground hover:text-primary" data-testid={`button-download-${type.toLowerCase().replace(/\s/g, '-')}`}><Download size={15}/></button></div></div>)}</div>{generated && <div className="mt-6 flex items-center justify-between border border-emerald-400/30 bg-emerald-400/5 p-4 text-sm text-emerald-200" data-testid="status-report-generated"><div className="flex items-center gap-2"><CheckCircle2 size={17}/> {generated} is ready for download.</div><button onClick={() => setGenerated(null)} className="text-muted-foreground hover:text-foreground" data-testid="button-dismiss-report"><X size={16}/></button></div>}<div className="mt-6 glass border border-border p-5"><SectionHeading eyebrow="Report archive" title="Recent exports"/><div className="divide-y divide-border">{['Command brief · Rivercrest event 24-071', 'Partner agency handoff · Shelter capacity', 'Field unit packet · Route A evacuation'].map((item, i) => <div key={item} className="flex flex-col justify-between gap-3 py-4 text-sm sm:flex-row sm:items-center"><div className="flex items-center gap-3"><Download size={15} className="text-primary"/><span>{item}</span></div><div className="flex items-center gap-4 text-xs text-muted-foreground"><span className="font-mono-ui">{['16:12','15:48','14:20'][i]} UTC</span><button className="text-primary" data-testid={`button-archive-download-${i}`}>Download</button></div></div>)}</div></div></Shell>;
}

function SettingsPage() {
  const [dark, setDark] = useState(true); const [layers, setLayers] = useState({ risk: true, shelters: true, roads: true }); const [notifications, setNotifications] = useState(true);
  useEffect(() => { document.documentElement.classList.toggle('dark', dark); }, [dark]);
  return <Shell title="System settings"><div className="mb-7"><div className="font-mono-ui text-[10px] uppercase tracking-[.2em] text-primary">Configuration · operator preferences</div><h2 className="mt-1 font-display text-4xl uppercase tracking-wide">Command settings</h2><p className="mt-2 text-sm text-muted-foreground">Tune your operational surface without changing the shared incident picture.</p></div><div className="grid gap-6 lg:grid-cols-2"><div className="glass border border-border p-5"><SectionHeading eyebrow="Interface" title="Display mode"/><div className="flex items-center justify-between border-b border-border py-4"><div><div className="text-sm">Dark command mode</div><div className="mt-1 text-xs text-muted-foreground">Optimized for low-light operations rooms.</div></div><button onClick={() => setDark(!dark)} className={cx('relative h-6 w-11 border transition-colors', dark ? 'border-primary bg-primary/20' : 'border-border bg-secondary')} data-testid="switch-dark-mode"><span className={cx('absolute top-1 h-4 w-4 bg-primary transition-transform', dark ? 'left-6' : 'left-1')}/></button></div><div className="flex items-center justify-between py-4"><div><div className="text-sm">Push notifications</div><div className="mt-1 text-xs text-muted-foreground">Critical and high-severity alerts only.</div></div><button onClick={() => setNotifications(!notifications)} className={cx('relative h-6 w-11 border transition-colors', notifications ? 'border-primary bg-primary/20' : 'border-border bg-secondary')} data-testid="switch-notifications"><span className={cx('absolute top-1 h-4 w-4 bg-primary transition-transform', notifications ? 'left-6' : 'left-1')}/></button></div></div><div className="glass border border-border p-5"><SectionHeading eyebrow="Map configuration" title="Visible layers"/>{Object.entries(layers).map(([key, value]) => <div key={key} className="flex items-center justify-between border-b border-border py-4 last:border-0"><div className="flex items-center gap-3"><Layers3 size={16} className="text-primary"/><span className="text-sm capitalize">{key} layer</span></div><button onClick={() => setLayers(prev => ({ ...prev, [key]: !value }))} className={cx('relative h-6 w-11 border transition-colors', value ? 'border-primary bg-primary/20' : 'border-border bg-secondary')} data-testid={`switch-layer-${key}`}><span className={cx('absolute top-1 h-4 w-4 bg-primary transition-transform', value ? 'left-6' : 'left-1')}/></button></div>)}</div><div className="glass border border-border p-5"><SectionHeading eyebrow="Escalation" title="Emergency contacts"/>{[['Regional command', '+1 555 014 7712'],['Fire and rescue desk', '+1 555 014 3340'],['Medical coordination', '+1 555 014 8891']].map(([name, phone]) => <div key={name} className="flex items-center justify-between border-b border-border py-4 last:border-0"><div><div className="text-sm">{name}</div><div className="mt-1 font-mono-ui text-xs text-muted-foreground">{phone}</div></div><button className="flex items-center gap-2 border border-primary/40 px-3 py-2 text-xs text-primary" data-testid={`button-call-${name.toLowerCase().replace(/\s/g, '-')}`}><Phone size={13}/> Call</button></div>)}</div><div className="glass border border-border p-5"><SectionHeading eyebrow="Access control" title="Operator identity"/><div className="space-y-4"><div className="flex items-center gap-3 border-b border-border pb-4"><div className="flex h-10 w-10 items-center justify-center bg-primary/15 font-display text-primary">MA</div><div><div className="text-sm font-semibold">M. Alvarez</div><div className="font-mono-ui text-[10px] uppercase tracking-wider text-muted-foreground">Incident commander · Sector 07</div></div></div><div className="flex justify-between text-xs"><span className="text-muted-foreground">Last authenticated</span><span className="font-mono-ui">16:02:14 UTC</span></div><div className="flex justify-between text-xs"><span className="text-muted-foreground">Clearance</span><span className="text-emerald-300">Level 04 · Active</span></div></div></div></div></Shell>;
}

function PageRouter() {
  return <Switch><Route path="/" component={Landing}/><Route path="/dashboard" component={Dashboard}/><Route path="/prediction" component={Prediction}/><Route path="/navigation" component={NavigationPage}/><Route path="/simulation" component={Simulation}/><Route path="/agents" component={Agents}/><Route path="/alerts" component={AlertsPage}/><Route path="/shelters" component={Shelters}/><Route path="/reports" component={Reports}/><Route path="/settings" component={SettingsPage}/><Route component={() => <Shell title="Unknown route"><div className="glass border border-border p-10"><h2 className="font-display text-5xl">404 / NOT FOUND</h2><Link href="/dashboard" className="mt-5 inline-flex items-center gap-2 text-primary" data-testid="link-return-dashboard">Return to command overview <ArrowRight size={15}/></Link></div></Shell>}/></Switch>;
}

function App() {
  return <QueryClientProvider client={queryClient}><TooltipProvider><WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}><PageRouter/></WouterRouter><Toaster/></TooltipProvider></QueryClientProvider>;
}

export default App;











