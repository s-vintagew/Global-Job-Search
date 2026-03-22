// ─── DOM Elements ───────────────────────────────────────────
const globeVizContainer = document.getElementById('globeViz');
const toggleRotationBtn = document.getElementById('toggleRotationBtn');
const rotationIcon = document.getElementById('rotationIcon');
const applyFiltersBtn = document.getElementById('applyFiltersBtn');

// Stats Elements
const jobCountEl = document.getElementById('jobCount');
const countryCountEl = document.getElementById('countryCount');
const sourceCountEl = document.getElementById('sourceCount');

// Filter Elements
const countryFilter = document.getElementById('countryFilter');
const typeFilter = document.getElementById('typeFilter');
const experienceFilter = document.getElementById('experienceFilter');
const roleFilter = document.getElementById('roleFilter');
const daysFilter = document.getElementById('daysFilter');

// Detail Panel Elements
const detailPanel = document.getElementById('jobDetailsPanel');
const closeDetailsBtn = document.getElementById('closeDetailsBtn');
const dSource = document.getElementById('detailSource');
const dTitle = document.getElementById('detailTitle');
const dCompany = document.getElementById('detailCompany');
const dLocationText = document.getElementById('detailLocationText');
const dType = document.getElementById('detailType');
const dSalary = document.getElementById('detailSalary');
const dExperience = document.getElementById('detailExperience');
const dDescription = document.getElementById('detailDescription');
const dLink = document.getElementById('detailLink');
const dTags = document.getElementById('detailTags');

let isAutoRotating = true;

// ─── Initialize Globe ───────────────────────────────────────
const world = Globe()
    (globeVizContainer)
    .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
    .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
    .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
    .pointOfView({ lat: 25, lng: 0, altitude: 2 })
    .htmlElementsData([])
    .htmlLat(d => d.lat)
    .htmlLng(d => d.lng)
    .htmlElement(d => {
        const el = document.createElement('div');
        el.className = 'globe-marker';
        
        // Custom tooltip logic to cleanly handle hover
        el.onmouseenter = () => {
            const tooltip = document.createElement('div');
            tooltip.className = 'scene-tooltip';
            tooltip.id = 'activeTooltip';
            tooltip.innerHTML = `
                <b>${d.title}</b>
                <div class="tooltip-company">${d.company || 'Unknown Company'} &bull; ${d.city || 'Remote'}</div>
            `;
            
            // Position near cursor
            Object.assign(tooltip.style, {
                position: 'fixed',
                pointerEvents: 'none',
                zIndex: 100,
                transform: 'translate(-50%, -100%)',
                marginTop: '-10px'
            });
            
            document.body.appendChild(tooltip);
            
            el.onmousemove = (e) => {
                const active = document.getElementById('activeTooltip');
                if (active) {
                    active.style.left = e.clientX + 'px';
                    active.style.top = e.clientY + 'px';
                }
            };
        };
        
        el.onmouseleave = () => {
            const active = document.getElementById('activeTooltip');
            if (active) active.remove();
        };
        
        // Click handler
        el.onclick = () => handleJobClick(d);
        
        return el;
    });

// Map Controls Setup
const controls = world.controls();
controls.autoRotate = true;
controls.autoRotateSpeed = 0.5;
controls.enableDamping = true;
controls.dampingFactor = 0.05;

// Pause on drag
controls.addEventListener('start', () => {
    if (isAutoRotating) setRotation(false);
});

// ─── Rotation Toggle ────────────────────────────────────────
function setRotation(enabled) {
    isAutoRotating = enabled;
    world.controls().autoRotate = isAutoRotating;
    
    if (isAutoRotating) {
        rotationIcon.textContent = 'pause';
        toggleRotationBtn.classList.add('playing');
    } else {
        rotationIcon.textContent = 'play_arrow';
        toggleRotationBtn.classList.remove('playing');
    }
}

toggleRotationBtn.addEventListener('click', () => {
    setRotation(!isAutoRotating);
});

