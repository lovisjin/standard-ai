import { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  size?: 'sm' | 'md' | 'lg';
}

export function Button({ children, size = 'md', className, ...props }: ButtonProps) {
  const sizeClasses = {
    sm: 'px-2 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };

  return (
    <button 
      className={`bg-black text-white rounded ${sizeClasses[size]} ${className || ''}`} 
      {...props}
    >
      {children}
    </button>
  );
}
