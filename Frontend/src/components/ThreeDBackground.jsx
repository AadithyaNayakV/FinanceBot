import { useEffect, useRef } from 'react';
import { useTheme } from '../context/ThemeContext';

export default function ThreeDBackground() {
  const canvasRef = useRef(null);
  const { isDark } = useTheme();

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;
    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);

    let mouse = {
      x: width / 2,
      y: height / 2,
      targetX: width / 2,
      targetY: height / 2,
    };

    const handleResize = () => {
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    };

    const handleMouseMove = (e) => {
      mouse.targetX = e.clientX;
      mouse.targetY = e.clientY;
    };

    window.addEventListener('resize', handleResize);
    window.addEventListener('mousemove', handleMouseMove);

    // Create 3D particle nodes
    const numParticles = Math.min(Math.floor((width * height) / 18000), 55);
    const particles = [];

    for (let i = 0; i < numParticles; i++) {
      particles.push({
        x: (Math.random() - 0.5) * width * 1.5,
        y: (Math.random() - 0.5) * height * 1.5,
        z: Math.random() * 800 + 200, // 3D depth
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        vz: (Math.random() - 0.5) * 0.5,
        size: Math.random() * 3 + 1.5,
        baseColor: i % 3 === 0 ? 'emerald' : i % 3 === 1 ? 'cyan' : 'indigo',
        pulse: Math.random() * Math.PI * 2,
      });
    }

    // Floating 3D Financial Isometric Cubes
    const numCubes = 6;
    const cubes = [];
    for (let i = 0; i < numCubes; i++) {
      cubes.push({
        x: (Math.random() - 0.5) * width,
        y: (Math.random() - 0.5) * height,
        z: Math.random() * 600 + 300,
        size: Math.random() * 30 + 20,
        rotX: Math.random() * Math.PI,
        rotY: Math.random() * Math.PI,
        rotZ: Math.random() * Math.PI,
        rotSpeedX: (Math.random() - 0.5) * 0.01,
        rotSpeedY: (Math.random() - 0.5) * 0.01,
        rotSpeedZ: (Math.random() - 0.5) * 0.01,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
      });
    }

    const render = () => {
      // Ease mouse
      mouse.x += (mouse.targetX - mouse.x) * 0.05;
      mouse.y += (mouse.targetY - mouse.y) * 0.05;

      const mouseNormX = (mouse.x / width - 0.5) * 2;
      const mouseNormY = (mouse.y / height - 0.5) * 2;

      ctx.clearRect(0, 0, width, height);

      const fov = 450;
      const centerX = width / 2;
      const centerY = height / 2;

      // Draw connected constellation mesh
      for (let i = 0; i < particles.length; i++) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.z += p.vz;
        p.pulse += 0.03;

        // Boundaries
        if (p.x < -width) p.x = width;
        if (p.x > width) p.x = -width;
        if (p.y < -height) p.y = height;
        if (p.y > height) p.y = -height;
        if (p.z < 100) p.z = 900;
        if (p.z > 900) p.z = 100;

        // 3D Perspective Projection + Mouse Parallax
        const parX = p.x - mouseNormX * 120 * (1 - p.z / 1000);
        const parY = p.y - mouseNormY * 120 * (1 - p.z / 1000);

        const scale = fov / (fov + p.z);
        const projX = centerX + parX * scale;
        const projY = centerY + parY * scale;
        const projRadius = Math.max(0.5, p.size * scale * (1 + Math.sin(p.pulse) * 0.2));

        p.projX = projX;
        p.projY = projY;
        p.projScale = scale;

        // Draw particle
        let colorStr = '';
        if (isDark) {
          if (p.baseColor === 'emerald') colorStr = `rgba(16, 185, 129, ${scale * 0.75})`;
          else if (p.baseColor === 'cyan') colorStr = `rgba(6, 182, 212, ${scale * 0.7})`;
          else colorStr = `rgba(99, 102, 241, ${scale * 0.65})`;
        } else {
          if (p.baseColor === 'emerald') colorStr = `rgba(5, 150, 105, ${scale * 0.45})`;
          else if (p.baseColor === 'cyan') colorStr = `rgba(8, 145, 178, ${scale * 0.4})`;
          else colorStr = `rgba(79, 70, 229, ${scale * 0.4})`;
        }

        ctx.beginPath();
        ctx.arc(projX, projY, projRadius, 0, Math.PI * 2);
        ctx.fillStyle = colorStr;
        ctx.fill();

        // Connect nearby particles
        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dx = p.projX - p2.projX;
          const dy = p.projY - p2.projY;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist < 110 * scale) {
            const alpha = (1 - dist / (110 * scale)) * scale * (isDark ? 0.25 : 0.12);
            ctx.beginPath();
            ctx.moveTo(p.projX, p.projY);
            ctx.lineTo(p2.projX, p2.projY);
            ctx.strokeStyle = isDark ? `rgba(16, 185, 129, ${alpha})` : `rgba(5, 150, 105, ${alpha})`;
            ctx.lineWidth = 0.8 * scale;
            ctx.stroke();
          }
        }
      }

      // Draw Floating 3D Geometric Wireframe Cubes
      cubes.forEach((cube) => {
        cube.x += cube.vx;
        cube.y += cube.vy;
        cube.rotX += cube.rotSpeedX;
        cube.rotY += cube.rotSpeedY;
        cube.rotZ += cube.rotSpeedZ;

        if (cube.x < -width / 2) cube.x = width / 2;
        if (cube.x > width / 2) cube.x = -width / 2;
        if (cube.y < -height / 2) cube.y = height / 2;
        if (cube.y > height / 2) cube.y = -height / 2;

        const parX = cube.x - mouseNormX * 80 * (1 - cube.z / 1000);
        const parY = cube.y - mouseNormY * 80 * (1 - cube.z / 1000);
        const scale = fov / (fov + cube.z);

        const s = (cube.size * scale) / 2;
        const cx = centerX + parX * scale;
        const cy = centerY + parY * scale;

        // 8 vertices of cube in local space rotated
        const cosX = Math.cos(cube.rotX), sinX = Math.sin(cube.rotX);
        const cosY = Math.cos(cube.rotY), sinY = Math.sin(cube.rotY);

        const project = (vx, vy, vz) => {
          // Y rot
          let x1 = vx * cosY - vz * sinY;
          let z1 = vx * sinY + vz * cosY;
          // X rot
          let y2 = vy * cosX - z1 * sinX;
          return [cx + x1, cy + y2];
        };

        const v = [
          project(-s, -s, -s), project(s, -s, -s),
          project(s, s, -s), project(-s, s, -s),
          project(-s, -s, s), project(s, -s, s),
          project(s, s, s), project(-s, s, s)
        ];

        const edges = [
          [0,1],[1,2],[2,3],[3,0],
          [4,5],[5,6],[6,7],[7,4],
          [0,4],[1,5],[2,6],[3,7]
        ];

        const alpha = isDark ? 0.18 * scale : 0.08 * scale;
        ctx.strokeStyle = isDark ? `rgba(6, 182, 212, ${alpha})` : `rgba(79, 70, 229, ${alpha})`;
        ctx.lineWidth = 1 * scale;

        edges.forEach(([start, end]) => {
          ctx.beginPath();
          ctx.moveTo(v[start][0], v[start][1]);
          ctx.lineTo(v[end][0], v[end][1]);
          ctx.stroke();
        });
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [isDark]);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {/* Dynamic 3D Radial Glow Orbs */}
      <div 
        className={`absolute -top-32 -left-32 w-96 h-96 rounded-full blur-[100px] transition-colors duration-700 pointer-events-none ${
          isDark ? 'bg-emerald-600/15' : 'bg-emerald-400/20'
        }`} 
      />
      <div 
        className={`absolute top-1/3 -right-32 w-96 h-96 rounded-full blur-[110px] transition-colors duration-700 pointer-events-none ${
          isDark ? 'bg-cyan-600/10' : 'bg-sky-300/25'
        }`} 
      />
      <div 
        className={`absolute -bottom-32 left-1/4 w-[500px] h-96 rounded-full blur-[120px] transition-colors duration-700 pointer-events-none ${
          isDark ? 'bg-indigo-600/15' : 'bg-indigo-300/20'
        }`} 
      />

      {/* 3D Canvas Mesh */}
      <canvas ref={canvasRef} className="w-full h-full block opacity-90" />
    </div>
  );
}
