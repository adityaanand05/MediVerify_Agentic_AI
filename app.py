from flask import Flask, render_template_string, request, jsonify, send_file, session
import random
import datetime
import io
import csv
import os
import requests
import json
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # For session

# ==========================================
# NPI Validation Function
# ==========================================

def validate_npi_real(npi):
    """
    Validate NPI using official NPPES API.
    Returns dict with 'valid': bool, 'provider': data if valid.
    """
    if not re.match(r'^\d{10}$', npi):
        return {'valid': False, 'error': 'Invalid NPI format'}

    url = f"https://npiregistry.cms.hhs.gov/api/?version=2.1&number={npi}"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        if data.get('result_count', 0) == 1:
            provider = data['results'][0]
            status = provider.get('basic', {}).get('status', '') == 'A'
            if status:
                return {
                    'valid': True,
                    'provider': provider
                }
            else:
                return {'valid': False, 'error': 'Inactive provider'}
        else:
            return {'valid': False, 'error': 'NPI not found'}
    except requests.RequestException as e:
        return {'valid': False, 'error': f'API error: {str(e)}'}
    except (json.JSONDecodeError, KeyError) as e:
        return {'valid': False, 'error': f'Invalid response: {str(e)}'}

# ==========================================
# Shared Navigation Template
# ==========================================

NAV_TEMPLATE = """
<!-- Navigation -->
<nav class="glass fixed w-full z-50 transition-all duration-300" id="navbar">
    <div class="container mx-auto px-6 py-4">
        <div class="flex items-center justify-between">
            <!-- Logo -->
            <a href="/" class="flex items-center gap-3 group">
                <div class="bg-brand-600 text-white w-10 h-10 rounded-xl flex items-center justify-center shadow-lg shadow-brand-500/30 group-hover:scale-105 transition-transform">
                    <i class="fa-solid fa-staff-snake text-xl"></i>
                </div>
                <div class="flex flex-col">
                    <span class="text-xl font-bold tracking-tight text-slate-900 dark:text-white leading-none">Mediverify<span class="text-brand-600 dark:text-brand-400">AI</span></span>
                </div>
            </a>

            <!-- Desktop Links -->
            <div class="hidden md:flex items-center gap-8">
                <a href="#features" class="text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 transition-colors">Features</a>
                <a href="#how-it-works" class="text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 transition-colors">How it Works</a>
                <a href="#faq" class="text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 transition-colors">FAQ</a>
            </div>

            <!-- Right Actions -->
            <div class="hidden md:flex items-center gap-4">
                
                <!-- Dark Mode Toggle -->
                <button onclick="toggleDarkMode()" class="w-10 h-10 rounded-full flex items-center justify-center text-slate-600 dark:text-yellow-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors">
                    <i class="fa-solid fa-moon dark:hidden"></i>
                    <i class="fa-solid fa-sun hidden dark:block"></i>
                </button>

                <a href="/validator" class="text-sm font-semibold text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 flex items-center gap-2">
                    <i class="fa-solid fa-shield-halved"></i> Bulk Validator
                </a>
                
                <button onclick="openModal('loginModal')" class="bg-slate-900 dark:bg-white dark:text-slate-900 text-white px-5 py-2.5 rounded-lg text-sm font-semibold hover:bg-slate-800 dark:hover:bg-slate-200 transition-all hover:shadow-lg hover:-translate-y-0.5">
                    Log In
                </button>
            </div>

            <!-- Mobile Menu Button -->
            <button class="md:hidden text-slate-700 dark:text-slate-200 text-2xl" onclick="toggleMobileMenu()">
                <i class="fa-solid fa-bars"></i>
            </button>
        </div>
    </div>

    <!-- Mobile Menu -->
    <div id="mobile-menu" class="hidden md:hidden bg-white dark:bg-dark-900 border-t border-slate-100 dark:border-slate-800 absolute w-full shadow-xl">
        <div class="flex flex-col p-4 space-y-4">
            <a href="#features" class="text-slate-600 dark:text-slate-300 font-medium" onclick="toggleMobileMenu()">Features</a>
            <a href="#how-it-works" class="text-slate-600 dark:text-slate-300 font-medium" onclick="toggleMobileMenu()">How it Works</a>
            <a href="#faq" class="text-slate-600 dark:text-slate-300 font-medium" onclick="toggleMobileMenu()">FAQ</a>
            <hr class="border-slate-100 dark:border-slate-800">
            <div class="flex items-center justify-between">
                <span class="text-slate-600 dark:text-slate-300 font-medium">Theme</span>
                <button onclick="toggleDarkMode()" class="text-slate-600 dark:text-yellow-400">
                    <i class="fa-solid fa-moon dark:hidden"></i>
                    <i class="fa-solid fa-sun hidden dark:block"></i>
                </button>
            </div>
            <button onclick="openModal('loginModal'); toggleMobileMenu()" class="w-full bg-brand-600 text-white px-4 py-2 rounded-lg font-medium">Log In</button>
        </div>
    </div>
</nav>
"""

# ==========================================
# Shared Footer Template
# ==========================================

