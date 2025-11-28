import React from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { cn } from '../lib/utils';

const ColorfulMetricCard = ({ title, value, change, changeLabel, icon: Icon, color = 'blue', iconBg }) => {
    const colorStyles = {
        pink: {
            bg: 'bg-pink-50',
            border: 'border-pink-100',
            iconBg: 'bg-pink-100',
            icon: 'text-pink-500',
            text: 'text-pink-600'
        },
        orange: {
            bg: 'bg-orange-50',
            border: 'border-orange-100',
            iconBg: 'bg-orange-100',
            icon: 'text-orange-500',
            text: 'text-orange-600'
        },
        green: {
            bg: 'bg-emerald-50',
            border: 'border-emerald-100',
            iconBg: 'bg-emerald-100',
            icon: 'text-emerald-500',
            text: 'text-emerald-600'
        },
        purple: {
            bg: 'bg-purple-50',
            border: 'border-purple-100',
            iconBg: 'bg-purple-100',
            icon: 'text-purple-500',
            text: 'text-purple-600'
        },
        blue: {
            bg: 'bg-blue-50',
            border: 'border-blue-100',
            iconBg: 'bg-blue-100',
            icon: 'text-blue-500',
            text: 'text-blue-600'
        }
    };

    const style = colorStyles[color] || colorStyles.blue;
    const isPositive = change >= 0;

    return (
        <div className={cn("p-5 rounded-2xl border-2 transition-all duration-200 hover:shadow-lg hover:-translate-y-0.5", style.bg, style.border)}>
            <div className="flex items-start justify-between mb-4">
                <div className={cn("w-12 h-12 rounded-xl flex items-center justify-center", iconBg || style.iconBg)}>
                    {Icon && <Icon className={cn("w-6 h-6", style.icon)} />}
                </div>
            </div>

            <div>
                <h3 className="text-3xl font-bold text-slate-900 mb-1">{value}</h3>
                <p className="text-sm font-medium text-slate-600 mb-2">{title}</p>

                {change !== undefined && (
                    <div className="flex items-center space-x-1">
                        {isPositive ? (
                            <TrendingUp className="w-3.5 h-3.5 text-emerald-500" />
                        ) : (
                            <TrendingDown className="w-3.5 h-3.5 text-red-500" />
                        )}
                        <span className={cn("text-xs font-semibold", isPositive ? "text-emerald-600" : "text-red-600")}>
                            {Math.abs(change)}%
                        </span>
                        <span className="text-xs text-slate-400">{changeLabel}</span>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ColorfulMetricCard;
