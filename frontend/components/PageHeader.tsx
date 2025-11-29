// components/PageHeader.tsx
interface PageHeaderProps {
  title: string;
  gradientText?: string;
  subtitle?: string;
  size?: 'sm' | 'md' | 'lg';
  centered?: boolean;
  className?: string;
}

export function PageHeader({ 
  title, 
  gradientText, 
  subtitle, 
  size = 'lg',
  centered = true,
  className = '' 
}: PageHeaderProps) {
  const sizeClasses = {
    sm: 'text-2xl sm:text-3xl md:text-4xl',
    md: 'text-3xl sm:text-4xl md:text-5xl', 
    lg: 'text-4xl sm:text-5xl md:text-6xl'
  };

  const subtitleSizeClasses = {
    sm: 'text-base',
    md: 'text-lg',
    lg: 'text-xl'
  };

  return (
    <header className={`${centered ? 'text-center' : ''} mb-8 sm:mb-12 ${className}`}>
      <h1 className={`${sizeClasses[size]} font-bold mb-4 sm:mb-6 text-foreground`}>
        {title}
        {gradientText && (
          <span className="text-transparent bg-clip-text bg-linear-to-r from-purple-400 to-pink-600">
            {" "}{gradientText}
          </span>
        )}
      </h1>
      {subtitle && (
        <p className={`${subtitleSizeClasses[size]} text-muted-foreground leading-relaxed max-w-3xl ${centered ? 'mx-auto' : ''}`}>
          {subtitle}
        </p>
      )}
    </header>
  );
}