FOOTER_TEMPLATE = """
<!-- Footer -->
<footer class="bg-dark-900 dark:bg-black text-white pt-20 pb-10 border-t dark:border-slate-800">
    <div class="container mx-auto px-6">
        <div class="grid md:grid-cols-2 lg:grid-cols-4 gap-12 mb-16">
            
            <!-- Brand Column -->
            <div class="space-y-6">
                <div class="flex items-center gap-2">
                    <div class="bg-brand-600 text-white w-8 h-8 rounded-lg flex items-center justify-center">
                        <i class="fa-solid fa-staff-snake"></i>
                    </div>
                    <span class="text-xl font-bold tracking-tight">MediverifyAI</span>
                </div>
                <p class="text-slate-400 text-sm leading-relaxed">
                    The trusted standard for healthcare data verification. Empowering organizations with AI-driven insights.
                </p>
                <div class="flex gap-4">
                    <a href="#" class="w-10 h-10 rounded-full bg-dark-800 dark:bg-slate-900 flex items-center justify-center hover:bg-brand-600 transition-colors"><i class="fa-brands fa-twitter"></i></a>
                    <a href="#" class="w-10 h-10 rounded-full bg-dark-800 dark:bg-slate-900 flex items-center justify-center hover:bg-brand-600 transition-colors"><i class="fa-brands fa-linkedin"></i></a>
                    <a href="#" class="w-10 h-10 rounded-full bg-dark-800 dark:bg-slate-900 flex items-center justify-center hover:bg-brand-600 transition-colors"><i class="fa-brands fa-github"></i></a>
                </div>
            </div>

            <!-- Links Column -->
            <div>
                <h4 class="font-bold text-lg mb-6">Product</h4>
                <ul class="space-y-4 text-sm text-slate-400">
                    <li><a href="#" class="hover:text-brand-500 transition-colors">NPI Lookup</a></li>
                    <li><a href="#" class="hover:text-brand-500 transition-colors">Bulk Search</a></li>
                    <li><a href="#" class="hover:text-brand-500 transition-colors">API Documentation</a></li>
                    <li><a href="#" class="hover:text-brand-500 transition-colors">Pricing</a></li>
                </ul>
            </div>

            <!-- Links Column -->
            <div>
                <h4 class="font-bold text-lg mb-6">Company</h4>
                <ul class="space-y-4 text-sm text-slate-400">
                    <li><a href="#" class="hover:text-brand-500 transition-colors">About Us</a></li>
                    <li><a href="#" class="hover:text-brand-500 transition-colors">Careers</a></li>
                    <li><a href="#" class="hover:text-brand-500 transition-colors">Privacy Policy</a></li>
                    <li><a href="#" class="hover:text-brand-500 transition-colors">Terms of Service</a></li>
                </ul>
            </div>

            <!-- Newsletter Column -->
            <div>
                <h4 class="font-bold text-lg mb-6">Stay Updated</h4>
                <p class="text-slate-400 text-sm mb-4">Subscribe to our newsletter for the latest healthcare data trends.</p>
                <form onsubmit="handleSubscribe(event)" class="relative">
                    <input type="email" required placeholder="Enter your email" class="w-full bg-dark-800 dark:bg-slate-900 border border-slate-700 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-brand-500 text-sm">
                    <button type="submit" class="absolute right-1 top-1 bottom-1 bg-brand-600 px-4 rounded-md text-sm font-bold hover:bg-brand-500 transition-colors">
                        <i class="fa-solid fa-arrow-right"></i>
                    </button>
                </form>
            </div>
        </div>

        <div class="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p class="text-slate-500 text-sm">© 2024 MediverifyAI Inc. All rights reserved.</p>
            <div class="flex gap-6 text-sm text-slate-500">
                <a href="#" class="hover:text-white">Privacy</a>
                <a href="#" class="hover:text-white">Cookies</a>
                <a href="#" class="hover:text-white">Security</a>
            </div>
        </div>
    </div>
</footer>
"""

# ==========================================
# Shared Login Modal Template
# ==========================================

LOGIN_MODAL_TEMPLATE = """
<!-- Login Modal -->
<div id="loginModal" class="fixed inset-0 z-[60] hidden transition-opacity duration-300 opacity-0 modal-container" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" onclick="closeModal('loginModal')"></div>
    <div class="fixed inset-0 z-10 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
            <div class="relative transform overflow-hidden rounded-2xl bg-white dark:bg-dark-800 text-left shadow-2xl transition-all w-full max-w-md border border-slate-100 dark:border-slate-700 scale-95 transition-transform duration-300 modal-panel">
                <div class="p-8">
                    <div class="text-center mb-8">
                        <div class="bg-brand-600 text-white w-12 h-12 rounded-xl flex items-center justify-center shadow-lg mx-auto mb-4">
                            <i class="fa-solid fa-staff-snake text-2xl"></i>
                        </div>
                        <h3 class="text-2xl font-bold text-slate-900 dark:text-white">Welcome Back</h3>
                        <p class="text-sm text-slate-500 dark:text-slate-400 mt-2">Sign in to access your dashboard</p>
                    </div>
                    
                    <form onsubmit="handleLogin(event)" class="space-y-4">
                        <div>
                            <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase mb-2">Email Address</label>
                            <input type="email" required class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg p-3 text-sm focus:ring-2 focus:ring-brand-500 outline-none transition-all text-slate-900 dark:text-white" placeholder="name@company.com">
                        </div>
                        <div>
                            <label class="block text-xs font-bold text-slate-700 dark:text-slate-300 uppercase mb-2">Password</label>
                            <input type="password" required class="w-full bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg p-3 text-sm focus:ring-2 focus:ring-brand-500 outline-none transition-all text-slate-900 dark:text-white" placeholder="••••••••">
                        </div>
                        
                        <div class="flex items-center justify-between text-xs">
                            <label class="flex items-center gap-2 text-slate-600 dark:text-slate-400 cursor-pointer">
                                <input type="checkbox" class="rounded border-slate-300 text-brand-600 focus:ring-brand-500">
                                Remember me
                            </label>
                            <a href="#" class="text-brand-600 dark:text-brand-400 hover:underline">Forgot password?</a>
                        </div>

                        <button type="submit" class="w-full bg-slate-900 dark:bg-white dark:text-slate-900 text-white py-3 rounded-lg font-bold hover:bg-slate-800 dark:hover:bg-slate-200 transition-colors shadow-lg">
                            Sign In
                        </button>
                    </form>

                    <div class="mt-6 text-center text-xs text-slate-500 dark:text-slate-400">
                        Don't have an account? <a href="#" class="text-brand-600 dark:text-brand-400 font-bold hover:underline">Sign up</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
"""

