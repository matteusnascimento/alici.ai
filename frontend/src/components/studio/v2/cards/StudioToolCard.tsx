/**
 * Reusable card component for creation tools (CREATE section)
 * Used in Homepage, can be extended to other views
 */
import React from 'react';
import { LucideIcon } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cn } from '../../../../utils/cn';

interface StudioToolCardProps {
  id: string;
  title: string;
  description: string;
  icon: LucideIcon;
  path: string;
  color: string;
  gradient: string;
  badge?: string;
  comingSoon?: boolean;
  size?: 'sm' | 'md' | 'lg';
}

export const StudioToolCard: React.FC<StudioToolCardProps> = ({
  id,
  title,
  description,
  icon: Icon,
  path,
  color,
  gradient,
  badge,
  comingSoon = false,
  size = 'lg',
}) => {
  const navigate = useNavigate();

  const handleClick = () => {
    if (!comingSoon) {
      navigate(path);
    }
  };

  const sizeClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  const iconSizeClasses = {
    sm: 'w-8 h-8',
    md: 'w-10 h-10',
    lg: 'w-12 h-12',
  };

  return (
    <div
      onClick={handleClick}
      className={cn(
        'relative overflow-hidden rounded-xl border border-white/10 backdrop-blur-md',
        'transition-all duration-300',
        'cursor-pointer group',
        sizeClasses[size],
        gradient,
        !comingSoon && 'hover:border-white/20 hover:shadow-lg hover:-translate-y-1'
      )}
    >
      {/* Animated background gradient */}
      <div
        className={cn(
          'absolute inset-0 opacity-0 group-hover:opacity-20 transition-opacity duration-300',
          'bg-gradient-to-br from-white to-transparent'
        )}
        style={{ pointerEvents: 'none' }}
      />

      {/* Content */}
      <div className="relative z-10 flex flex-col gap-3 h-full">
        {/* Header with icon and badge */}
        <div className="flex items-start justify-between gap-3">
          <div
            className={cn(
              'rounded-lg p-2.5 transition-all duration-300',
              `bg-gradient-to-br ${color} shadow-lg`,
              'group-hover:scale-110 group-hover:shadow-lg'
            )}
          >
            <Icon className={cn(iconSizeClasses[size], 'text-white')} />
          </div>

          {badge && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-white/10 text-white/70 backdrop-blur-md">
              {badge}
            </span>
          )}

          {comingSoon && (
            <span className="px-2 py-1 rounded-full text-xs font-medium bg-amber-500/20 text-amber-200 backdrop-blur-md border border-amber-500/30">
              Em breve
            </span>
          )}
        </div>

        {/* Title and description */}
        <div className="flex-1">
          <h3 className="font-bold text-white text-base md:text-lg leading-tight">
            {title}
          </h3>
          <p className="text-xs md:text-sm text-white/65 leading-relaxed mt-1">
            {description}
          </p>
        </div>

        {/* CTA button indicator */}
        {!comingSoon && (
          <div className="flex items-center gap-2 text-white/50 group-hover:text-white/80 transition-colors text-xs font-semibold mt-auto">
            <span>Abrir →</span>
          </div>
        )}
      </div>

    </div>
  );
};
