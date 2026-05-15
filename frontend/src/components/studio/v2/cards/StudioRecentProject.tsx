/**
 * Component for recent projects in CONTINUE section
 * Shows minimal info: title, last edited, quick open button
 */
import React from 'react';
import { FileText, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { cn } from '../../../../utils/cn';
import { resolveStudioProjectRoute } from '../config/studioHomeConfig';

interface StudioRecentProjectProps {
  id: string;
  projectKey: string;
  title: string;
  type: string; // 'video', 'photo', 'poster', 'story', etc.
  lastEdited: Date | string;
  thumbnail?: string;
}

export const StudioRecentProject: React.FC<StudioRecentProjectProps> = ({
  id,
  projectKey,
  title,
  type,
  lastEdited,
  thumbnail,
}) => {
  const navigate = useNavigate();

  // Convert to relative time (e.g., "2 hours ago")
  const getRelativeTime = (date: Date | string) => {
    const d = typeof date === 'string' ? new Date(date) : date;
    const now = new Date();
    const seconds = Math.floor((now.getTime() - d.getTime()) / 1000);

    let interval = seconds / 31536000;
    if (interval > 1) return Math.floor(interval) + ' anos atrás';

    interval = seconds / 2592000;
    if (interval > 1) return Math.floor(interval) + ' meses atrás';

    interval = seconds / 86400;
    if (interval > 1) return Math.floor(interval) + ' dias atrás';

    interval = seconds / 3600;
    if (interval > 1) return Math.floor(interval) + ' horas atrás';

    interval = seconds / 60;
    if (interval > 1) return Math.floor(interval) + ' minutos atrás';

    return 'agora mesmo';
  };

  const handleOpen = (e: React.MouseEvent) => {
    e.stopPropagation();
    navigate(resolveStudioProjectRoute(type, projectKey));
  };

  return (
    <div
      className={cn(
        'group relative overflow-hidden rounded-lg border border-white/10 backdrop-blur-md',
        'bg-white/5 transition-all duration-200',
        'hover:border-white/20 hover:bg-white/10'
      )}
    >
      {/* Thumbnail or fallback visual */}
      <div className="relative w-full aspect-video bg-gradient-to-br from-slate-700 to-slate-900 overflow-hidden">
        {thumbnail ? (
          <img src={thumbnail} alt={title} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <FileText className="w-8 h-8 text-white/20" />
          </div>
        )}

        {/* Overlay on hover */}
        <div
          className={cn(
            'absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100',
            'transition-all duration-200 flex items-center justify-center'
          )}
        >
          <button
            onClick={handleOpen}
            className={cn(
              'rounded-full p-3 bg-white/20 backdrop-blur-md border border-white/30',
              'hover:bg-white/30 transition-all duration-200',
              'flex items-center gap-2 text-white'
            )}
          >
            <Play className="w-5 h-5 fill-current" />
          </button>
        </div>

        {/* Type badge */}
        <div className="absolute top-2 right-2 px-2 py-1 rounded text-xs font-medium bg-black/50 text-white/70 backdrop-blur-md border border-white/10">
          {type}
        </div>
      </div>

      {/* Content */}
      <div className="p-3">
        <h4 className="font-medium text-white/90 text-sm line-clamp-2 leading-tight mb-1">
          {title}
        </h4>
        <p className="text-xs text-white/50">
          Editado {getRelativeTime(lastEdited)}
        </p>
      </div>

      {/* Quick action button */}
      <button
        onClick={handleOpen}
        className={cn(
          'absolute bottom-3 right-3 px-3 py-1.5 rounded text-xs font-medium',
          'bg-white/10 hover:bg-white/20 text-white/70 hover:text-white',
          'border border-white/10 hover:border-white/20',
          'transition-all duration-200 opacity-0 group-hover:opacity-100',
          'translate-y-1 group-hover:translate-y-0'
        )}
      >
        Abrir
      </button>
    </div>
  );
};