// ─── Ambient Particles Effect ───────────────────────────────
function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    const ctx = canvas.getContext('2d');
    
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    
    const particles = Array.from({ length: 50 }, () => ({
        x: Math.random() * width,
        y: Math.random() * height,
        r: Math.random() * 1.5,
        dx: (Math.random() - 0.5) * 0.2,
        dy: (Math.random() - 0.5) * 0.2,
        baseAlpha: Math.random() * 0.5 + 0.1
    }));
    
    function animate() {
        ctx.clearRect(0, 0, width, height);
        
        particles.forEach(p => {
            p.x += p.dx;
            p.y += p.dy;
            
            if (p.x < 0 || p.x > width) p.dx *= -1;
            if (p.y < 0 || p.y > height) p.dy *= -1;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(0, 212, 255, ${p.baseAlpha})`;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });
    
    animate();
}

// ─── Job Details Panel ──────────────────────────────────────
function handleJobClick(job) {
    // Zoom and stop rotation
    world.pointOfView({ lat: job.lat, lng: job.lng, altitude: 0.8 }, 1200);
    setRotation(false);
    
    // Cleanup any lingering tooltip
    const activeTooltips = document.querySelectorAll('.scene-tooltip');
    activeTooltips.forEach(t => t.remove());

    // Populate data
    dSource.textContent = job.source || 'globaljobs';
    dTitle.textContent = job.title;
    dCompany.textContent = job.company;
    dLocationText.textContent = `${job.city}, ${job.country}`;
    
    // Type Tag
    if (job.type) {
        dType.textContent = job.type.charAt(0).toUpperCase() + job.type.slice(1);
        dType.style.display = 'inline-block';
    } else {
        dType.style.display = 'none';
    }
    
    // Experience Tag
    if (job.experience_level) {
        dExperience.textContent = job.experience_level.charAt(0).toUpperCase() + job.experience_level.slice(1);
        dExperience.style.display = 'inline-block';
    } else {
        dExperience.style.display = 'none';
    }
    
    // Salary
    dSalary.textContent = job.salary && job.salary !== 'Competitive' ? job.salary : 'Competitive Comp';
    
    // Desc
    dDescription.textContent = job.description || 'No description provided.';
    dLink.href = job.url;
    
    // Tech Stack Tags
    dTags.innerHTML = '';
    if (job.tags) {
        const skills = job.tags.split(',').filter(t => t.trim() !== '');
        skills.slice(0, 5).forEach(skill => {
            const span = document.createElement('span');
            span.className = 'skill-tag';
            span.textContent = skill.trim();
            dTags.appendChild(span);
        });
    }

    // Show Panel
    detailPanel.classList.remove('hidden');
}

closeDetailsBtn.addEventListener('click', () => {
    detailPanel.classList.add('hidden');
    world.pointOfView({ altitude: 2 }, 1000);
    // Auto resume after closing panel
    setTimeout(() => { if (detailPanel.classList.contains('hidden')) setRotation(true) }, 1000);
});

// ─── API Calls ──────────────────────────────────────────────

// Dynamic base URL handling (supports Nginx reverse proxy or direct API for dev)
const API_BASE = 'http://localhost:8000/api';

// Number rolling animation
function animateCounter(el, target) {
    let current = 0;
    const increment = Math.max(1, Math.floor(target / 40));
    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }
        el.textContent = current;
    }, 20);
}

async function fetchStatsAndFilters() {
    try {
        // 1. Stats
        const statsRes = await fetch(`${API_BASE}/stats`);
        if (statsRes.ok) {
            const stats = await statsRes.json();
            // Animate counters
            animateCounter(jobCountEl, stats.total_jobs);
            animateCounter(countryCountEl, stats.total_countries);
            animateCounter(sourceCountEl, stats.total_sources);
        }

        // 2. Countries for filter
        const countriesRes = await fetch(`${API_BASE}/countries`);
        if (countriesRes.ok) {
            const countries = await countriesRes.json();
            
            // Keep "Everywhere" and append others
            while (countryFilter.options.length > 1) {
                countryFilter.remove(1);
            }
            
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countryFilter.appendChild(option);
            });
        }
    } catch (e) {
        console.error("Stats/Filters fetch failed:", e);
    }
}

async function fetchJobs() {
    try {
        applyFiltersBtn.innerHTML = '<span class="material-icons-round">sync</span> Loading...';
        applyFiltersBtn.style.opacity = '0.7';

        const params = new URLSearchParams({ limit: 300 }); // Limit to keep rendering smooth
        
        if (countryFilter.value !== 'all') params.append('country', countryFilter.value);
        if (typeFilter.value !== 'all') params.append('type', typeFilter.value);
        if (experienceFilter.value !== 'all') params.append('experience', experienceFilter.value);
        if (roleFilter.value.trim()) params.append('q', roleFilter.value.trim());
        if (daysFilter.value) params.append('days', daysFilter.value);

        const res = await fetch(`${API_BASE}/jobs?${params.toString()}`);
        
        if (res.ok) {
            const jobs = await res.json();
            world.htmlElementsData(jobs);
        } else {
            console.error("Failed to fetch jobs");
        }
    } catch (e) {
        console.error("Jobs fetch error:", e);
    } finally {
        setTimeout(() => {
            applyFiltersBtn.innerHTML = '<span class="material-icons-round">filter_list</span> Apply Filters';
            applyFiltersBtn.style.opacity = '1';
        }, 300); // slight delay for UI feel
    }
}

// ─── Setup Listeners ────────────────────────────────────────
applyFiltersBtn.addEventListener('click', () => {
    // Close detail panel if open
    if (!detailPanel.classList.contains('hidden')) {
        detailPanel.classList.add('hidden');
    }
    fetchJobs();
    
    // Reset view
    world.pointOfView({ altitude: 2 }, 1000);
});

// Submit search on Enter key
roleFilter.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        applyFiltersBtn.click();
    }
});

// Handle resize
window.addEventListener('resize', () => {
    world.width(window.innerWidth);
    world.height(window.innerHeight);
    initParticles(); // Re-init to update canvas bounds correctly
});

// ─── Boot ───────────────────────────────────────────────────
initParticles();
fetchStatsAndFilters();
fetchJobs();
