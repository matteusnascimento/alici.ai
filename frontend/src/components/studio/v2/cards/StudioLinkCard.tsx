/**
 * Reusable card component for navigation links (MANAGE & LIBRARY sections)
 * More compact than creation tools, focused on clear hierarchy
 */
import React from 'react';
import { LucideIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cn } from '../../../../utils/cn';

interface StudioLinkCardProps {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  color: string;
  variant?: 'manage' | 'library';
}

export const StudioLinkCard: React.FC<StudioLinkCardProps> = ({
  id,
  title,
  description,
  icon: Icon,
  path,
  color,
  variant = 'manage',
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(path);
  };

  return (
    <button
      onClick={handleClick}
      className={cn(
        'group w-full text-left rounded-xl border border-white/10 backdrop-blur-md',
        'p-4 transition-all duration-200',
        'hover:border-white/20 hover:bg-white/5 hover:shadow-lg hover:shadow-white/5',
        'focus:outline-none focus:ring-2 focus:ring-white/20',
        'active:scale-95'
      )}
    >
      <div className="flex items-start gap-3">
        {/* Icon container */}
        <div
          className={cn(
            'rounded-lg p-2 flex-shrink-0 transition-all duration-200',
            `bg-gradient-to-br ${color}`,
            'group-hover:scale-110 shadow-lg'
          )}
        >
          <Icon className="w-5 h-5 text-white" />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-white text-sm leading-tight">
            {title}
          </h3>
          <p className="text-xs text-white/55 leading-relaxed mt-0.5 truncate group-hover:text-white/70 transition-colors">
            {description}
          </p>
        </div>

        {/* Arrow indicator */}
        <div className="flex-shrink-0 text-white/30 transition-all duration-200 group-hover:text-white/60 group-hover:translate-x-1 font-semibold">
          →
        </div>
      </div>
    </button>
  );
};
