const LogoReactifPro = ({ size = "md", className = "" }) => {
  const sizes = {
    sm: { icon: 28, text: "text-sm", sub: "text-[6px]", gap: "gap-1.5" },
    md: { icon: 36, text: "text-lg", sub: "text-[7px]", gap: "gap-2" },
    lg: { icon: 56, text: "text-3xl", sub: "text-[10px]", gap: "gap-3" },
    xl: { icon: 80, text: "text-5xl", sub: "text-sm", gap: "gap-4" },
  };

  const s = sizes[size] || sizes.md;

  return (
    <div className={`flex items-center ${s.gap} ${className}`} data-testid="logo-reactif-pro">
      {/* Icon SVG */}
      <svg
        width={s.icon}
        height={s.icon}
        viewBox="0 0 80 80"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="flex-shrink-0"
      >
        {/* Outer ring */}
        <circle cx="40" cy="40" r="38" stroke="#1e3a5f" strokeWidth="2" fill="#eef2f7" />
        {/* Inner circle */}
        <circle cx="40" cy="40" r="28" fill="#1e3a5f" opacity="0.08" />
        {/* Person silhouette */}
        <circle cx="40" cy="30" r="8" fill="#4f6df5" />
        <path d="M26 56 C26 44 34 40 40 40 C46 40 54 44 54 56" fill="#4f6df5" opacity="0.85" />
        {/* Network nodes */}
        <circle cx="18" cy="28" r="4" fill="#6c5ce7" opacity="0.7" />
        <circle cx="62" cy="28" r="4" fill="#6c5ce7" opacity="0.7" />
        <circle cx="18" cy="54" r="3.5" fill="#4f6df5" opacity="0.5" />
        <circle cx="62" cy="54" r="3.5" fill="#4f6df5" opacity="0.5" />
        {/* Connection lines */}
        <line x1="24" y1="30" x2="32" y2="30" stroke="#6c5ce7" strokeWidth="1.5" opacity="0.4" />
        <line x1="48" y1="30" x2="58" y2="30" stroke="#6c5ce7" strokeWidth="1.5" opacity="0.4" />
        <line x1="20" y1="34" x2="28" y2="42" stroke="#4f6df5" strokeWidth="1" opacity="0.3" />
        <line x1="60" y1="34" x2="52" y2="42" stroke="#4f6df5" strokeWidth="1" opacity="0.3" />
      </svg>

      {/* Text */}
      <div className="flex flex-col leading-none">
        <span className={`${s.text} font-bold tracking-tight`} style={{ fontFamily: 'Outfit, sans-serif' }}>
          <span className="text-[#1e3a5f]">RE'</span>
          <span className="text-[#4f6df5]">ACTIF</span>
          <span className="text-[#1e3a5f]"> PRO</span>
        </span>
        <span className={`${s.sub} font-semibold tracking-[0.2em] text-[#6c5ce7] uppercase mt-0.5`}>
          Intelligence Professionnelle
        </span>
      </div>
    </div>
  );
};

export default LogoReactifPro;