# ==========================================
# Shared Scripts (Common JS functions)
# ==========================================

SHARED_SCRIPTS = """
<script>
    // --- Dark Mode Logic ---
    function toggleDarkMode() {
        const html = document.documentElement;
        if (html.classList.contains('dark')) {
            html.classList.remove('dark');
            localStorage.setItem('theme', 'light');
        } else {
            html.classList.add('dark');
            localStorage.setItem('theme', 'dark');
        }
    }

    // Initialize theme
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
        document.documentElement.classList.add('dark');
    } else {
        document.documentElement.classList.remove('dark');
    }

    // --- Generic Modal Logic ---
    function openModal(id) {
        const modal = document.getElementById(id);
        const panel = modal.querySelector('.modal-panel');
        modal.classList.remove('hidden');
        setTimeout(() => {
            modal.classList.remove('opacity-0');
            panel.classList.remove('scale-95');
            panel.classList.add('scale-100');
        }, 10);
    }

    function closeModal(id) {
        const modal = document.getElementById(id);
        const panel = modal.querySelector('.modal-panel');
        modal.classList.add('opacity-0');
        panel.classList.remove('scale-100');
        panel.classList.add('scale-95');
        setTimeout(() => modal.classList.add('hidden'), 300);
    }

    // --- Login Logic ---
    function handleLogin(e) {
        e.preventDefault();
        const btn = e.target.querySelector('button[type="submit"]');
        const originalText = btn.innerHTML;
        
        btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i>';
        btn.disabled = true;
        
        setTimeout(() => {
            btn.innerHTML = originalText;
            btn.disabled = false;
            closeModal('loginModal');
            showToast('Welcome back! You have successfully logged in.', 'success');
        }, 1500);
    }

    // --- Newsletter Subscription ---
    function handleSubscribe(e) {
        e.preventDefault();
        const btn = e.target.querySelector('button');
        const originalIcon = btn.innerHTML;
        
        btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
        setTimeout(() => {
            btn.innerHTML = originalIcon;
            e.target.reset();
            showToast("You've been subscribed to the newsletter!");
        }, 1000);
    }

    // --- Toast Notifications ---
    function showToast(message, type='success') {
        const container = document.getElementById('toast-container');
        if (!container) return; // Skip if no container
        const toast = document.createElement('div');
        
        const colors = type === 'success' ? 'bg-green-600' : 'bg-red-600';
        const icon = type === 'success' ? 'fa-check' : 'fa-exclamation-triangle';

        toast.className = `${colors} text-white px-6 py-4 rounded-lg shadow-xl flex items-center gap-3 transform translate-y-10 opacity-0 transition-all duration-300 min-w-[300px] border border-white/10`;
        toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span class="font-medium text-sm">${message}</span>`;
        
        container.appendChild(toast);
        
        requestAnimationFrame(() => {
            toast.classList.remove('translate-y-10', 'opacity-0');
        });

        setTimeout(() => {
            toast.classList.add('translate-y-10', 'opacity-0');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    // --- Mobile Menu ---
    function toggleMobileMenu() {
        const menu = document.getElementById('mobile-menu');
        menu.classList.toggle('hidden');
    }
</script>
"""

