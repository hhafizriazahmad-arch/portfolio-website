document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // 1. Interactive Canvas Background (HR Autonomous Gray & Gold Luxury Network Grid)
    // -------------------------------------------------------------------------
    const canvas = document.getElementById('bg-canvas');
    if (canvas) {
        const ctx = canvas.getContext('2d');

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const particles = [];
        const maxParticles = 65;
        const maxDistance = 130;

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.4;
                this.vy = (Math.random() - 0.5) * 0.4;
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
                ctx.fillStyle = 'rgba(212, 175, 55, 0.5)'; // Primary Gold Accent with opacity
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
                        const alpha = (1 - dist / maxDistance) * 0.20;
                        ctx.strokeStyle = `rgba(212, 175, 55, ${alpha})`; // Primary Gold
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
            requestAnimationFrame(animate);
        }
        animate();
    }

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
        'shopping-cart': `<svg class="w-6 h-6 text-[#D4AF37]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>`,
        'cpu': `<svg class="w-6 h-6 text-[#D4AF37]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>`,
        'database': `<svg class="w-6 h-6 text-[#D4AF37]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.58 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.58 4 8 4s8-1.79 8-4M4 7c0-2.21 3.58-4 8-4s8 1.79 8 4m0 5c0 2.21-3.58 4-8 4s-8-1.79-8-4" />
        </svg>`,
        'default': `<svg class="w-6 h-6 text-[#D4AF37]" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>`
    };

    const fallbackProjects = [
        {
            title: "AI Lead Intelligence System",
            description: "An automated B2B lead generation pipeline engineered to identify, enrich, and qualify profiles of founders and C-level executives. Built on FastAPI and Gemini AI for high-impact prospect research.",
            tech_stack: "Python, FastAPI, Gemini AI, Playwright, HubSpot API, Webhooks",
            github_url: "https://github.com/hhafizriazahmad-arch/ai-lead-intelligence-system",
            live_url: "https://ai-lead-intelligence-system.vercel.app",
            icon_type: "database"
        },
        {
            title: "Digital Marketing Automation Suite",
            description: "Full-stack digital marketing platform featuring an interactive dynamic UI, serverless backend integrations, and automated lead intelligence data pipelines.",
            tech_stack: "Full-Stack Web Dev, JavaScript, Python, REST API, HTML5/CSS3, Vercel",
            github_url: "https://github.com/hhafizriazahmad-arch/digital-marketing",
            live_url: "https://digital-marketing-sand.vercel.app",
            icon_type: "cpu"
        },
        {
            title: "Onboarding Automation Workflow",
            description: "An enterprise-grade automation workflow triggered by Typeform submissions. It automatically feeds user profiles to Google Sheets, creates dedicated workspaces, and triggers real-time notifications via Slack webhooks.",
            tech_stack: "Python, APScheduler, Webhooks, Google Sheets API, Slack Webhooks",
            github_url: "https://github.com/hhafizriazahmad-arch/onboarding-automation-system",
            live_url: null,
            icon_type: "cpu"
        }
    ];

    function renderProjectsList(projects) {
        if (!projectsGrid) return;
        if (!projects || projects.length === 0) {
            projectsGrid.innerHTML = `
                <div class="col-span-full text-center py-8 text-[#B0B0B0]">
                    No HR Autonomous projects loaded yet. Please check back later.
                </div>`;
            return;
        }

        projectsGrid.innerHTML = ''; // Clear loading spinner
        projects.forEach(project => {
            const iconSvg = svgIcons[project.icon_type] || svgIcons['default'];
            const techStackBadges = project.tech_stack.split(',').map(tech => 
                `<span class="text-xs px-2.5 py-1 rounded bg-[#1E1E1E] border border-[rgba(212,175,55,0.25)] text-[#D4AF37] font-mono">${tech.trim()}</span>`
            ).join('');

            const githubLink = project.github_url ? `
                <a href="${project.github_url}" target="_blank" rel="noopener noreferrer" class="text-[#B0B0B0] hover:text-[#F4C542] transition flex items-center space-x-1 text-sm font-medium">
                    <span>GitHub</span>
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>` : '';

            const projectCard = document.createElement('div');
            projectCard.className = 'p-8 rounded-3xl glass-panel flex flex-col space-y-6 transition-all duration-300 group';
            projectCard.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="w-12 h-12 rounded-xl bg-[#D4AF37]/10 border border-[rgba(212,175,55,0.25)] flex items-center justify-center group-hover:bg-[#D4AF37]/20 transition-all duration-300">
                        ${iconSvg}
                    </div>
                    <div class="flex items-center">
                        ${githubLink}
                    </div>
                </div>
                <div class="space-y-3 flex-grow">
                    <h3 class="font-display text-2xl font-bold text-[#F5F5F5] group-hover:text-transparent group-hover:bg-clip-text group-hover:bg-gradient-to-r group-hover:from-[#D4AF37] group-hover:via-[#F4C542] group-hover:to-[#E6C200] transition-all duration-300">
                        ${project.title}
                    </h3>
                    <p class="text-[#B0B0B0] text-sm leading-relaxed">
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
                console.warn('Backend API fetch failed, rendering HR Autonomous fallback projects:', error);
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
                notification.className = 'block mb-6 p-4 rounded-xl border border-[#D4AF37]/40 bg-[#D4AF37]/10 text-[#D4AF37] font-medium';
                notification.textContent = 'Thank you! Your inquiry has been sent successfully to HR Autonomous.';
                contactForm.reset();
            })
            .catch((err) => {
                // Error
                console.error('Contact Form error:', err);
                const displayMsg = (err && typeof err.message === 'string' && err.message !== '[object Object]')
                    ? err.message
                    : 'Something went wrong. Please check your connection and try again.';
                notification.className = 'block mb-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 font-medium';
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

    // -------------------------------------------------------------------------
    // 5. Interactive Chat Controller
    // -------------------------------------------------------------------------
    const chatTrigger = document.getElementById('chat-trigger');
    const chatModal = document.getElementById('chat-modal');
    const chatCloseBtn = document.getElementById('chat-close-btn');
    const chatIconOpen = document.getElementById('chat-icon-open');
    const chatIconClose = document.getElementById('chat-icon-close');
    const chatMessages = document.getElementById('chat-messages');
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatSubmitBtn = document.getElementById('chat-submit-btn');
    const chatSendIcon = document.getElementById('chat-send-icon');
    const chatSpinner = document.getElementById('chat-spinner');

    let chatHistory = [];
    let isChatOpen = false;
    let starterPromptsRendered = false;

    function renderInitialChatState() {
        if (!chatMessages || chatMessages.children.length > 0) return;

        // Render initial human greeting
        const welcomeText = "Hi, welcome to HR Autonomous. What are you working on right now?";
        appendMessageUI('assistant', welcomeText);

        // Render starter prompts
        const startersContainer = document.createElement('div');
        startersContainer.id = 'chat-starter-prompts';
        startersContainer.className = 'flex flex-wrap gap-2 pt-2 pb-1';

        const starterOptions = [
            "What can you automate?",
            "I need help with lead generation",
            "Can you automate my CRM?",
            "I want to build an AI workflow"
        ];

        starterOptions.forEach(opt => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'text-xs px-3 py-1.5 rounded-full bg-[#111111] border border-[rgba(212,175,55,0.30)] text-[#D4AF37] hover:bg-[#D4AF37]/20 hover:text-[#F5F5F5] transition duration-200 font-medium text-left';
            btn.textContent = opt;
            btn.addEventListener('click', () => {
                const starterDiv = document.getElementById('chat-starter-prompts');
                if (starterDiv) starterDiv.remove();
                sendChatMessage(opt);
            });
            startersContainer.appendChild(btn);
        });

        chatMessages.appendChild(startersContainer);
        scrollChatToBottom();
    }

    function toggleChatModal() {
        isChatOpen = !isChatOpen;
        if (isChatOpen) {
            chatModal.classList.remove('hidden');
            setTimeout(() => {
                chatModal.classList.remove('scale-95', 'opacity-0');
                chatModal.classList.add('scale-100', 'opacity-100');
                chatInput.focus();
                renderInitialChatState();
            }, 10);
            chatIconOpen.classList.add('hidden');
            chatIconClose.classList.remove('hidden');
        } else {
            chatModal.classList.remove('scale-100', 'opacity-100');
            chatModal.classList.add('scale-95', 'opacity-0');
            setTimeout(() => {
                chatModal.classList.add('hidden');
            }, 300);
            chatIconOpen.classList.remove('hidden');
            chatIconClose.classList.add('hidden');
        }
    }

    if (chatTrigger && chatModal) {
        chatTrigger.addEventListener('click', toggleChatModal);
        chatCloseBtn.addEventListener('click', toggleChatModal);
    }

    function scrollChatToBottom() {
        if (chatMessages) {
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
    }

    function appendMessageUI(role, text) {
        if (!chatMessages) return;
        const msgDiv = document.createElement('div');
        msgDiv.className = 'flex items-start ' + (role === 'user' ? 'justify-end' : '');

        if (role === 'user') {
            msgDiv.innerHTML = `
                <div class="bg-[#D4AF37] text-[#111111] font-medium rounded-2xl rounded-tr-none p-3.5 leading-relaxed max-w-[85%] shadow-md">
                    ${text}
                </div>
            `;
        } else {
            msgDiv.innerHTML = `
                <div class="bg-[#111111] border border-[rgba(212,175,55,0.25)] rounded-2xl rounded-tl-none p-3.5 text-[#F5F5F5] leading-relaxed max-w-[88%] shadow-sm">
                    ${text.replace(/\n/g, '<br>')}
                </div>
            `;
        }
        chatMessages.appendChild(msgDiv);
        scrollChatToBottom();
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.id = 'chat-typing-indicator';
        typingDiv.className = 'flex items-center space-x-2 text-[#B0B0B0] text-xs py-2 px-1';
        typingDiv.innerHTML = `
            <div class="w-2 h-2 rounded-full bg-[#D4AF37] animate-bounce"></div>
            <div class="w-2 h-2 rounded-full bg-[#F4C542] animate-bounce [animation-delay:0.2s]"></div>
            <div class="w-2 h-2 rounded-full bg-[#E6C200] animate-bounce [animation-delay:0.4s]"></div>
            <span class="text-[#B0B0B0] font-mono text-[11px]">HR Autonomous Team is typing...</span>
        `;
        chatMessages.appendChild(typingDiv);
        scrollChatToBottom();
    }

    function hideTypingIndicator() {
        const indicator = document.getElementById('chat-typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    async function sendChatMessage(userText) {
        if (!userText.trim()) return;

        // Remove starter prompts container if present
        const starterDiv = document.getElementById('chat-starter-prompts');
        if (starterDiv) starterDiv.remove();

        appendMessageUI('user', userText.trim());
        chatHistory.push({ role: 'user', content: userText.trim() });

        chatInput.value = '';
        chatSubmitBtn.disabled = true;
        chatSendIcon.classList.add('hidden');
        chatSpinner.classList.remove('hidden');
        showTypingIndicator();

        const payload = {
            messages: chatHistory.slice(-16)
        };

        let messageBubbleDiv = null;
        let aiReplyText = '';

        try {
            const res = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                throw new Error('Chat API error');
            }

            hideTypingIndicator();

            // Create streaming response bubble
            const msgContainer = document.createElement('div');
            msgContainer.className = 'flex items-start';
            messageBubbleDiv = document.createElement('div');
            messageBubbleDiv.className = 'bg-[#111111] border border-[rgba(212,175,55,0.25)] rounded-2xl rounded-tl-none p-3.5 text-[#F5F5F5] leading-relaxed max-w-[88%] shadow-sm';
            msgContainer.appendChild(messageBubbleDiv);
            chatMessages.appendChild(msgContainer);

            const reader = res.body.getReader();
            const decoder = new TextDecoder('utf-8');

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                aiReplyText += chunk;
                messageBubbleDiv.innerHTML = aiReplyText.replace(/\n/g, '<br>');
                scrollChatToBottom();
            }

            const finalChunk = decoder.decode();
            if (finalChunk) {
                aiReplyText += finalChunk;
                messageBubbleDiv.innerHTML = aiReplyText.replace(/\n/g, '<br>');
            }

            if (aiReplyText.trim()) {
                chatHistory.push({ role: 'assistant', content: aiReplyText.trim() });
            }
        } catch (err) {
            console.error('Chat error:', err);
            hideTypingIndicator();
            if (messageBubbleDiv) {
                messageBubbleDiv.innerHTML = "Something went wrong on my end. Give that another try.";
            } else {
                appendMessageUI('assistant', "Something went wrong on my end. Give that another try.");
            }
        } finally {
            chatSubmitBtn.disabled = false;
            chatSendIcon.classList.remove('hidden');
            chatSpinner.classList.add('hidden');
        }
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (chatForm) chatForm.requestSubmit();
            }
        });
    }

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const text = chatInput.value.trim();
            if (text) {
                sendChatMessage(text);
            }
        });
    }

    // -------------------------------------------------------------------------
    // 6. CRM & System Operational Status Fetcher
    // -------------------------------------------------------------------------
    function loadCRMStatus() {
        const statusText = document.getElementById('crm-status-text');
        if (!statusText) return;

        fetch('/api/crm/status')
            .then(res => res.ok ? res.json() : null)
            .then(data => {
                if (data && data.system_status) {
                    statusText.textContent = `CRM: ${data.system_status.toUpperCase()} (${data.total_contact_messages} Leads)`;
                }
            })
            .catch(err => {
                console.warn('CRM Status sync notice:', err);
            });
    }

    // Global API utilities for developer console / extended inspection
    window.HRAutonomousAPI = {
        getCRMStatus: () => fetch('/api/crm/status').then(r => r.json()),
        getSettings: () => fetch('/api/settings').then(r => r.json()),
        getAuditLogs: (limit = 20) => fetch(`/api/audit-logs?limit=${limit}`).then(r => r.json())
    };

    loadCRMStatus();
});

