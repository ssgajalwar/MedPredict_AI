import React from 'react';
import { cn } from '../lib/utils';

const MetricCard = ({ title, value, subtext, icon: Icon, trend, status = 'neutral' }) => {
    const statusStyles = {
        neutral: 'bg-white border-slate-100',
        warning: 'bg-amber-50 border-amber-200',
        critical: 'bg-red-50 border-red-200',
        success: 'bg-emerald-50 border-emerald-200',
    };

    const textStyles = {
        neutral: 'text-slate-500',
        warning: 'text-amber-600',
        critical: 'text-red-600',
        success: 'text-emerald-600',
    };

    return (
        <div className={cn("p-4 rounded-xl border shadow-sm transition-all duration-200 hover:shadow-md", statusStyles[status])}>
            <div className="flex justify-between items-start">
                <div>
                    <p className={cn("text-xs font-medium mb-1", textStyles[status])}>{title}</p>
                    <h3 className="text-xl font-bold text-slate-900">{value}</h3>
                </div>
                {Icon && <Icon className={cn("w-4 h-4 opacity-70", textStyles[status])} />}
            </div>
            {subtext && (
                <div className="mt-3 flex items-center text-xs">
                    {trend && (
                        <span className={cn("font-medium mr-2", trend > 0 ? "text-red-500" : "text-emerald-500")}>
                            {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}%
                        </span>
                    )}
                    <span className="text-slate-400">{subtext}</span>
                </div>
            )}
        </div>
    );
};

export default MetricCard;
