document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // 1. Interactive Canvas Background (Network Constellation)
    // -------------------------------------------------------------------------
    const canvas = document.getElementById('bg-canvas');
    const ctx = canvas.getContext('2d');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    window.addEventListener('resize', () => {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
    });

    const particles = [];
    const maxParticles = 60;
    const maxDistance = 120;

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.5;
            this.vy = (Math.random() - 0.5) * 0.5;
            this.radius = Math.random() * 1.5 + 1;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(139, 92, 246, 0.4)'; // violet-500 with opacity
            ctx.fill();
        }
    }

    // Initialize particles
    for (let i = 0; i < maxParticles; i++) {
        particles.push(new Particle());
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        // Draw connections
        for (let i = 0; i < particles.length; i++) {
            const p1 = particles[i];
            p1.update();
            p1.draw();

            for (let j = i + 1; j < particles.length; j++) {
                const p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < maxDistance) {
                    ctx.beginPath();
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    // Fade lines out as they get further apart
                    const alpha = (1 - dist / maxDistance) * 0.15;
                    ctx.strokeStyle = `rgba(99, 102, 241, ${alpha})`; // indigo-500
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
        requestAnimationFrame(animate);
    }
    animate();

    // -------------------------------------------------------------------------
    // 2. Mobile Menu Toggle
    // -------------------------------------------------------------------------
    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('hidden');
            const spans = menuBtn.querySelectorAll('span');
            // Toggle hamburger icon animation
            spans[0].classList.toggle('rotate-45');
            spans[0].classList.toggle('translate-y-1.5');
            spans[1].classList.toggle('opacity-0');
            spans[2].classList.toggle('-rotate-45');
            spans[2].classList.toggle('-translate-y-1.5');
        });

        // Close mobile menu when a link is clicked
        const mobileLinks = mobileMenu.querySelectorAll('a');
        mobileLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.add('hidden');
                const spans = menuBtn.querySelectorAll('span');
                spans[0].classList.remove('rotate-45', 'translate-y-1.5');
                spans[1].classList.remove('opacity-0');
                spans[2].classList.remove('-rotate-45', '-translate-y-1.5');
            });
        });
    }

    // -------------------------------------------------------------------------
    // 3. Dynamic Projects Fetch & Render
    // -------------------------------------------------------------------------
    const projectsGrid = document.getElementById('projects-grid');

    const svgIcons = {
        'shopping-cart': `<svg class="w-6 h-6 text-brand-indigo" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>`,
        'cpu': `<svg class="w-6 h-6 text-brand-emerald" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>`,
        'database': `<svg class="w-6 h-6 text-brand-violet" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.58 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.58 4 8 4s8-1.79 8-4M4 7c0-2.21 3.58-4 8-4s8 1.79 8 4m0 5c0 2.21-3.58 4-8 4s-8-1.79-8-4" />
        </svg>`,
        'default': `<svg class="w-6 h-6 text-brand-violet" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>`
    };

    const fallbackProjects = [
        {
            title: "E-Commerce Order Processing Engine",
            description: "A high-performance order processing engine that handles asynchronous orders, logs requests to an SQLite database, and broadcasts live update notifications. Designed for maximum throughput and reliability.",
            tech_stack: "Python, FastAPI, SQLite, Asynchronous Tasks, Uvicorn",
            github_url: "https://github.com/hhafizriazahmad-arch/fluxflow-ecommerce-engine",
            live_url: null,
            icon_type: "shopping-cart"
        },
        {
            title: "Onboarding Automation System",
            description: "An enterprise-grade automation workflow triggered by Typeform submissions. It automatically feeds user profiles to Google Sheets, creates dedicated workspaces, and triggers real-time onboarding notifications via Slack webhook integrations.",
            tech_stack: "Python, APScheduler, Webhooks, Google Sheets API, Slack Webhooks",
            github_url: "https://github.com/hhafizriazahmad-arch/onboarding-automation-system",
            live_url: null,
            icon_type: "cpu"
        },
        {
            title: "Autonomous AI Prospecting Agent",
            description: "An AI-driven autonomous lead generation and intelligence pipeline that automatically discovers, scrapes, and qualifies potential client leads. It aggregates business metrics, performs context analysis, and structures leads directly into a database and Slack for automated outreach.",
            tech_stack: "Python, AI / LLM Integration, Web Scraping, Data Pipeline, Slack Webhooks",
            github_url: "https://github.com/hhafizriazahmad-arch/autonomous-prospecting-agent",
            live_url: "https://autonomous-prospecting-agent.vercel.app",
            icon_type: "cpu"
        }
    ];

    function renderProjectsList(projects) {
        if (!projects || projects.length === 0) {
            projectsGrid.innerHTML = `
                <div class="col-span-full text-center py-8 text-slate-500">
                    No projects loaded yet. Please check back later.
                </div>`;
            return;
        }

        projectsGrid.innerHTML = ''; // Clear loading spinner
        projects.forEach(project => {
            const iconSvg = svgIcons[project.icon_type] || svgIcons['default'];
            const techStackBadges = project.tech_stack.split(',').map(tech => 
                `<span class="text-xs px-2.5 py-1 rounded bg-white/5 border border-white/10 text-slate-300 font-mono">${tech.trim()}</span>`
            ).join('');

            const githubLink = project.github_url ? `
                <a href="${project.github_url}" target="_blank" rel="noopener noreferrer" class="text-slate-400 hover:text-white transition flex items-center space-x-1 text-sm font-medium">
                    <span>GitHub</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>` : '';

            const liveLink = project.live_url ? `
                <a href="${project.live_url}" target="_blank" rel="noopener noreferrer" class="text-brand-indigo hover:underline transition flex items-center space-x-1 text-sm font-medium">
                    <span>Live Demo</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>` : '';

            const projectCard = document.createElement('div');
            projectCard.className = 'p-8 rounded-3xl glass-panel flex flex-col space-y-6 transition-all duration-300 group';
            projectCard.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="w-12 h-12 rounded-xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:bg-white/10 transition-all duration-300">
                        ${iconSvg}
                    </div>
                    <div class="flex space-x-4">
                        ${githubLink}
                        ${liveLink}
                    </div>
                </div>
                <div class="space-y-3 flex-grow">
                    <h3 class="font-display text-2xl font-bold text-slate-100 group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-white group-hover:to-brand-violet transition-all duration-300">
                        ${project.title}
                    </h3>
                    <p class="text-slate-400 text-sm leading-relaxed">
                        ${project.description}
                    </p>
                </div>
                <div class="flex flex-wrap gap-2 pt-2 border-t border-white/5">
                    ${techStackBadges}
                </div>
            `;
            projectsGrid.appendChild(projectCard);
        });
    }

    function loadProjects() {
        fetch('/api/projects')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(projects => {
                renderProjectsList(projects);
            })
            .catch(error => {
                console.warn('Backend API fetch failed, rendering static fallback projects:', error);
                renderProjectsList(fallbackProjects);
            });
    }

    loadProjects();

    // -------------------------------------------------------------------------
    // 4. Contact Form AJAX Submission
    // -------------------------------------------------------------------------
    const contactForm = document.getElementById('contact-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const notification = document.getElementById('form-notification');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();

            // Form payload
            const payload = {
                name: document.getElementById('name').value.trim(),
                email: document.getElementById('email').value.trim(),
                subject: document.getElementById('subject').value.trim(),
                message: document.getElementById('message').value.trim()
            };

            // Loading state UI
            submitBtn.disabled = true;
            btnText.textContent = 'Sending Message...';
            btnSpinner.classList.remove('hidden');
            notification.className = 'hidden'; // Hide prior notification

            fetch('/api/contact', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(async (response) => {
                if (!response.ok) {
                    let errorText = 'Failed to submit message.';
                    try {
                        const rawText = await response.text();
                        try {
                            const jsonErr = JSON.parse(rawText);
                            if (typeof jsonErr.detail === 'string') {
                                errorText = jsonErr.detail;
                            } else if (jsonErr.detail && typeof jsonErr.detail === 'object') {
                                errorText = JSON.stringify(jsonErr.detail);
                            } else {
                                errorText = rawText || errorText;
                            }
                        } catch (pErr) {
                            errorText = rawText || errorText;
                        }
                    } catch (tErr) {}
                    throw new Error(errorText);
                }
                return response;
            })
            .then(() => {
                // Success
                notification.className = 'block mb-6 p-4 rounded-xl border border-brand-emerald/20 bg-brand-emerald/10 text-brand-emerald font-medium';
                notification.textContent = 'Thank you! Your message has been sent successfully.';
                contactForm.reset();
            })
            .catch((err) => {
                // Error
                console.error('Contact Form error:', err);
                const displayMsg = (err && typeof err.message === 'string' && err.message !== '[object Object]')
                    ? err.message
                    : 'Something went wrong. Please check your connection and try again.';
                notification.className = 'block mb-6 p-4 rounded-xl border border-red-500/20 bg-red-500/10 text-red-400 font-medium';
                notification.textContent = displayMsg;
            })
            .finally(() => {
                // Reset submit button state
                submitBtn.disabled = false;
                btnText.textContent = 'Send Message';
                btnSpinner.classList.add('hidden');
            });
        });
    }
});
