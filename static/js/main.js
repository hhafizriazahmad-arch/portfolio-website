document.addEventListener('DOMContentLoaded', () => {
    // -------------------------------------------------------------------------
    // 1. Interactive Canvas Background (Gray & Gold Luxury Network Grid)
    // -------------------------------------------------------------------------
    const canvas = document.getElementById('bg-canvas');
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (canvas && !prefersReducedMotion) {
        const ctx = canvas.getContext('2d');

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        window.addEventListener('resize', () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        });

        const particles = [];
        const maxParticles = 55;
        const maxDistance = 120;

        class Particle {
            constructor() {
                this.x = Math.random() * width;
                this.y = Math.random() * height;
                this.vx = (Math.random() - 0.5) * 0.35;
                this.vy = (Math.random() - 0.5) * 0.35;
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
                ctx.fillStyle = 'rgba(212, 175, 55, 0.45)';
                ctx.fill();
            }
        }

        // Initialize particles
        for (let i = 0; i < maxParticles; i++) {
            particles.push(new Particle());
        }

        let animationFrameId;
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
                        const alpha = (1 - dist / maxDistance) * 0.18;
                        ctx.strokeStyle = `rgba(212, 175, 55, ${alpha})`;
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    }
                }
            }
            animationFrameId = requestAnimationFrame(animate);
        }
        animate();

        // Pause animation when tab is inactive to preserve performance
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                cancelAnimationFrame(animationFrameId);
            } else {
                animationFrameId = requestAnimationFrame(animate);
            }
        });
    }

    // -------------------------------------------------------------------------
    // 2. Mobile Menu Toggle & Accessibility
    // -------------------------------------------------------------------------
    const menuBtn = document.getElementById('menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.addEventListener('click', () => {
            const isHidden = mobileMenu.classList.toggle('hidden');
            const isExpanded = !isHidden;
            menuBtn.setAttribute('aria-expanded', isExpanded ? 'true' : 'false');
            
            const spans = menuBtn.querySelectorAll('span');
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
                menuBtn.setAttribute('aria-expanded', 'false');
                const spans = menuBtn.querySelectorAll('span');
                spans[0].classList.remove('rotate-45', 'translate-y-1.5');
                spans[1].classList.remove('opacity-0');
                spans[2].classList.remove('-rotate-45', '-translate-y-1.5');
            });
        });
    }

    // -------------------------------------------------------------------------
    // 3. Dynamic Projects Fetch & Progressive Enhancement
    // -------------------------------------------------------------------------
    const projectsGrid = document.getElementById('projects-grid');

    const svgIcons = {
        'shopping-cart': `<svg class="w-6 h-6 text-[#D4AF37]" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
        </svg>`,
        'cpu': `<svg class="w-6 h-6 text-[#D4AF37]" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>`,
        'database': `<svg class="w-6 h-6 text-[#D4AF37]" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 7v10c0 2.21 3.58 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.58 4 8 4s8-1.79 8-4M4 7c0-2.21 3.58-4 8-4s8 1.79 8 4m0 5c0 2.21-3.58 4-8 4s-8-1.79-8-4" />
        </svg>`,
        'chat': `<svg class="w-6 h-6 text-[#D4AF37]" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M8 10h.01M12 10h.01M16 10h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>`,
        'default': `<svg class="w-6 h-6 text-[#D4AF37]" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>`
    };

    const fallbackProjects = [
        {
            title: "AI Agency Operating System",
            description: "An enterprise-grade autonomous workflow orchestration engine executing a 16-stage deterministic pipeline. Features automated BANT lead qualification, Gemini-powered proposal generation, human-in-the-loop approval gates, dynamic revenue attribution, and real-time Google Sheets audit synchronization.",
            tech_stack: "Next.js, TypeScript, Prisma ORM, SQLite, Gemini AI, Google Sheets API, Slack Webhooks, Vercel",
            github_url: "https://github.com/hhafizriazahmad-arch/AI-agency-operating-system",
            live_url: "https://ai-agency-operating-system-gamma.vercel.app",
            icon_type: "cpu"
        },
        {
            title: "AI Lead Intelligence System",
            description: "An automated B2B lead generation pipeline engineered to identify, enrich, and qualify profiles of founders and C-level executives. Built on FastAPI and Gemini AI for high-impact prospect research.",
            tech_stack: "Python, FastAPI, Playwright, Gemini AI, HubSpot API, Slack Webhooks, Vercel",
            github_url: "https://github.com/hhafizriazahmad-arch/ai-lead-intelligence-system",
            live_url: "https://ai-lead-intelligence-system.vercel.app",
            icon_type: "database"
        },
        {
            title: "Autonomous AI Conversational Agent",
            description: "A responsive AI chatbot platform engineered with Google Gemini AI integration, contextual knowledge-base retrieval, automated multi-turn query handling, and conversational response validation. Features automated fallback handlers, conversation history tracking, and serverless edge deployment.",
            tech_stack: "JavaScript, Node.js, Express, Gemini AI, Knowledge Retrieval, Vercel",
            github_url: "https://github.com/hhafizriazahmad-arch/chat-bot",
            live_url: "https://chat-bot-chi-wine.vercel.app",
            icon_type: "chat"
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
            // Keep existing prerendered cards if available
            if (projectsGrid.querySelectorAll('article').length > 0) {
                return;
            }
            projectsGrid.innerHTML = `
                <div class="col-span-full text-center py-8 text-[#B0B0B0]">
                    No case studies available at the moment. Please check back soon.
                </div>`;
            return;
        }

        projectsGrid.innerHTML = '';
        projects.forEach(project => {
            const iconSvg = svgIcons[project.icon_type] || svgIcons['default'];
            const techStackBadges = project.tech_stack.split(',').map(tech => 
                `<span class="text-xs px-2.5 py-1 rounded bg-[#1E1E1E] border border-[rgba(212,175,55,0.25)] text-[#D4AF37] font-mono">${tech.trim()}</span>`
            ).join('');

            const liveLink = project.live_url ? `
                <a href="${project.live_url}" target="_blank" rel="noopener noreferrer" class="text-xs px-3 py-1.5 rounded-lg bg-[#D4AF37] text-[#111111] font-bold hover:bg-[#F4C542] transition flex items-center space-x-1">
                    <span>Live</span>
                    <svg class="w-3.5 h-3.5" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>` : '';

            const githubLink = project.github_url ? `
                <a href="${project.github_url}" target="_blank" rel="noopener noreferrer" class="text-[#B0B0B0] hover:text-[#F4C542] transition flex items-center space-x-1 text-sm font-medium">
                    <span>GitHub</span>
                    <svg class="w-4 h-4" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24" aria-hidden="true"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>` : '';

            const projectCard = document.createElement('article');
            projectCard.className = 'p-8 rounded-3xl glass-panel flex flex-col space-y-6 transition-all duration-300 group';
            projectCard.innerHTML = `
                <div class="flex items-center justify-between">
                    <div class="w-12 h-12 rounded-xl bg-[#D4AF37]/10 border border-[rgba(212,175,55,0.25)] flex items-center justify-center group-hover:bg-[#D4AF37]/20 transition-all duration-300">
                        ${iconSvg}
                    </div>
                    <div class="flex items-center space-x-3">
                        ${liveLink}
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
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 6000);

        fetch('/api/projects', { signal: controller.signal })
            .then(response => {
                clearTimeout(timeoutId);
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(projects => {
                if (projects && projects.length > 0) {
                    renderProjectsList(projects);
                }
            })
            .catch(error => {
                clearTimeout(timeoutId);
                console.warn('Backend API fetch notice (preserving prerendered cards):', error);
                // If the grid was completely empty, populate with fallback
                if (projectsGrid && projectsGrid.querySelectorAll('article').length === 0) {
                    renderProjectsList(fallbackProjects);
                }
            });
    }

    // Attempt progressive refresh without disturbing prerendered cards
    loadProjects();

    // -------------------------------------------------------------------------
    // 4. Contact Form AJAX Submission with Client Validation
    // -------------------------------------------------------------------------
    const contactForm = document.getElementById('contact-form');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnSpinner = document.getElementById('btn-spinner');
    const notification = document.getElementById('form-notification');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const subjectInput = document.getElementById('subject');
            const messageInput = document.getElementById('message');

            const name = nameInput.value.trim();
            const email = emailInput.value.trim();
            const subject = subjectInput.value.trim();
            const message = messageInput.value.trim();

            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

            if (!name || !email || !subject || !message) {
                notification.className = 'block mb-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 font-medium';
                notification.textContent = 'Please fill out all required fields before submitting.';
                return;
            }

            if (!emailRegex.test(email)) {
                notification.className = 'block mb-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 font-medium';
                notification.textContent = 'Please provide a valid email address.';
                emailInput.focus();
                return;
            }

            // Form payload
            const payload = { name, email, subject, message };

            // Loading state UI
            submitBtn.disabled = true;
            btnText.textContent = 'Sending Message...';
            btnSpinner.classList.remove('hidden');
            notification.className = 'hidden';

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
                notification.className = 'block mb-6 p-4 rounded-xl border border-[#D4AF37]/40 bg-[#D4AF37]/10 text-[#D4AF37] font-medium';
                notification.textContent = 'Thank you! Your message has been sent directly to Riaz Ahmad. I will review your details and respond promptly.';
                contactForm.reset();
            })
            .catch((err) => {
                console.error('Contact Form error:', err);
                const displayMsg = (err && typeof err.message === 'string' && err.message !== '[object Object]')
                    ? err.message
                    : 'Something went wrong. Please check your connection or email me directly at hafizriaz.ai@gmail.com.';
                notification.className = 'block mb-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 font-medium';
                notification.textContent = displayMsg;
            })
            .finally(() => {
                submitBtn.disabled = false;
                btnText.textContent = 'Send Automation Inquiry';
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

    function renderInitialChatState() {
        if (!chatMessages || chatMessages.children.length > 0) return;

        const welcomeText = "Hey! I'm Riaz Ahmad. Thanks for visiting. What specific workflow, lead process, or backend system are you looking to automate?";
        appendMessageUI('assistant', welcomeText);

        const startersContainer = document.createElement('div');
        startersContainer.id = 'chat-starter-prompts';
        startersContainer.className = 'flex flex-wrap gap-2 pt-2 pb-1';

        const starterOptions = [
            "What can you automate?",
            "I need lead generation pipelines",
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
        if (chatTrigger) {
            chatTrigger.setAttribute('aria-expanded', isChatOpen ? 'true' : 'false');
        }
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
            <span class="text-[#B0B0B0] font-sans text-[11px]">Riaz Ahmad is typing...</span>
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
            const fallbackMsg = "Something went wrong on my end. Feel free to reach me directly at hafizriaz.ai@gmail.com or try again.";
            if (messageBubbleDiv) {
                messageBubbleDiv.innerHTML = fallbackMsg;
            } else {
                appendMessageUI('assistant', fallbackMsg);
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