# ==========================================
# Frontend Template (HTML/Tailwind/JS) - Main Page
# ==========================================

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MediverifyAI - Intelligent Healthcare Verification</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- Tailwind Config -->
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            50: '#f0f9ff',
                            100: '#e0f2fe',
                            500: '#0ea5e9',
                            600: '#0284c7', // Primary Blue
                            700: '#0369a1',
                            800: '#075985',
                            900: '#0c4a6e',
                        },
                        dark: {
                            950: '#020617', // Deepest background
                            900: '#0f172a',
                            800: '#1e293b',
                            700: '#334155',
                        }
                    },
                    animation: {
                        'float': 'float 6s ease-in-out infinite',
                        'blob': 'blob 10s infinite',
                    },
                    keyframes: {
                        float: {
                            '0%, 100%': { transform: 'translateY(0)' },
                            '50%': { transform: 'translateY(-10px)' },
                        },
                        blob: {
                            '0%': { transform: 'translate(0px, 0px) scale(1)' },
                            '33%': { transform: 'translate(30px, -50px) scale(1.1)' },
                            '66%': { transform: 'translate(-20px, 20px) scale(0.9)' },
                            '100%': { transform: 'translate(0px, 0px) scale(1)' },
                        }
                    }
                }
            }
        }
    </script>

    <style>
        /* Base Styles */
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        
        /* Glassmorphism - Light */
        .glass {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.6);
        }
        
        /* Glassmorphism - Dark */
        .dark .glass {
            background: rgba(15, 23, 42, 0.85);
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        }

        /* Scroll Animations */
        .reveal {
            opacity: 0;
            transform: translateY(30px);
            transition: all 0.8s ease-out;
        }
        .reveal.active {
            opacity: 1;
            transform: translateY(0);
        }

        /* Typewriter Cursor */
        .cursor::after {
            content: '|';
            animation: blink 1s step-start infinite;
        }
        @keyframes blink { 50% { opacity: 0; } }
        
        /* Custom Scrollbar */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        .dark ::-webkit-scrollbar-thumb { background: #475569; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 dark:bg-dark-950 dark:text-slate-200 antialiased overflow-x-hidden relative transition-colors duration-300">

    <!-- Toast Notification Container -->
    <div id="toast-container" class="fixed bottom-5 right-5 z-[100] flex flex-col gap-3"></div>

    <!-- Background Blobs -->
    <div class="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        <div class="absolute top-0 right-0 w-[500px] h-[500px] bg-brand-100 dark:bg-brand-900/20 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-50 animate-blob"></div>
        <div class="absolute bottom-0 left-0 w-[500px] h-[500px] bg-purple-100 dark:bg-purple-900/20 rounded-full mix-blend-multiply dark:mix-blend-screen filter blur-3xl opacity-50 animate-blob animation-delay-2000"></div>
    </div>

""" + NAV_TEMPLATE + LOGIN_MODAL_TEMPLATE + """

    <!-- Hero Section -->
    <section class="pt-32 pb-20 lg:pt-48 lg:pb-32 px-6 relative">
        <div class="container mx-auto grid lg:grid-cols-2 gap-12 items-center">
            
            <!-- Hero Text -->
            <div class="max-w-2xl reveal active">
                <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 dark:bg-blue-900/30 border border-blue-100 dark:border-blue-800 text-blue-700 dark:text-blue-300 text-xs font-bold uppercase tracking-wide mb-6">
                    <span class="relative flex h-2 w-2">
                      <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                      <span class="relative inline-flex rounded-full h-2 w-2 bg-blue-500"></span>
                    </span>
                    Live Database v3.1
                </div>
                
                <h1 class="text-5xl lg:text-6xl font-extrabold text-slate-900 dark:text-white leading-[1.15] mb-6">
                    Verified Healthcare Data,<br>
                    <span class="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-purple-600 cursor">Powered by AI</span>
                </h1>
                
                <p class="text-lg text-slate-600 dark:text-slate-400 mb-10 leading-relaxed max-w-lg">
                    Instantly validate NPI numbers, check medical licenses, and screen sanctions with our real-time, AI-driven compliance engine.
                </p>

                <!-- Search Box -->
                <div class="relative max-w-xl group z-20">
                    <div class="absolute -inset-0.5 bg-gradient-to-r from-brand-500 to-purple-500 rounded-2xl blur opacity-30 group-hover:opacity-60 transition duration-200"></div>
                    <div class="relative bg-white dark:bg-dark-800 rounded-xl shadow-xl flex items-center p-2 border border-transparent dark:border-slate-700">
                        <i class="fa-solid fa-search text-slate-400 ml-4 text-lg"></i>
                        <input type="text" 
                               id="heroSearch"
                               onkeyup="handleSearch(this.value)"
                               placeholder="Search NPI, Name, or Specialty..." 
                               class="w-full p-4 text-slate-700 dark:text-slate-200 font-medium outline-none bg-transparent placeholder-slate-400">
                        <button class="bg-brand-600 text-white p-3.5 px-8 rounded-lg font-semibold hover:bg-brand-700 transition-colors shadow-lg shadow-brand-500/30">
                            Search
                        </button>
                    </div>

                    <!-- Dropdown Results -->
                    <div id="searchResults" class="absolute top-full left-0 right-0 mt-4 bg-white dark:bg-dark-800 rounded-xl shadow-2xl border border-slate-100 dark:border-slate-700 hidden overflow-hidden">
                        <div id="resultsContent" class="max-h-64 overflow-y-auto"></div>
                    </div>
                </div>

                <div class="mt-8 flex items-center gap-4 text-sm text-slate-500 dark:text-slate-400">
                    <div class="flex -space-x-2">
                        <img class="w-8 h-8 rounded-full border-2 border-white dark:border-dark-900" src="https://i.pravatar.cc/100?img=1" alt="">
                        <img class="w-8 h-8 rounded-full border-2 border-white dark:border-dark-900" src="https://i.pravatar.cc/100?img=2" alt="">
                        <img class="w-8 h-8 rounded-full border-2 border-white dark:border-dark-900" src="https://i.pravatar.cc/100?img=3" alt="">
                    </div>
                    <span>Trusted by 2,000+ Providers</span>
                </div>
            </div>

            <!-- Hero Image/Illustration -->
            <div class="relative lg:h-[600px] flex items-center justify-center reveal delay-200">
                <div class="relative w-full max-w-md">
                    <!-- Main Card -->
                    <div class="bg-white dark:bg-dark-800 rounded-2xl shadow-2xl overflow-hidden border border-slate-100 dark:border-slate-700 relative z-10 animate-float">
                        <div class="bg-slate-900 dark:bg-black p-4 flex items-center justify-between">
                            <div class="flex gap-2">
                                <div class="w-3 h-3 rounded-full bg-red-500"></div>
                                <div class="w-3 h-3 rounded-full bg-yellow-500"></div>
                                <div class="w-3 h-3 rounded-full bg-green-500"></div>
                            </div>
                            <div class="text-xs text-slate-400 font-mono">analysis_result.json</div>
                        </div>
                        <div class="p-6 space-y-4">
                            <div class="flex items-center gap-4 border-b border-slate-100 dark:border-slate-700 pb-4">
                                <div class="w-12 h-12 bg-blue-100 dark:bg-blue-900/50 rounded-full flex items-center justify-center text-blue-600 dark:text-blue-400 text-xl font-bold">JD</div>
                                <div>
                                    <div class="font-bold text-slate-900 dark:text-white">Dr. John Doe</div>
                                    <div class="text-xs text-slate-500 dark:text-slate-400">Cardiology • NPI #1425369874</div>
                                </div>
                                <div class="ml-auto bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-1 rounded text-xs font-bold">ACTIVE</div>
                            </div>
                            <div class="space-y-2">
                                <div class="flex justify-between text-sm">
                                    <span class="text-slate-500 dark:text-slate-400">License Status</span>
                                    <span class="font-semibold text-slate-900 dark:text-white"><i class="fa-solid fa-check-circle text-green-500 mr-1"></i> Verified</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-slate-500 dark:text-slate-400">OIG Exclusions</span>
                                    <span class="font-semibold text-slate-900 dark:text-white">None Found</span>
                                </div>
                                <div class="flex justify-between text-sm">
                                    <span class="text-slate-500 dark:text-slate-400">Credibility Score</span>
                                    <span class="font-semibold text-brand-600 dark:text-brand-400">98/100</span>
                                </div>
                            </div>
                            <div class="h-2 w-full bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden mt-2">
                                <div class="h-full bg-brand-500 w-[98%]"></div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Decorative Elements -->
                    <div class="absolute -right-8 top-20 bg-white dark:bg-dark-800 p-4 rounded-xl shadow-lg border border-slate-100 dark:border-slate-700 z-20 animate-float" style="animation-delay: 2s;">
                        <i class="fa-solid fa-database text-purple-500 text-2xl mb-2"></i>
                        <div class="text-xs font-bold text-slate-900 dark:text-white">Syncing with NPPES</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Stats Section -->
    <section class="py-10 bg-white dark:bg-dark-900 border-y border-slate-100 dark:border-slate-800 transition-colors duration-300">
        <div class="container mx-auto px-6 grid grid-cols-2 md:grid-cols-4 gap-8 text-center divide-x divide-slate-100 dark:divide-slate-800">
            <div class="reveal">
                <div class="text-4xl font-bold text-slate-900 dark:text-white mb-1 counter" data-target="5">0</div>
                <div class="text-sm text-slate-500 dark:text-slate-400 font-medium">Million Records</div>
            </div>
            <div class="reveal delay-100">
                <div class="text-4xl font-bold text-slate-900 dark:text-white mb-1 counter" data-target="99">0</div>
                <div class="text-sm text-slate-500 dark:text-slate-400 font-medium">% Accuracy</div>
            </div>
            <div class="reveal delay-200">
                <div class="text-4xl font-bold text-slate-900 dark:text-white mb-1 counter" data-target="50">0</div>
                <div class="text-sm text-slate-500 dark:text-slate-400 font-medium">States Covered</div>
            </div>
            <div class="reveal delay-300">
                <div class="text-4xl font-bold text-slate-900 dark:text-white mb-1 counter" data-target="24">0</div>
                <div class="text-sm text-slate-500 dark:text-slate-400 font-medium">/7 Support</div>
            </div>
        </div>
    </section>

    <!-- Features Section -->
    <section id="features" class="py-24 px-6 bg-slate-50 dark:bg-dark-950 relative transition-colors duration-300">
        <div class="container mx-auto">
            <div class="text-center max-w-3xl mx-auto mb-16 reveal">
                <h2 class="text-3xl lg:text-4xl font-bold text-slate-900 dark:text-white mb-4">Why Choose MediverifyAI?</h2>
                <p class="text-slate-600 dark:text-slate-400">We combine official government databases with advanced machine learning to provide the most accurate healthcare provider data API on the market.</p>
            </div>

            <div class="grid md:grid-cols-3 gap-8">
                <!-- Card 1 -->
                <div class="bg-white dark:bg-dark-800 p-8 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group reveal">
                    <div class="w-14 h-14 bg-brand-50 dark:bg-brand-900/30 rounded-xl flex items-center justify-center text-brand-600 dark:text-brand-400 text-2xl mb-6 group-hover:bg-brand-600 group-hover:text-white transition-colors">
                        <i class="fa-solid fa-bolt"></i>
                    </div>
                    <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-3">Real-Time Validation</h3>
                    <p class="text-slate-500 dark:text-slate-400 leading-relaxed">Direct connection to NPPES and state licensing boards ensures data is never stale.</p>
                </div>

                <!-- Card 2 -->
                <div class="bg-white dark:bg-dark-800 p-8 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group reveal delay-100">
                    <div class="w-14 h-14 bg-purple-50 dark:bg-purple-900/30 rounded-xl flex items-center justify-center text-purple-600 dark:text-purple-400 text-2xl mb-6 group-hover:bg-purple-600 group-hover:text-white transition-colors">
                        <i class="fa-solid fa-brain"></i>
                    </div>
                    <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-3">AI Anomaly Detection</h3>
                    <p class="text-slate-500 dark:text-slate-400 leading-relaxed">Our algorithms flag suspicious patterns and potential fraud risks in provider profiles.</p>
                </div>

                <!-- Card 3 -->
                <div class="bg-white dark:bg-dark-800 p-8 rounded-2xl shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 group reveal delay-200">
                    <div class="w-14 h-14 bg-emerald-50 dark:bg-emerald-900/30 rounded-xl flex items-center justify-center text-emerald-600 dark:text-emerald-400 text-2xl mb-6 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                        <i class="fa-solid fa-code"></i>
                    </div>
                    <h3 class="text-xl font-bold text-slate-900 dark:text-white mb-3">Developer Friendly API</h3>
                    <p class="text-slate-500 dark:text-slate-400 leading-relaxed">Integrate comprehensive healthcare data into your app with just a few lines of code.</p>
                </div>
            </div>
        </div>
    </section>

    <!-- How It Works Section -->
    <section id="how-it-works" class="py-24 px-6 bg-white dark:bg-dark-900 transition-colors duration-300">
        <div class="container mx-auto">
            <div class="flex flex-col lg:flex-row gap-16 items-center">
                <div class="lg:w-1/2 reveal">
                    <img src="https://img.freepik.com/free-vector/data-extraction-concept-illustration_114360-4876.jpg" alt="How it works" class="w-full rounded-2xl mix-blend-multiply dark:mix-blend-normal dark:opacity-80">
                </div>
                <div class="lg:w-1/2 space-y-10 reveal">
                    <h2 class="text-3xl lg:text-4xl font-bold text-slate-900 dark:text-white">Seamless Integration Workflow</h2>
                    
                    <div class="flex gap-4">
                        <div class="flex flex-col items-center">
                            <div class="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center font-bold text-sm">1</div>
                            <div class="w-0.5 h-full bg-slate-100 dark:bg-slate-800 my-2"></div>
                        </div>
                        <div>
                            <h4 class="text-lg font-bold text-slate-900 dark:text-white">Input Data</h4>
                            <p class="text-slate-500 dark:text-slate-400 mt-1">Enter an NPI number, name, or upload a CSV file of providers.</p>
                        </div>
                    </div>

                    <div class="flex gap-4">
                        <div class="flex flex-col items-center">
                            <div class="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center font-bold text-sm">2</div>
                            <div class="w-0.5 h-full bg-slate-100 dark:bg-slate-800 my-2"></div>
                        </div>
                        <div>
                            <h4 class="text-lg font-bold text-slate-900 dark:text-white">AI Processing</h4>
                            <p class="text-slate-500 dark:text-slate-400 mt-1">Our system cross-references 50+ databases and runs compliance checks.</p>
                        </div>
                    </div>

                    <div class="flex gap-4">
                        <div class="flex flex-col items-center">
                            <div class="w-8 h-8 rounded-full bg-brand-600 text-white flex items-center justify-center font-bold text-sm">3</div>
                        </div>
                        <div>
                            <h4 class="text-lg font-bold text-slate-900 dark:text-white">Get Results</h4>
                            <p class="text-slate-500 dark:text-slate-400 mt-1">Receive a detailed JSON report or view the verified profile instantly.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- FAQ Section -->
    <section id="faq" class="py-24 px-6 bg-slate-50 dark:bg-dark-950 transition-colors duration-300">
        <div class="container mx-auto max-w-3xl">
            <h2 class="text-3xl font-bold text-slate-900 dark:text-white text-center mb-12 reveal">Frequently Asked Questions</h2>
            
            <div class="space-y-4">
                <!-- FAQ Item 1 -->
                <div class="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden reveal">
                    <button class="w-full px-6 py-4 text-left flex justify-between items-center font-semibold text-slate-900 dark:text-white focus:outline-none" onclick="toggleAccordion(1)">
                        <span>Is the data updated in real-time?</span>
                        <i id="icon-1" class="fa-solid fa-chevron-down text-slate-400 transition-transform"></i>
                    </button>
                    <div id="content-1" class="hidden px-6 pb-4 text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                        Yes, our system queries the NPPES registry and state licensing boards in real-time to ensure you always have the latest information.
                    </div>
                </div>

                <!-- FAQ Item 2 -->
                <div class="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden reveal delay-100">
                    <button class="w-full px-6 py-4 text-left flex justify-between items-center font-semibold text-slate-900 dark:text-white focus:outline-none" onclick="toggleAccordion(2)">
                        <span>Do you offer an API for developers?</span>
                        <i id="icon-2" class="fa-solid fa-chevron-down text-slate-400 transition-transform"></i>
                    </button>
                    <div id="content-2" class="hidden px-6 pb-4 text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                        Absolutely. We have a RESTful API with extensive documentation, enabling you to integrate NPI validation directly into your existing software.
                    </div>
                </div>

                <!-- FAQ Item 3 -->
                <div class="bg-white dark:bg-dark-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden reveal delay-200">
                    <button class="w-full px-6 py-4 text-left flex justify-between items-center font-semibold text-slate-900 dark:text-white focus:outline-none" onclick="toggleAccordion(3)">
                        <span>Is this service HIPAA compliant?</span>
                        <i id="icon-3" class="fa-solid fa-chevron-down text-slate-400 transition-transform"></i>
                    </button>
                    <div id="content-3" class="hidden px-6 pb-4 text-slate-600 dark:text-slate-400 text-sm leading-relaxed">
                        Yes, MediverifyAI adheres to strict security standards including HIPAA compliance to ensure all data handling is secure and private.
                    </div>
                </div>
            </div>
        </div>
    </section>

""" + FOOTER_TEMPLATE + """

    <!-- Scripts -->
    <script>
        // Home-specific scripts (scroll animations, counters, search, FAQ)
        // --- Scroll Animation Observer ---
        const observerOptions = { threshold: 0.1, rootMargin: "0px 0px -50px 0px" };
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('active');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.reveal').forEach(el => observer.observe(el));

        // --- Animated Counters ---
        function animateCounter(el) {
            const target = +el.getAttribute('data-target');
            const duration = 2000;
            const step = target / (duration / 16); 
            let current = 0;
            
            const timer = setInterval(() => {
                current += step;
                if (current >= target) {
                    el.innerText = target + (target > 50 ? '+' : '');
                    clearInterval(timer);
                } else {
                    el.innerText = Math.floor(current);
                }
            }, 16);
        }

        const statsObserver = new IntersectionObserver((entries) => {
            if (entries[0].isIntersecting) {
                document.querySelectorAll('.counter').forEach(animateCounter);
                statsObserver.disconnect();
            }
        });
        statsObserver.observe(document.querySelector('.counter'));

        // --- Search Logic ---
        const mockResults = [
            { name: "Dr. Sarah Jenkins", npi: "1452369874", type: "Cardiology", status: "Active" },
            { name: "Dr. Michael Chen", npi: "1985423654", type: "Dermatology", status: "Active" },
            { name: "City General Hospital", npi: "1597534568", type: "Organization", status: "Verified" },
            { name: "James Wilson, MD", npi: "1236547896", type: "Internal Med", status: "Active" },
        ];

        function handleSearch(val) {
            const container = document.getElementById('searchResults');
            const content = document.getElementById('resultsContent');
            
            if (val.length < 2) {
                container.classList.add('hidden');
                return;
            }

            container.classList.remove('hidden');
            const filtered = mockResults.filter(r => r.name.toLowerCase().includes(val.toLowerCase()));
            
            if (filtered.length === 0) {
                content.innerHTML = `<div class="p-4 text-center text-slate-500 dark:text-slate-400 text-sm">No records found.</div>`;
            } else {
                content.innerHTML = filtered.map(item => `
                    <div class="p-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer border-b border-slate-50 dark:border-slate-700 transition-colors flex justify-between items-center group">
                        <div class="flex items-center gap-3">
                            <div class="w-8 h-8 rounded-full bg-brand-100 dark:bg-brand-900/30 text-brand-600 dark:text-brand-400 flex items-center justify-center font-bold text-xs">
                                ${item.name.charAt(0)}
                            </div>
                            <div>
                                <div class="font-semibold text-slate-800 dark:text-slate-200 text-sm group-hover:text-brand-600 dark:group-hover:text-brand-400 transition-colors">${item.name}</div>
                                <div class="text-[10px] text-slate-500 dark:text-slate-400 uppercase">${item.type} • NPI: ${item.npi}</div>
                            </div>
                        </div>
                        <span class="text-[10px] bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 px-2 py-0.5 rounded-full font-bold">${item.status}</span>
                    </div>
                `).join('');
            }
        }

        // --- FAQ Accordion ---
        function toggleAccordion(id) {
            const content = document.getElementById(`content-${id}`);
            const icon = document.getElementById(`icon-${id}`);
            if (content.classList.contains('hidden')) {
                content.classList.remove('hidden');
                icon.classList.add('rotate-180');
            } else {
                content.classList.add('hidden');
                icon.classList.remove('rotate-180');
            }
        }
    </script>
""" + SHARED_SCRIPTS + """
</body>
</html>
"""

# ==========================================
# Validator Page Template (Updated with Shared Header/Footer)
# ==========================================

VALIDATOR_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" class="scroll-smooth">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Validator - MediverifyAI</title>
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Google Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

    <!-- Tailwind Config -->
    <script>
        tailwind.config = {
            darkMode: 'class',
            theme: {
                extend: {
                    fontFamily: {
                        sans: ['"Plus Jakarta Sans"', 'sans-serif'],
                    },
                    colors: {
                        brand: {
                            50: '#f0f9ff',
                            100: '#e0f2fe',
                            500: '#0ea5e9',
                            600: '#0284c7',
                            700: '#0369a1',
                            800: '#075985',
                            900: '#0c4a6e',
                        },
                        dark: {
                            950: '#020617',
                            900: '#0f172a',
                            800: '#1e293b',
                            700: '#334155',
                        }
                    }
                }
            }
        }
    </script>

    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .glass {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(226, 232, 240, 0.6);
        }
        .dark .glass {
            background: rgba(15, 23, 42, 0.85);
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        }
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
        .dark ::-webkit-scrollbar-thumb { background: #475569; }
        ::-webkit-scrollbar-thumb:hover { background: #94a3b8; }
    </style>
</head>
<body class="bg-slate-50 text-slate-800 dark:bg-dark-950 dark:text-slate-200 antialiased overflow-x-hidden relative transition-colors duration-300 min-h-screen">

    <!-- Toast Notification Container -->
    <div id="toast-container" class="fixed bottom-5 right-5 z-[100] flex flex-col gap-3"></div>

""" + NAV_TEMPLATE + LOGIN_MODAL_TEMPLATE + """

    <!-- Main Content -->
    <main class="pt-24 pb-12 px-6">
        <div class="container mx-auto max-w-6xl">
            <!-- Header -->
            <div class="text-center mb-12">
                <h1 class="text-4xl lg:text-5xl font-bold text-slate-900 dark:text-white mb-4">Bulk NPI Validator</h1>
                <p class="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">Upload your CSV file with NPI numbers to validate multiple providers at once. Get instant compliance reports.</p>
            </div>

            {% if results %}
            <!-- Results Section -->
            <div class="bg-white dark:bg-dark-800 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-700 p-8 mb-8">
                <div class="flex justify-between items-center mb-6">
                    <h2 class="text-2xl font-bold text-slate-900 dark:text-white">Validation Results</h2>
                    <a href="/download_report?session_id={{ session_id }}" class="bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-brand-700 transition-colors flex items-center gap-2">
                        <i class="fa-solid fa-download"></i> Download Report (CSV)
                    </a>
                </div>
                <div class="overflow-x-auto">
                    <table class="w-full text-sm text-left text-slate-500 dark:text-slate-400">
                        <thead class="text-xs uppercase bg-slate-50 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                            <tr>
                                <th class="px-6 py-3">NPI</th>
                                <th class="px-6 py-3">Provider Name</th>
                                <th class="px-6 py-3">Status</th>
                                <th class="px-6 py-3">Taxonomy</th>
                                <th class="px-6 py-3">City, State</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for row in results %}
                            <tr class="bg-white dark:bg-dark-800 border-b border-slate-100 dark:border-slate-700 {% if row.valid %}hover:bg-green-50 dark:hover:bg-green-900/20{% else %}hover:bg-red-50 dark:hover:bg-red-900/20{% endif %}">
                                <td class="px-6 py-4 font-mono font-semibold">{{ row.npi }}</td>
                                <td class="px-6 py-4">{{ row.name }}</td>
                                <td class="px-6 py-4">
                                    <span class="px-2 py-1 rounded-full text-xs font-bold {% if row.valid %}bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400{% else %}bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400{% endif %}">
                                        {{ 'Valid' if row.valid else 'Invalid' }}
                                    </span>
                                </td>
                                <td class="px-6 py-4">{{ row.taxonomy or 'N/A' }}</td>
                                <td class="px-6 py-4">{{ row.location or 'N/A' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                <div class="mt-4 text-center text-sm text-slate-500 dark:text-slate-400">
                    Processed {{ results|length }} records. {{ valid_count }} valid, {{ invalid_count }} invalid.
                </div>
            </div>
            {% endif %}

            <!-- Upload Form -->
            <div class="bg-white dark:bg-dark-800 rounded-2xl shadow-xl border border-slate-100 dark:border-slate-700 p-8 max-w-2xl mx-auto">
                <form method="POST" enctype="multipart/form-data" id="uploadForm">
                    <div class="space-y-6">
                        <div>
                            <label class="block text-sm font-bold text-slate-700 dark:text-slate-300 mb-2">Upload CSV File</label>
                            <input type="file" name="csv_file" accept=".csv" required class="w-full px-4 py-3 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg focus:ring-2 focus:ring-brand-500 outline-none transition-all">
                            <p class="text-xs text-slate-500 dark:text-slate-400 mt-1">CSV should have a 'NPI' column with 10-digit numbers.</p>
                        </div>
                        <button type="submit" class="w-full bg-brand-600 text-white py-3 rounded-lg font-semibold hover:bg-brand-700 transition-colors shadow-lg">
                            <i class="fa-solid fa-upload mr-2"></i> Validate Batch
                        </button>
                    </div>
                </form>
            </div>
        </div>
    </main>

""" + FOOTER_TEMPLATE + """

    <script>
        // Validator-specific scripts
        // Form submission with loading
        document.getElementById('uploadForm').addEventListener('submit', function() {
            const btn = this.querySelector('button[type="submit"]');
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i> Processing...';
            btn.disabled = true;
        });
    </script>
""" + SHARED_SCRIPTS + """
</body>
</html>
"""

# ==========================================
# Routes
# ==========================================

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/validate', methods=['POST'])
def validate_npi():
    try:
        req_data = request.get_json()
        npi = req_data.get('npi', '').strip()
        
        if not npi:
            return jsonify({'error': 'NPI is required'}), 400
        
        result = validate_npi_real(npi)
        
        if result['valid']:
            return jsonify({
                'status': 'success',
                'valid': True,
                'provider': result['provider']
            })
        else:
            return jsonify({
                'status': 'error',
                'valid': False,
                'message': result.get('error', 'Validation failed')
            }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500

@app.route('/validator', methods=['GET', 'POST'])
def validator():
    if request.method == 'POST':
        if 'csv_file' not in request.files:
            return render_template_string(VALIDATOR_TEMPLATE, error='No file uploaded'), 400
        
        file = request.files['csv_file']
        if file.filename == '':
            return render_template_string(VALIDATOR_TEMPLATE, error='No file selected'), 400
        
        if file and file.filename.endswith('.csv'):
            # Read CSV
            stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
            csv_reader = csv.DictReader(stream)
            
            results = []
            valid_count = 0
            invalid_count = 0
            
            for row in csv_reader:
                npi = row.get('NPI', '').strip()
                if npi:
                    result = validate_npi_real(npi)
                    name = ''
                    taxonomy = ''
                    location = ''
                    valid = result['valid']
                    
                    if valid:
                        provider = result['provider']
                        basic = provider.get('basic', {})
                        name = f"{basic.get('first_name', '')} {basic.get('last_name', basic.get('organization_name', 'N/A'))}".strip() or 'N/A'
                        taxonomies = provider.get('taxonomies', [])
                        if taxonomies:
                            taxonomy = taxonomies[0].get('desc', '') if taxonomies[0].get('primary', False) else taxonomies[0].get('desc', '')
                        addresses = provider.get('addresses', [])
                        if addresses:
                            addr = addresses[0]
                            location = f"{addr.get('city', '')}, {addr.get('state', '')}"
                        valid_count += 1
                    else:
                        name = row.get('Name', 'N/A') if 'Name' in row else 'N/A'
                        invalid_count += 1
                    
                    results.append({
                        'npi': npi,
                        'name': name,
                        'valid': valid,
                        'taxonomy': taxonomy,
                        'location': location
                    })
            
            # Store in session
            session_id = str(random.randint(100000, 999999))
            session['results'] = results
            session['session_id'] = session_id
            session['valid_count'] = valid_count
            session['invalid_count'] = invalid_count
            
            return render_template_string(VALIDATOR_TEMPLATE, results=results, session_id=session_id, valid_count=valid_count, invalid_count=invalid_count)
    
    return render_template_string(VALIDATOR_TEMPLATE)

@app.route('/download_report')
def download_report():
    session_id = request.args.get('session_id')
    if not session_id or session_id != session.get('session_id'):
        return 'Invalid session', 400
    
    results = session.get('results', [])
    if not results:
        return 'No results to download', 400
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(['NPI', 'Provider Name', 'Status', 'Taxonomy', 'City, State'])
    
    # Data
    for row in results:
        writer.writerow([row['npi'], row['name'], 'Valid' if row['valid'] else 'Invalid', row['taxonomy'], row['location']])
    
    filename = f"validation_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=filename
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000)