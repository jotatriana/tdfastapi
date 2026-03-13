from dotenv import load_dotenv
import os
import requests
from flask import Flask, jsonify, render_template_string, request

# Import shared client classes
from talkdesk_client import TalkdeskGenericClient, PromptsManager, CLIENT_ID, CLIENT_SECRET, extract_hal_link

load_dotenv()

app = Flask(__name__)

# --- CONFIGURATION ---
OPENAPI_FILE = 'openapi.yaml'

# Initialize API client and managers
api_client = TalkdeskGenericClient(OPENAPI_FILE)
prompts_manager = PromptsManager(api_client)

# --- ROUTES ---

@app.route('/prompts-admin')
def prompts_admin():
    """Main Prompts Administration Interface"""
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Talkdesk Prompts Administration</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            /* Design System Tokens */
            :root {
                --color-primary: #2563eb;
                --color-primary-light: #3b82f6;
                --color-primary-dark: #1e40af;
                --color-primary-alpha-10: rgba(37, 99, 235, 0.1);
                --color-primary-alpha-20: rgba(37, 99, 235, 0.2);
                --color-secondary: #7c3aed;
                --color-secondary-light: #8b5cf6;
                --color-success: #22c55e;
                --color-success-light: #4ade80;
                --color-warning: #f59e0b;
                --color-error: #ef4444;
                --color-error-light: #f87171;
                --color-grey-50: #fafafa;
                --color-grey-100: #f5f5f5;
                --color-grey-200: #e5e5e5;
                --color-grey-300: #d4d4d4;
                --color-grey-400: #a3a3a3;
                --color-grey-500: #737373;
                --color-grey-600: #525252;
                --color-grey-700: #404040;
                --color-grey-800: #262626;
                --color-grey-900: #171717;
                --color-background: #ffffff;
                --color-surface: #fafafa;
                --color-surface-elevated: #ffffff;
                --color-border: #e5e5e5;
                --color-border-hover: #d4d4d4;
                --color-text-primary: #0a0a0a;
                --color-text-secondary: #525252;
                --color-text-tertiary: #737373;

                /* Radial Gradient Extension - Ocean Theme Colors */
                --gradient-color-1: #800000;  /* Maroon */
                --gradient-color-2: #804000;  /* Brown */
                --gradient-color-3: #004040;  /* Dark Teal */
                --gradient-color-4: #006666;  /* Ocean Blue */
                --gradient-color-5: #004040;  /* Deep Sea */
                --gradient-color-6: #006666;  /* Ocean Teal */
                --gradient-color-7: #008080;  /* Turquoise */
                --gradient-color-8: #003333;  /* Ocean Deep */
                --gradient-color-9: #00B4B4;  /* Bright Turquoise */
                --gradient-color-10: #20B2AA; /* Sea Green */
                --gradient-base-black: #001a1a;

                /* Radial Gradient Patterns - Ocean Theme */
                --gradient-teal: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-5) 0%, var(--gradient-base-black) 100%);
                --gradient-ocean: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-6) 0%, var(--gradient-base-black) 100%);
                --gradient-turquoise: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-7) 0%, var(--gradient-base-black) 100%);
                --gradient-radial-multi: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-5) 0%, var(--gradient-color-7) 50%, var(--gradient-base-black) 100%);
                --gradient-radial-glow: radial-gradient(circle at center, var(--gradient-color-7) 0%, rgba(0, 128, 128, 0.3) 30%, transparent 60%);
                --gradient-radial-overlay: radial-gradient(100% 100% at 50% 0%, rgba(0, 102, 102, 0.8) 0%, rgba(0, 26, 26, 0.9) 100%);
                --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                --font-size-xs: 0.75rem;
                --font-size-sm: 0.875rem;
                --font-size-base: 1rem;
                --font-size-lg: 1.125rem;
                --font-size-xl: 1.25rem;
                --font-size-2xl: 1.5rem;
                --font-size-3xl: 1.875rem;
                --font-weight-normal: 400;
                --font-weight-medium: 500;
                --font-weight-semibold: 600;
                --font-weight-bold: 700;
                --line-height-tight: 1.25;
                --line-height-normal: 1.5;
                --spacing-1: 0.25rem;
                --spacing-2: 0.5rem;
                --spacing-3: 0.75rem;
                --spacing-4: 1rem;
                --spacing-5: 1.25rem;
                --spacing-6: 1.5rem;
                --spacing-8: 2rem;
                --spacing-10: 2.5rem;
                --spacing-12: 3rem;
                --radius-md: 0.375rem;
                --radius-lg: 0.5rem;
                --radius-xl: 0.75rem;
                --radius-2xl: 1rem;
                --radius-full: 9999px;
                --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
                --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
                --duration-fast: 150ms;
                --duration-base: 250ms;
                --ease-out: cubic-bezier(0, 0, 0.2, 1);
                --z-index-modal-backdrop: 1040;
                --z-index-modal: 1050;
            }

            /* Dark Mode */
            @media (prefers-color-scheme: dark) {
                :root {
                    --color-background: #0a0a0a;
                    --color-surface: #171717;
                    --color-surface-elevated: #262626;
                    --color-border: #404040;
                    --color-border-hover: #525252;
                    --color-text-primary: #fafafa;
                    --color-text-secondary: #a3a3a3;
                    --color-text-tertiary: #737373;
                }
            }

            /* Base Styles */
            *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: var(--font-family-primary);
                background: var(--gradient-radial-multi);
                background-attachment: fixed;
                min-height: 100vh;
                color: #ffffff;
                line-height: var(--line-height-normal);
                position: relative;
                overflow-x: hidden;
            }

            /* Floating Orbs - Using Radial Gradient Extension */
            .floating-orb {
                position: fixed;
                border-radius: 50%;
                background: var(--gradient-radial-glow);
                filter: blur(60px);
                opacity: 0.6;
                pointer-events: none;
                z-index: 0;
            }
            body::before,
            body::after {
                content: '';
                position: fixed;
                border-radius: 50%;
                filter: blur(80px);
                opacity: 0.5;
                pointer-events: none;
                z-index: 0;
            }
            body::before {
                width: 600px;
                height: 600px;
                background: radial-gradient(circle, var(--gradient-color-6) 0%, transparent 70%);
                top: -200px;
                right: -100px;
                animation: floatOrb 20s ease-in-out infinite;
            }
            body::after {
                width: 500px;
                height: 500px;
                background: radial-gradient(circle, var(--gradient-color-7) 0%, transparent 70%);
                bottom: -150px;
                left: -100px;
                animation: floatOrb 25s ease-in-out infinite reverse;
            }
            @keyframes floatOrb {
                0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.5; }
                33% { transform: translate(20px, -30px) scale(1.2); opacity: 0.7; }
                66% { transform: translate(-20px, 20px) scale(0.9); opacity: 0.4; }
            }

            /* Header */
            .header {
                background: linear-gradient(135deg, rgba(0, 64, 64, 0.95) 0%, rgba(0, 128, 128, 0.95) 100%);
                backdrop-filter: blur(20px);
                color: white;
                padding: var(--spacing-6) var(--spacing-8);
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid rgba(0, 180, 180, 0.3);
                position: relative;
                z-index: 10;
            }
            .header-content {
                max-width: 1400px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .header h1 {
                font-size: var(--font-size-2xl);
                font-weight: var(--font-weight-bold);
                margin-bottom: var(--spacing-1);
                display: flex;
                align-items: center;
                gap: var(--spacing-3);
            }
            .header p {
                opacity: 0.9;
                font-size: var(--font-size-sm);
            }
            .header-link {
                color: white;
                text-decoration: none;
                font-size: var(--font-size-sm);
                font-weight: var(--font-weight-medium);
                padding: var(--spacing-2) var(--spacing-4);
                background: rgba(255,255,255,0.15);
                border-radius: var(--radius-lg);
                transition: background var(--duration-fast) var(--ease-out);
            }
            .header-link:hover {
                background: rgba(255,255,255,0.25);
            }

            /* Container */
            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: var(--spacing-8);
                position: relative;
                z-index: 1;
            }

            /* Toolbar */
            .toolbar {
                background: linear-gradient(135deg, rgba(0, 64, 64, 0.3) 0%, rgba(0, 128, 128, 0.2) 100%);
                backdrop-filter: blur(20px);
                padding: var(--spacing-5);
                border-radius: var(--radius-xl);
                margin-bottom: var(--spacing-6);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.15);
            }
            .toolbar-row {
                display: flex;
                gap: var(--spacing-4);
                margin-bottom: var(--spacing-4);
                align-items: center;
                flex-wrap: wrap;
            }
            .toolbar-row:last-child { margin-bottom: 0; }
            .search-box { flex: 1; min-width: 300px; }
            .search-box input {
                width: 100%;
                padding: var(--spacing-3) var(--spacing-4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: var(--radius-lg);
                font-size: var(--font-size-sm);
                font-family: var(--font-family-primary);
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                transition: all var(--duration-fast) var(--ease-out);
            }
            .search-box input:focus {
                outline: none;
                border-color: rgba(0, 180, 180, 0.6);
                box-shadow: 0 0 0 3px rgba(0, 180, 180, 0.2);
                background: rgba(255, 255, 255, 0.15);
            }
            .search-box input::placeholder { color: rgba(255, 255, 255, 0.5); }

            /* Buttons - Using Radial Gradient Pattern from Design System */
            .btn {
                display: inline-flex;
                align-items: center;
                justify-content: center;
                gap: var(--spacing-2);
                padding: var(--spacing-3) var(--spacing-5);
                border: none;
                border-radius: var(--radius-lg);
                cursor: pointer;
                font-size: var(--font-size-sm);
                font-weight: var(--font-weight-medium);
                font-family: var(--font-family-primary);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                white-space: nowrap;
                position: relative;
                overflow: hidden;
            }
            .btn:disabled { opacity: 0.5; cursor: not-allowed; }

            /* Primary Button with Radial Gradient */
            .btn-primary {
                background: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-6) 0%, var(--gradient-color-5) 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(0, 64, 64, 0.4);
            }
            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 102, 102, 0.5);
            }

            /* Success Button with Radial Gradient */
            .btn-success {
                background: radial-gradient(100% 100% at 50% 0%, #4ade80 0%, var(--gradient-color-3) 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(0, 64, 0, 0.4);
            }
            .btn-success:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 64, 0, 0.5);
            }

            /* Danger Button with Radial Gradient */
            .btn-danger {
                background: radial-gradient(100% 100% at 50% 0%, #f87171 0%, var(--gradient-color-1) 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(128, 0, 0, 0.4);
            }
            .btn-danger:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(128, 0, 0, 0.5);
            }

            /* Secondary Button with Radial Gradient */
            .btn-secondary {
                background: radial-gradient(100% 100% at 50% 0%, rgba(0, 128, 128, 0.8) 0%, var(--gradient-color-8) 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(0, 51, 51, 0.4);
            }
            .btn-secondary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 128, 128, 0.5);
            }

            /* Outline Button */
            .btn-outline {
                background: rgba(0, 51, 51, 0.3);
                border: 1px solid rgba(0, 128, 128, 0.4);
                color: #ffffff;
                backdrop-filter: blur(4px);
            }
            .btn-outline:hover:not(:disabled) {
                background: rgba(0, 128, 128, 0.2);
                border-color: rgba(0, 128, 128, 0.6);
                transform: translateY(-2px);
            }
            .btn-sm {
                padding: var(--spacing-2) var(--spacing-3);
                font-size: var(--font-size-xs);
            }

            /* Stats */
            .stats {
                display: flex;
                gap: var(--spacing-2);
                align-items: center;
                color: rgba(255, 255, 255, 0.7);
                font-size: var(--font-size-sm);
            }
            .stats strong { color: #ffffff; }

            /* Prompts Grid */
            .prompts-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
                gap: var(--spacing-5);
            }

            /* Card with Radial Gradient Hover Effect - From Design System */
            .prompt-card {
                position: relative;
                overflow: hidden;
                background: rgba(0, 51, 51, 0.4);
                backdrop-filter: blur(20px);
                border-radius: var(--radius-xl);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(0, 128, 128, 0.3);
                transition: all 0.3s ease;
            }
            .prompt-card::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: radial-gradient(circle, var(--gradient-color-7), transparent);
                opacity: 0;
                transform: translate(-50%, -50%);
                transition: all 0.6s ease;
                z-index: 0;
            }
            .prompt-card:hover::before {
                width: 300%;
                height: 300%;
                opacity: 0.2;
            }
            .prompt-card:hover {
                transform: translateY(-6px);
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4), 0 0 40px rgba(0, 128, 128, 0.2);
                border-color: rgba(0, 128, 128, 0.5);
            }
            .prompt-card.selected {
                border: 2px solid var(--gradient-color-7);
                box-shadow: 0 0 30px rgba(0, 128, 128, 0.4);
            }
            .prompt-card.hidden { display: none; }

            .prompt-header {
                padding: var(--spacing-4);
                background: radial-gradient(100% 200% at 50% 0%, rgba(0, 102, 102, 0.3) 0%, transparent 100%);
                border-bottom: 1px solid rgba(0, 128, 128, 0.2);
                position: relative;
                z-index: 1;
            }
            .prompt-title {
                font-weight: var(--font-weight-semibold);
                font-size: var(--font-size-base);
                color: #ffffff;
                margin-bottom: var(--spacing-1);
            }
            .prompt-description {
                font-size: var(--font-size-sm);
                color: rgba(255, 255, 255, 0.7);
                line-height: var(--line-height-normal);
            }

            .prompt-body { padding: var(--spacing-4); position: relative; z-index: 1; }
            .prompt-meta {
                display: flex;
                gap: var(--spacing-3);
                font-size: var(--font-size-xs);
                color: rgba(255, 255, 255, 0.6);
                margin-bottom: var(--spacing-3);
                flex-wrap: wrap;
            }
            .meta-item {
                display: flex;
                align-items: center;
                gap: var(--spacing-1);
            }

            .prompt-audio { margin: var(--spacing-3) 0; }
            .audio-wrapper {
                position: relative;
                width: 100%;
            }
            .audio-player {
                width: 100%;
                height: 36px;
                border-radius: var(--radius-lg);
                display: none;
            }
            .audio-player.loaded {
                display: block;
            }
            .play-btn {
                width: 100%;
                height: 36px;
                border-radius: var(--radius-lg);
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                color: var(--color-text-primary);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
                font-size: 14px;
                transition: all 0.2s ease;
            }
            .play-btn:hover {
                background: rgba(255, 255, 255, 0.15);
                border-color: rgba(255, 255, 255, 0.3);
            }
            .play-btn.loading {
                pointer-events: none;
                opacity: 0.7;
            }
            .play-btn.hidden {
                display: none;
            }

            .prompt-actions {
                display: flex;
                gap: var(--spacing-2);
                padding-top: var(--spacing-3);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }

            .checkbox {
                position: absolute;
                top: var(--spacing-4);
                right: var(--spacing-4);
                width: 20px;
                height: 20px;
                cursor: pointer;
                accent-color: var(--color-primary);
                z-index: 2;
            }

            /* Modal - Using Radial Gradient Overlay from Design System */
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: var(--gradient-radial-overlay);
                backdrop-filter: blur(8px);
                z-index: var(--z-index-modal-backdrop);
            }
            .modal.active {
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .modal-content {
                background: radial-gradient(100% 100% at 50% 0%, rgba(0, 64, 64, 0.6) 0%, rgba(0, 0, 0, 0.9) 100%);
                backdrop-filter: blur(30px);
                border-radius: var(--radius-2xl);
                max-width: 560px;
                width: 90%;
                max-height: 85vh;
                overflow-y: auto;
                box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6), 0 0 60px rgba(0, 128, 128, 0.2);
                border: 1px solid rgba(0, 128, 128, 0.4);
                animation: slideUp 0.3s var(--ease-out);
                position: relative;
            }
            .modal-content::before {
                content: '';
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 4px;
                background: linear-gradient(90deg, var(--gradient-color-5), var(--gradient-color-7));
                border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
            }
            @keyframes slideUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .modal-header {
                padding: var(--spacing-5) var(--spacing-6);
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .modal-header h2 {
                font-size: var(--font-size-xl);
                font-weight: var(--font-weight-semibold);
                color: #ffffff;
            }
            .modal-body { padding: var(--spacing-6); }
            .modal-footer {
                padding: var(--spacing-4) var(--spacing-6);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: flex;
                gap: var(--spacing-3);
                justify-content: flex-end;
            }
            .close-btn {
                background: none;
                border: none;
                font-size: var(--font-size-2xl);
                cursor: pointer;
                color: rgba(255, 255, 255, 0.6);
                line-height: 1;
                padding: var(--spacing-1);
                border-radius: var(--radius-md);
                transition: all var(--duration-fast) var(--ease-out);
            }
            .close-btn:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 0.1);
            }

            /* Form */
            .form-group { margin-bottom: var(--spacing-5); }
            .form-group label {
                display: block;
                margin-bottom: var(--spacing-2);
                font-weight: var(--font-weight-medium);
                font-size: var(--font-size-sm);
                color: rgba(255, 255, 255, 0.9);
            }
            .form-group input,
            .form-group textarea {
                width: 100%;
                padding: var(--spacing-3) var(--spacing-4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: var(--radius-lg);
                font-size: var(--font-size-sm);
                font-family: var(--font-family-primary);
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                transition: all var(--duration-fast) var(--ease-out);
            }
            .form-group input:focus,
            .form-group textarea:focus {
                outline: none;
                border-color: rgba(0, 180, 180, 0.6);
                box-shadow: 0 0 0 3px rgba(0, 180, 180, 0.2);
                background: rgba(255, 255, 255, 0.15);
            }
            .form-group input::placeholder,
            .form-group textarea::placeholder {
                color: rgba(255, 255, 255, 0.4);
            }
            .form-group textarea { min-height: 100px; resize: vertical; }

            /* Upload Area */
            .upload-area {
                border: 2px dashed rgba(255, 255, 255, 0.3);
                border-radius: var(--radius-xl);
                padding: var(--spacing-10);
                text-align: center;
                cursor: pointer;
                transition: all var(--duration-base) var(--ease-out);
                background: rgba(255, 255, 255, 0.05);
            }
            .upload-area:hover {
                border-color: rgba(0, 180, 180, 0.6);
                background: rgba(0, 180, 180, 0.1);
            }
            .upload-area.drag-over {
                border-color: rgba(0, 180, 180, 0.8);
                background: rgba(0, 180, 180, 0.2);
            }
            .upload-icon {
                font-size: 3rem;
                margin-bottom: var(--spacing-3);
                opacity: 0.6;
            }
            .upload-text {
                color: rgba(255, 255, 255, 0.7);
                font-size: var(--font-size-sm);
            }
            .upload-text strong { color: #3b82f6; }

            /* Progress */
            .progress-bar {
                width: 100%;
                height: 6px;
                background: var(--color-border);
                border-radius: var(--radius-full);
                overflow: hidden;
                margin-top: var(--spacing-3);
            }
            .progress-fill {
                height: 100%;
                background: linear-gradient(90deg, var(--color-primary), var(--color-secondary));
                transition: width var(--duration-base) var(--ease-out);
            }

            /* Empty State */
            .empty-state {
                text-align: center;
                padding: var(--spacing-12) var(--spacing-6);
                color: rgba(255, 255, 255, 0.7);
            }
            .empty-state-icon {
                font-size: 4rem;
                margin-bottom: var(--spacing-4);
                opacity: 0.4;
            }
            .empty-state h3 {
                font-size: var(--font-size-xl);
                font-weight: var(--font-weight-semibold);
                margin-bottom: var(--spacing-2);
                color: #ffffff;
            }

            /* Loading */
            .loading {
                text-align: center;
                padding: var(--spacing-10);
                color: rgba(255, 255, 255, 0.8);
            }
            .spinner {
                border: 3px solid rgba(255, 255, 255, 0.2);
                border-top-color: #3b82f6;
                border-radius: var(--radius-full);
                width: 40px;
                height: 40px;
                animation: spin 0.8s linear infinite;
                margin: 0 auto var(--spacing-4);
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            /* Focus States */
            *:focus-visible {
                outline: 2px solid var(--color-primary);
                outline-offset: 2px;
            }
            *:focus:not(:focus-visible) { outline: none; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div>
                    <h1>Prompts Administration</h1>
                    <p>Manage your Contact Center audio prompts</p>
                </div>
                <a href="/" class="header-link">API Explorer</a>
            </div>
        </div>

        <div class="container">
            <!-- Toolbar -->
            <div class="toolbar">
                <div class="toolbar-row">
                    <div class="search-box">
                        <input type="text" id="search-input" placeholder="Search prompts by name or description...">
                    </div>
                    <button class="btn btn-primary" onclick="showUploadModal()">
                        📤 Upload Prompt
                    </button>
                    <button class="btn btn-secondary" onclick="showBulkUploadModal()">
                        📦 Bulk Upload
                    </button>
                    <button class="btn btn-secondary" onclick="refreshPrompts()">
                        🔄 Refresh
                    </button>
                </div>
                <div class="toolbar-row">
                    <div class="stats">
                        Showing <strong><span id="visible-count">0</span></strong> of <strong><span id="total-count">0</span></strong> prompts
                    </div>
                    <div id="bulk-actions" style="display: none; flex: 1; display: flex; gap: 10px; justify-content: flex-end;">
                        <span class="stats"><strong><span id="selected-count">0</span></strong> selected</span>
                        <button class="btn btn-sm btn-danger" onclick="bulkDelete()">Delete Selected</button>
                        <button class="btn btn-sm btn-secondary" onclick="clearSelection()">Clear Selection</button>
                    </div>
                </div>
            </div>

            <!-- Prompts Grid -->
            <div id="prompts-container">
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Loading prompts...</p>
                </div>
            </div>
        </div>

        <!-- Upload Modal -->
        <div id="upload-modal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Upload Audio Prompt</h2>
                    <button class="close-btn" onclick="closeUploadModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="upload-form" enctype="multipart/form-data">
                        <div class="form-group">
                            <label>Prompt Name *</label>
                            <input type="text" id="prompt-name" required>
                        </div>
                        <div class="form-group">
                            <label>Description</label>
                            <textarea id="prompt-description"></textarea>
                        </div>
                        <div class="form-group">
                            <label>Audio File (MP3 or WAV, max 10MB) *</label>
                            <div class="upload-area" id="upload-area">
                                <div class="upload-icon">📁</div>
                                <div class="upload-text">
                                    <strong>Click to browse</strong> or drag and drop your audio file here
                                </div>
                                <input type="file" id="file-input" accept=".mp3,.wav" style="display: none;">
                            </div>
                            <div id="file-info" style="margin-top: 10px; color: #4a5568;"></div>
                            <div id="upload-progress" style="display: none;">
                                <div class="progress-bar">
                                    <div class="progress-fill" id="progress-fill" style="width: 0%"></div>
                                </div>
                                <p style="text-align: center; margin-top: 8px; color: #667eea;" id="progress-text">Uploading...</p>
                            </div>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeUploadModal()">Cancel</button>
                    <button class="btn btn-success" onclick="uploadPrompt()">Upload</button>
                </div>
            </div>
        </div>

        <!-- Bulk Upload Modal -->
        <div id="bulk-upload-modal" class="modal">
            <div class="modal-content" style="max-width: 700px;">
                <div class="modal-header">
                    <h2>Bulk Upload Audio Prompts</h2>
                    <button class="close-btn" onclick="closeBulkUploadModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <form id="bulk-upload-form">
                        <div class="form-group">
                            <label>Select Audio Files (MP3 or WAV) *</label>
                            <div class="upload-area" id="bulk-upload-area">
                                <div class="upload-icon">📦</div>
                                <div class="upload-text">
                                    <strong>Click to browse</strong> or drag and drop multiple audio files here
                                </div>
                                <input type="file" id="bulk-file-input" accept=".mp3,.wav" multiple style="display: none;">
                            </div>
                            <div id="bulk-file-info" style="margin-top: 10px; color: var(--color-text-secondary);"></div>
                        </div>
                        <div class="form-group">
                            <label>Name Prefix (optional)</label>
                            <input type="text" id="bulk-prefix" placeholder="e.g., IVR_">
                            <small style="color: var(--color-text-tertiary);">Added before each filename</small>
                        </div>
                        <div class="form-group">
                            <label>Name Suffix (optional)</label>
                            <input type="text" id="bulk-suffix" placeholder="e.g., _v2">
                            <small style="color: var(--color-text-tertiary);">Added after each filename (before extension is removed)</small>
                        </div>
                        <div class="form-group">
                            <label>Description (optional)</label>
                            <textarea id="bulk-description" placeholder="Applied to all uploaded prompts"></textarea>
                        </div>
                    </form>
                    <!-- Bulk Upload Progress Section -->
                    <div id="bulk-progress-section" style="display: none; margin-top: 20px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                            <span id="bulk-progress-text">Uploading...</span>
                            <span id="bulk-progress-count">0/0</span>
                        </div>
                        <div class="progress-bar" style="height: 12px;">
                            <div class="progress-fill" id="bulk-progress-fill" style="width: 0%"></div>
                        </div>
                        <div id="bulk-upload-log" style="margin-top: 15px; max-height: 200px; overflow-y: auto; font-size: 13px; background: rgba(0,0,0,0.2); padding: 10px; border-radius: 8px;">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn btn-secondary" onclick="closeBulkUploadModal()" id="bulk-cancel-btn">Cancel</button>
                    <button class="btn btn-success" onclick="startBulkUpload()" id="bulk-upload-btn">Upload All</button>
                </div>
            </div>
        </div>

        <script>
            let allPrompts = [];
            let selectedPrompts = new Set();
            let currentFile = null;
            let bulkFiles = [];
            let bulkUploadInProgress = false;

            // Load prompts on page load
            document.addEventListener('DOMContentLoaded', loadPrompts);

            // Search functionality
            document.getElementById('search-input').addEventListener('input', filterPrompts);

            // Upload area interactions
            const uploadArea = document.getElementById('upload-area');
            const fileInput = document.getElementById('file-input');

            uploadArea.addEventListener('click', () => fileInput.click());

            fileInput.addEventListener('change', (e) => {
                handleFileSelect(e.target.files[0]);
            });

            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.classList.add('drag-over');
            });

            uploadArea.addEventListener('dragleave', () => {
                uploadArea.classList.remove('drag-over');
            });

            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.classList.remove('drag-over');
                handleFileSelect(e.dataTransfer.files[0]);
            });

            function handleFileSelect(file) {
                if (!file) return;

                // Validate file type
                const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3'];
                const validExtensions = ['.mp3', '.wav'];
                const fileExt = '.' + file.name.split('.').pop().toLowerCase();

                if (!validTypes.includes(file.type) && !validExtensions.includes(fileExt)) {
                    alert('Please select an MP3 or WAV file');
                    return;
                }

                // Validate file size (10MB)
                if (file.size > 10 * 1024 * 1024) {
                    alert('File size must be less than 10MB');
                    return;
                }

                currentFile = file;
                const fileInfo = document.getElementById('file-info');
                fileInfo.innerHTML = `<strong>Selected:</strong> ${file.name} (${formatFileSize(file.size)})`;
            }

            function formatFileSize(bytes) {
                if (bytes < 1024) return bytes + ' B';
                if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
                return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
            }

            async function loadPrompts() {
                try {
                    const response = await fetch('/api/prompts?per_page=100');
                    const result = await response.json();

                    if (result.status === 200 && result.data) {
                        // Talkdesk API returns prompts in HAL format with _embedded wrapper
                        allPrompts = result.data._embedded?.prompts || result.data.prompts || [];
                        renderPrompts();
                    } else {
                        showError('Failed to load prompts');
                    }
                } catch (error) {
                    showError('Error loading prompts: ' + error.message);
                }
            }

            function renderPrompts() {
                const container = document.getElementById('prompts-container');
                const search = document.getElementById('search-input').value.toLowerCase();

                let filtered = allPrompts;
                if (search) {
                    filtered = allPrompts.filter(p =>
                        p.name.toLowerCase().includes(search) ||
                        (p.description && p.description.toLowerCase().includes(search))
                    );
                }

                document.getElementById('total-count').textContent = allPrompts.length;
                document.getElementById('visible-count').textContent = filtered.length;

                if (filtered.length === 0) {
                    container.innerHTML = `
                        <div class="empty-state">
                            <div class="empty-state-icon">🎵</div>
                            <h3>${search ? 'No prompts found' : 'No prompts yet'}</h3>
                            <p>${search ? 'Try a different search term' : 'Upload your first audio prompt to get started'}</p>
                        </div>
                    `;
                    return;
                }

                const grid = document.createElement('div');
                grid.className = 'prompts-grid';

                filtered.forEach(prompt => {
                    const card = createPromptCard(prompt);
                    grid.appendChild(card);
                });

                container.innerHTML = '';
                container.appendChild(grid);
            }

            async function playPrompt(promptId) {
                const wrapper = document.getElementById(`audio-wrapper-${promptId}`);
                const playBtn = wrapper.querySelector('.play-btn');
                const audioPlayer = document.getElementById(`audio-${promptId}`);

                playBtn.textContent = '⏳ Loading...';
                playBtn.classList.add('loading');

                try {
                    const response = await fetch(`/api/prompts/${promptId}/download`);
                    const result = await response.json();

                    if (result.url) {
                        audioPlayer.src = result.url;
                        audioPlayer.oncanplaythrough = () => {
                            playBtn.classList.add('hidden');
                            audioPlayer.classList.add('loaded');
                            audioPlayer.play();
                        };
                        audioPlayer.onerror = () => {
                            playBtn.textContent = '⚠ Error loading';
                            playBtn.classList.remove('loading');
                        };
                        audioPlayer.load();
                    } else {
                        playBtn.textContent = '⚠ No audio URL';
                        playBtn.classList.remove('loading');
                    }
                } catch (error) {
                    playBtn.textContent = '⚠ Error';
                    playBtn.classList.remove('loading');
                }
            }

            function createPromptCard(prompt) {
                const card = document.createElement('div');
                card.className = 'prompt-card';
                card.dataset.id = prompt.id;
                if (selectedPrompts.has(prompt.id)) {
                    card.classList.add('selected');
                }

                card.innerHTML = `
                    <input type="checkbox" class="checkbox" ${selectedPrompts.has(prompt.id) ? 'checked' : ''}
                           onchange="toggleSelection('${prompt.id}')">
                    <div class="prompt-header">
                        <div class="prompt-title">${escapeHtml(prompt.name)}</div>
                        ${prompt.description ? `<div class="prompt-description">${escapeHtml(prompt.description)}</div>` : ''}
                    </div>
                    <div class="prompt-body">
                        <div class="prompt-meta">
                            <span class="meta-item">📅 ${formatDate(prompt.created_at)}</span>
                            ${prompt.duration ? `<span class="meta-item">⏱️ ${prompt.duration}s</span>` : ''}
                        </div>
                        <div class="prompt-audio">
                            <div class="audio-wrapper" id="audio-wrapper-${prompt.id}">
                                <button class="play-btn" onclick="playPrompt('${prompt.id}')">
                                    ▶ Click to Play
                                </button>
                                <audio class="audio-player" id="audio-${prompt.id}" controls preload="none"></audio>
                            </div>
                        </div>
                        <div class="prompt-actions">
                            <button class="btn btn-sm btn-secondary" onclick="viewDetails('${prompt.id}')">Details</button>
                            <button class="btn btn-sm btn-primary" onclick="downloadPrompt('${prompt.id}')">Download</button>
                            <button class="btn btn-sm btn-danger" onclick="deletePrompt('${prompt.id}')">Delete</button>
                        </div>
                    </div>
                `;

                return card;
            }

            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML;
            }

            function formatDate(dateString) {
                if (!dateString) return 'N/A';
                const date = new Date(dateString);
                return date.toLocaleDateString();
            }

            function filterPrompts() {
                renderPrompts();
            }

            function toggleSelection(promptId) {
                if (selectedPrompts.has(promptId)) {
                    selectedPrompts.delete(promptId);
                } else {
                    selectedPrompts.add(promptId);
                }
                updateBulkActions();
                renderPrompts();
            }

            function updateBulkActions() {
                const bulkActions = document.getElementById('bulk-actions');
                const count = document.getElementById('selected-count');
                count.textContent = selectedPrompts.size;
                bulkActions.style.display = selectedPrompts.size > 0 ? 'flex' : 'none';
            }

            function clearSelection() {
                selectedPrompts.clear();
                updateBulkActions();
                renderPrompts();
            }

            function showUploadModal() {
                document.getElementById('upload-modal').classList.add('active');
            }

            function closeUploadModal() {
                document.getElementById('upload-modal').classList.remove('active');
                document.getElementById('upload-form').reset();
                document.getElementById('file-info').innerHTML = '';
                document.getElementById('upload-progress').style.display = 'none';
                currentFile = null;
            }

            // Bulk Upload Functions
            function showBulkUploadModal() {
                document.getElementById('bulk-upload-modal').classList.add('active');
                setupBulkUploadArea();
            }

            function closeBulkUploadModal() {
                if (bulkUploadInProgress) {
                    if (!confirm('Upload in progress. Are you sure you want to cancel?')) {
                        return;
                    }
                }
                document.getElementById('bulk-upload-modal').classList.remove('active');
                document.getElementById('bulk-upload-form').reset();
                document.getElementById('bulk-file-info').innerHTML = '';
                document.getElementById('bulk-progress-section').style.display = 'none';
                document.getElementById('bulk-upload-log').innerHTML = '';
                document.getElementById('bulk-upload-btn').disabled = false;
                document.getElementById('bulk-cancel-btn').textContent = 'Cancel';
                bulkFiles = [];
                bulkUploadInProgress = false;
            }

            function setupBulkUploadArea() {
                const bulkUploadArea = document.getElementById('bulk-upload-area');
                const bulkFileInput = document.getElementById('bulk-file-input');

                // Remove existing listeners to prevent duplicates
                bulkUploadArea.onclick = () => bulkFileInput.click();

                bulkFileInput.onchange = (e) => {
                    handleBulkFileSelect(e.target.files);
                };

                bulkUploadArea.ondragover = (e) => {
                    e.preventDefault();
                    bulkUploadArea.classList.add('drag-over');
                };

                bulkUploadArea.ondragleave = () => {
                    bulkUploadArea.classList.remove('drag-over');
                };

                bulkUploadArea.ondrop = (e) => {
                    e.preventDefault();
                    bulkUploadArea.classList.remove('drag-over');
                    handleBulkFileSelect(e.dataTransfer.files);
                };
            }

            function handleBulkFileSelect(files) {
                const validTypes = ['audio/mpeg', 'audio/wav', 'audio/mp3'];
                const validExtensions = ['.mp3', '.wav'];
                const maxSize = 10 * 1024 * 1024; // 10MB

                bulkFiles = [];
                const errors = [];

                for (const file of files) {
                    const fileExt = '.' + file.name.split('.').pop().toLowerCase();

                    if (!validTypes.includes(file.type) && !validExtensions.includes(fileExt)) {
                        errors.push(`${file.name}: Invalid file type (must be MP3 or WAV)`);
                        continue;
                    }

                    if (file.size > maxSize) {
                        errors.push(`${file.name}: File too large (max 10MB)`);
                        continue;
                    }

                    bulkFiles.push(file);
                }

                // Update file info display
                const fileInfo = document.getElementById('bulk-file-info');
                let html = '';

                if (bulkFiles.length > 0) {
                    const totalSize = bulkFiles.reduce((sum, f) => sum + f.size, 0);
                    html += `<strong>${bulkFiles.length} files selected</strong> (${formatFileSize(totalSize)} total)<br>`;
                    html += '<div style="max-height: 120px; overflow-y: auto; margin-top: 8px; padding: 8px; background: rgba(0,0,0,0.2); border-radius: 6px;">';
                    bulkFiles.forEach((f, i) => {
                        const name = f.name.replace(/\\.[^.]+$/, '');
                        html += `<div style="padding: 2px 0; font-size: 12px;">${i + 1}. ${f.name} (${formatFileSize(f.size)})</div>`;
                    });
                    html += '</div>';
                }

                if (errors.length > 0) {
                    html += '<div style="color: var(--color-error); margin-top: 8px;">';
                    html += '<strong>Skipped files:</strong><br>';
                    errors.forEach(e => {
                        html += `<div style="font-size: 12px;">- ${e}</div>`;
                    });
                    html += '</div>';
                }

                fileInfo.innerHTML = html;
            }

            function generatePromptName(filename, prefix, suffix) {
                // Remove file extension
                const name = filename.replace(/\\.[^.]+$/, '');
                return `${prefix}${name}${suffix}`;
            }

            async function startBulkUpload() {
                if (bulkFiles.length === 0) {
                    alert('Please select at least one audio file');
                    return;
                }

                const prefix = document.getElementById('bulk-prefix').value.trim();
                const suffix = document.getElementById('bulk-suffix').value.trim();
                const description = document.getElementById('bulk-description').value.trim();

                bulkUploadInProgress = true;
                document.getElementById('bulk-upload-btn').disabled = true;
                document.getElementById('bulk-cancel-btn').textContent = 'Close';
                document.getElementById('bulk-progress-section').style.display = 'block';

                const log = document.getElementById('bulk-upload-log');
                const progressFill = document.getElementById('bulk-progress-fill');
                const progressCount = document.getElementById('bulk-progress-count');
                const progressText = document.getElementById('bulk-progress-text');

                let successCount = 0;
                let failCount = 0;
                const total = bulkFiles.length;

                log.innerHTML = '<div style="color: var(--color-text-tertiary);">Starting bulk upload...</div>';

                for (let i = 0; i < bulkFiles.length; i++) {
                    const file = bulkFiles[i];
                    const promptName = generatePromptName(file.name, prefix, suffix);

                    progressCount.textContent = `${i + 1}/${total}`;
                    progressText.textContent = `Uploading: ${file.name}`;
                    progressFill.style.width = `${((i) / total) * 100}%`;

                    log.innerHTML += `<div style="padding: 4px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
                        <span style="color: var(--color-warning);">⏳</span> Uploading: ${promptName}...
                    </div>`;
                    log.scrollTop = log.scrollHeight;

                    try {
                        const formData = new FormData();
                        formData.append('file', file);
                        formData.append('name', promptName);
                        if (description) {
                            formData.append('description', description);
                        }

                        const response = await fetch('/api/prompts/upload', {
                            method: 'POST',
                            body: formData
                        });

                        const result = await response.json();

                        // Update the last log entry
                        const lastEntry = log.lastElementChild;
                        if (result.success) {
                            successCount++;
                            lastEntry.innerHTML = `<span style="color: var(--color-success);">✓</span> ${promptName} - uploaded successfully`;
                        } else {
                            failCount++;
                            lastEntry.innerHTML = `<span style="color: var(--color-error);">✗</span> ${promptName} - ${result.error || 'Upload failed'}`;
                        }
                    } catch (error) {
                        failCount++;
                        const lastEntry = log.lastElementChild;
                        lastEntry.innerHTML = `<span style="color: var(--color-error);">✗</span> ${promptName} - ${error.message}`;
                    }

                    log.scrollTop = log.scrollHeight;

                    // Rate limiting delay (300ms between uploads)
                    if (i < bulkFiles.length - 1) {
                        await new Promise(resolve => setTimeout(resolve, 300));
                    }
                }

                // Complete
                progressFill.style.width = '100%';
                progressCount.textContent = `${total}/${total}`;
                progressText.textContent = 'Upload complete!';

                log.innerHTML += `<div style="padding: 8px 0; margin-top: 8px; border-top: 2px solid rgba(255,255,255,0.2); font-weight: bold;">
                    Summary: ${successCount} successful, ${failCount} failed
                </div>`;
                log.scrollTop = log.scrollHeight;

                bulkUploadInProgress = false;

                // Refresh the prompts list
                loadPrompts();
            }

            async function uploadPrompt() {
                const name = document.getElementById('prompt-name').value.trim();
                const description = document.getElementById('prompt-description').value.trim();

                if (!name) {
                    alert('Please enter a prompt name');
                    return;
                }

                if (!currentFile) {
                    alert('Please select an audio file');
                    return;
                }

                const formData = new FormData();
                formData.append('file', currentFile);
                formData.append('name', name);
                formData.append('description', description);

                try {
                    document.getElementById('upload-progress').style.display = 'block';
                    document.getElementById('progress-fill').style.width = '50%';

                    const response = await fetch('/api/prompts/upload', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();

                    if (result.success) {
                        document.getElementById('progress-fill').style.width = '100%';
                        document.getElementById('progress-text').textContent = 'Upload complete!';
                        setTimeout(() => {
                            closeUploadModal();
                            loadPrompts();
                        }, 1000);
                    } else {
                        throw new Error(result.error || 'Upload failed');
                    }
                } catch (error) {
                    alert('Upload failed: ' + error.message);
                    document.getElementById('upload-progress').style.display = 'none';
                }
            }

            async function downloadPrompt(promptId) {
                try {
                    const response = await fetch(`/api/prompts/${promptId}/download`);
                    const result = await response.json();

                    if (result.url) {
                        window.open(result.url, '_blank');
                    } else {
                        throw new Error('No download URL received');
                    }
                } catch (error) {
                    alert('Download failed: ' + error.message);
                }
            }

            async function deletePrompt(promptId) {
                if (!confirm('Are you sure you want to delete this prompt?')) return;

                try {
                    const response = await fetch(`/api/prompts/${promptId}`, {
                        method: 'DELETE'
                    });

                    const result = await response.json();

                    if (result.status === 200 || result.status === 204) {
                        loadPrompts();
                    } else {
                        throw new Error(result.error || 'Delete failed');
                    }
                } catch (error) {
                    alert('Delete failed: ' + error.message);
                }
            }

            async function bulkDelete() {
                if (selectedPrompts.size === 0) return;

                if (!confirm(`Delete ${selectedPrompts.size} selected prompts?`)) return;

                const requests = Array.from(selectedPrompts).map(id => ({ id }));

                try {
                    const response = await fetch('/api/prompts/bulk', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            operation: 'delete',
                            requests: requests
                        })
                    });

                    const result = await response.json();

                    if (result.status === 200) {
                        selectedPrompts.clear();
                        updateBulkActions();
                        loadPrompts();
                    } else {
                        throw new Error(result.error || 'Bulk delete failed');
                    }
                } catch (error) {
                    alert('Bulk delete failed: ' + error.message);
                }
            }

            async function viewDetails(promptId) {
                try {
                    const response = await fetch(`/api/prompts/${promptId}`);
                    const result = await response.json();

                    if (result.status === 200 && result.data) {
                        const prompt = result.data;
                        alert(`Prompt Details:\n\nName: ${prompt.name}\nDescription: ${prompt.description || 'N/A'}\nID: ${prompt.id}\nCreated: ${formatDate(prompt.created_at)}`);
                        // TODO: Show in a proper modal
                    }
                } catch (error) {
                    alert('Failed to load details: ' + error.message);
                }
            }

            function refreshPrompts() {
                loadPrompts();
            }

            function showError(message) {
                const container = document.getElementById('prompts-container');
                container.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-state-icon">⚠️</div>
                        <h3>Error</h3>
                        <p>${escapeHtml(message)}</p>
                        <button class="btn btn-primary" onclick="refreshPrompts()">Try Again</button>
                    </div>
                `;
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/')
def index():
    endpoints = api_client.get_endpoints()
    tags = api_client.get_tags()

    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Talkdesk API Explorer</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            /* Design System Tokens */
            :root {
                --color-primary: #2563eb;
                --color-primary-light: #3b82f6;
                --color-primary-dark: #1e40af;
                --color-primary-alpha-10: rgba(37, 99, 235, 0.1);
                --color-primary-alpha-20: rgba(37, 99, 235, 0.2);
                --color-secondary: #7c3aed;
                --color-secondary-light: #8b5cf6;
                --color-success: #22c55e;
                --color-success-light: #4ade80;
                --color-warning: #f59e0b;
                --color-error: #ef4444;
                --color-grey-50: #fafafa;
                --color-grey-100: #f5f5f5;
                --color-grey-200: #e5e5e5;
                --color-grey-300: #d4d4d4;
                --color-grey-400: #a3a3a3;
                --color-grey-500: #737373;
                --color-grey-600: #525252;
                --color-grey-700: #404040;
                --color-grey-800: #262626;
                --color-grey-900: #171717;
                --color-background: #ffffff;
                --color-surface: #fafafa;
                --color-surface-elevated: #ffffff;
                --color-border: #e5e5e5;
                --color-border-hover: #d4d4d4;
                --color-text-primary: #0a0a0a;
                --color-text-secondary: #525252;
                --color-text-tertiary: #737373;

                /* Radial Gradient Extension - Ocean Theme Colors */
                --gradient-color-1: #800000;  /* Maroon */
                --gradient-color-2: #804000;  /* Brown */
                --gradient-color-3: #004040;  /* Dark Teal */
                --gradient-color-4: #006666;  /* Ocean Blue */
                --gradient-color-5: #004040;  /* Deep Sea */
                --gradient-color-6: #006666;  /* Ocean Teal */
                --gradient-color-7: #008080;  /* Turquoise */
                --gradient-color-8: #003333;  /* Ocean Deep */
                --gradient-color-9: #00B4B4;  /* Bright Turquoise */
                --gradient-color-10: #20B2AA; /* Sea Green */
                --gradient-base-black: #001a1a;

                /* Radial Gradient Patterns - Ocean Theme */
                --gradient-teal: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-5) 0%, var(--gradient-base-black) 100%);
                --gradient-ocean: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-6) 0%, var(--gradient-base-black) 100%);
                --gradient-turquoise: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-7) 0%, var(--gradient-base-black) 100%);
                --gradient-radial-multi: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-5) 0%, var(--gradient-color-7) 50%, var(--gradient-base-black) 100%);
                --gradient-radial-glow: radial-gradient(circle at center, var(--gradient-color-7) 0%, rgba(0, 128, 128, 0.3) 30%, transparent 60%);

                --font-family-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                --font-family-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', monospace;
                --font-size-xs: 0.75rem;
                --font-size-sm: 0.875rem;
                --font-size-base: 1rem;
                --font-size-lg: 1.125rem;
                --font-size-xl: 1.25rem;
                --font-size-2xl: 1.5rem;
                --font-weight-normal: 400;
                --font-weight-medium: 500;
                --font-weight-semibold: 600;
                --font-weight-bold: 700;
                --line-height-normal: 1.5;
                --spacing-1: 0.25rem;
                --spacing-2: 0.5rem;
                --spacing-3: 0.75rem;
                --spacing-4: 1rem;
                --spacing-5: 1.25rem;
                --spacing-6: 1.5rem;
                --spacing-8: 2rem;
                --radius-md: 0.375rem;
                --radius-lg: 0.5rem;
                --radius-xl: 0.75rem;
                --radius-full: 9999px;
                --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
                --duration-fast: 150ms;
                --duration-base: 250ms;
                --ease-out: cubic-bezier(0, 0, 0.2, 1);
            }

            /* Base Styles */
            *, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: var(--font-family-primary);
                background: var(--gradient-radial-multi);
                background-attachment: fixed;
                min-height: 100vh;
                color: #ffffff;
                line-height: var(--line-height-normal);
                position: relative;
                overflow-x: hidden;
            }

            /* Floating Orbs - Using Radial Gradient Extension */
            body::before,
            body::after {
                content: '';
                position: fixed;
                border-radius: 50%;
                filter: blur(80px);
                opacity: 0.5;
                pointer-events: none;
                z-index: 0;
            }
            body::before {
                width: 500px;
                height: 500px;
                background: radial-gradient(circle, var(--gradient-color-6) 0%, transparent 70%);
                top: -150px;
                right: -50px;
                animation: floatOrb 20s ease-in-out infinite;
            }
            body::after {
                width: 400px;
                height: 400px;
                background: radial-gradient(circle, var(--gradient-color-7) 0%, transparent 70%);
                bottom: -100px;
                left: -50px;
                animation: floatOrb 25s ease-in-out infinite reverse;
            }
            @keyframes floatOrb {
                0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.5; }
                33% { transform: translate(20px, -30px) scale(1.2); opacity: 0.7; }
                66% { transform: translate(-20px, 20px) scale(0.9); opacity: 0.4; }
            }

            /* Header */
            .header {
                background: linear-gradient(135deg, rgba(0, 64, 64, 0.95) 0%, rgba(0, 128, 128, 0.95) 100%);
                backdrop-filter: blur(20px);
                color: white;
                padding: var(--spacing-6) var(--spacing-8);
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.3);
                border-bottom: 1px solid rgba(0, 180, 180, 0.3);
                position: relative;
                z-index: 10;
            }
            .header-content {
                max-width: 1200px;
                margin: 0 auto;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            .header h1 {
                font-size: var(--font-size-2xl);
                font-weight: var(--font-weight-bold);
                margin-bottom: var(--spacing-1);
            }
            .header p {
                opacity: 0.9;
                font-size: var(--font-size-sm);
            }
            .header-link {
                color: white;
                text-decoration: none;
                font-size: var(--font-size-sm);
                font-weight: var(--font-weight-medium);
                padding: var(--spacing-2) var(--spacing-4);
                background: linear-gradient(135deg, rgba(255,255,255,0.2) 0%, rgba(255,255,255,0.1) 100%);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: var(--radius-lg);
                transition: all var(--duration-fast) var(--ease-out);
            }
            .header-link:hover {
                background: linear-gradient(135deg, rgba(255,255,255,0.3) 0%, rgba(255,255,255,0.15) 100%);
                transform: translateY(-1px);
            }
            .base-url {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-xs);
                background: rgba(255,255,255,0.15);
                padding: var(--spacing-1) var(--spacing-2);
                border-radius: var(--radius-md);
                margin-top: var(--spacing-1);
                display: inline-block;
            }

            /* Container */
            .container {
                max-width: 1200px;
                margin: 0 auto;
                padding: var(--spacing-6);
                position: relative;
                z-index: 1;
            }

            /* Filter Panel */
            .filter-panel {
                background: linear-gradient(135deg, rgba(0, 64, 64, 0.3) 0%, rgba(0, 128, 128, 0.2) 100%);
                backdrop-filter: blur(20px);
                padding: var(--spacing-5);
                margin-bottom: var(--spacing-5);
                border-radius: var(--radius-xl);
                border: 1px solid rgba(255, 255, 255, 0.15);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1);
            }
            .filter-controls {
                display: flex;
                gap: var(--spacing-4);
                align-items: flex-end;
                flex-wrap: wrap;
            }
            .filter-group {
                flex: 1;
                min-width: 200px;
            }
            .filter-group label {
                display: block;
                font-weight: var(--font-weight-medium);
                margin-bottom: var(--spacing-2);
                font-size: var(--font-size-sm);
                color: rgba(255, 255, 255, 0.8);
            }
            .filter-group input,
            .filter-group select {
                width: 100%;
                padding: var(--spacing-3) var(--spacing-4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: var(--radius-lg);
                font-size: var(--font-size-sm);
                font-family: var(--font-family-primary);
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                transition: all var(--duration-fast) var(--ease-out);
            }
            .filter-group input:focus,
            .filter-group select:focus {
                outline: none;
                border-color: rgba(0, 180, 180, 0.6);
                box-shadow: 0 0 0 3px rgba(0, 180, 180, 0.2);
                background: rgba(255, 255, 255, 0.15);
            }
            .filter-group input::placeholder { color: rgba(255, 255, 255, 0.5); }
            .filter-group select option {
                background: #1e293b;
                color: #ffffff;
            }
            .filter-stats {
                margin-top: var(--spacing-4);
                color: rgba(255, 255, 255, 0.7);
                font-size: var(--font-size-sm);
            }
            .filter-stats strong {
                color: #ffffff;
            }

            /* Endpoint Card - Using Radial Gradient Hover Effect */
            .endpoint-card {
                position: relative;
                overflow: hidden;
                background: rgba(0, 51, 51, 0.4);
                backdrop-filter: blur(20px);
                border: 1px solid rgba(0, 128, 128, 0.3);
                margin-bottom: var(--spacing-3);
                border-radius: var(--radius-xl);
                transition: all 0.3s ease;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            }
            .endpoint-card::before {
                content: '';
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                border-radius: 50%;
                background: radial-gradient(circle, var(--gradient-color-7), transparent);
                opacity: 0;
                transform: translate(-50%, -50%);
                transition: all 0.6s ease;
                z-index: 0;
            }
            .endpoint-card:hover::before {
                width: 300%;
                height: 300%;
                opacity: 0.15;
            }
            .endpoint-card:hover {
                box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35), 0 0 30px rgba(0, 128, 128, 0.15);
                border-color: rgba(0, 128, 128, 0.5);
                transform: translateY(-2px);
            }
            .endpoint-card.hidden { display: none; }

            .endpoint-header {
                padding: var(--spacing-4) var(--spacing-5);
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: space-between;
                transition: background var(--duration-fast) var(--ease-out);
                position: relative;
                z-index: 1;
            }
            .endpoint-header:hover {
                background: radial-gradient(100% 200% at 50% 100%, rgba(0, 102, 102, 0.2) 0%, transparent 100%);
            }
            .endpoint-info {
                display: flex;
                align-items: center;
                flex-wrap: wrap;
                gap: var(--spacing-3);
            }
            .method {
                font-weight: var(--font-weight-semibold);
                padding: var(--spacing-1) var(--spacing-3);
                border-radius: var(--radius-md);
                color: white;
                font-size: var(--font-size-xs);
                min-width: 56px;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }
            .GET { background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%); }
            .POST { background: linear-gradient(135deg, #22c55e 0%, #10b981 100%); }
            .PATCH { background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%); }
            .DELETE { background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); }

            .path {
                font-family: var(--font-family-mono);
                font-size: var(--font-size-sm);
                color: #ffffff;
                font-weight: var(--font-weight-medium);
            }
            .tag-badge {
                display: inline-block;
                background: rgba(0, 180, 180, 0.2);
                color: #60a5fa;
                padding: var(--spacing-1) var(--spacing-2);
                border-radius: var(--radius-full);
                font-size: var(--font-size-xs);
                font-weight: var(--font-weight-medium);
                border: 1px solid rgba(0, 180, 180, 0.3);
            }
            .expand-icon {
                color: rgba(255, 255, 255, 0.5);
                transition: transform var(--duration-fast) var(--ease-out);
                font-size: var(--font-size-sm);
            }
            .endpoint-card.expanded .expand-icon {
                transform: rotate(180deg);
            }

            .endpoint-summary {
                padding: 0 var(--spacing-5) var(--spacing-4);
                color: rgba(255, 255, 255, 0.7);
                font-size: var(--font-size-sm);
            }

            .details {
                padding: var(--spacing-5);
                border-top: 1px solid rgba(255, 255, 255, 0.1);
                display: none;
                background: linear-gradient(180deg, rgba(0, 0, 0, 0.3) 0%, rgba(15, 23, 42, 0.4) 100%);
                position: relative;
                z-index: 2;
            }

            .param-group {
                margin-bottom: var(--spacing-4);
            }
            .param-group label {
                display: block;
                font-weight: var(--font-weight-medium);
                margin-bottom: var(--spacing-2);
                font-size: var(--font-size-sm);
                color: rgba(255, 255, 255, 0.9);
            }
            .param-group input {
                width: 100%;
                max-width: 400px;
                padding: var(--spacing-3) var(--spacing-4);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: var(--radius-lg);
                font-family: var(--font-family-primary);
                font-size: var(--font-size-sm);
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                transition: all var(--duration-fast) var(--ease-out);
            }
            .param-group input:focus {
                outline: none;
                border-color: rgba(0, 180, 180, 0.6);
                box-shadow: 0 0 0 3px rgba(0, 180, 180, 0.2);
                background: rgba(255, 255, 255, 0.15);
            }
            .param-group input::placeholder { color: rgba(255, 255, 255, 0.4); }

            .section-title {
                font-size: var(--font-size-sm);
                font-weight: var(--font-weight-semibold);
                color: #ffffff;
                margin-bottom: var(--spacing-3);
                margin-top: var(--spacing-4);
            }
            .section-title:first-child {
                margin-top: 0;
            }

            textarea.req-body {
                width: 100%;
                height: 150px;
                font-family: var(--font-family-mono);
                font-size: var(--font-size-sm);
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: var(--spacing-4);
                border-radius: var(--radius-lg);
                background: rgba(255, 255, 255, 0.1);
                color: #ffffff;
                resize: vertical;
                transition: all var(--duration-fast) var(--ease-out);
            }
            textarea.req-body:focus {
                outline: none;
                border-color: rgba(0, 180, 180, 0.6);
                box-shadow: 0 0 0 3px rgba(0, 180, 180, 0.2);
                background: rgba(255, 255, 255, 0.15);
            }
            textarea.req-body::placeholder { color: rgba(255, 255, 255, 0.4); }

            /* Submit Button - Using Radial Gradient from Design System */
            .submit-btn {
                background: radial-gradient(100% 100% at 50% 0%, var(--gradient-color-6) 0%, var(--gradient-color-5) 100%);
                color: white;
                border: none;
                padding: var(--spacing-3) var(--spacing-6);
                cursor: pointer;
                border-radius: var(--radius-lg);
                margin-top: var(--spacing-4);
                font-family: var(--font-family-primary);
                font-size: var(--font-size-sm);
                font-weight: var(--font-weight-medium);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                box-shadow: 0 4px 15px rgba(0, 64, 64, 0.4);
            }
            .submit-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(0, 102, 102, 0.5);
            }

            .response-area {
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(0, 0, 0, 0.6) 100%);
                border: 1px solid rgba(0, 180, 180, 0.2);
                color: #94a3b8;
                padding: var(--spacing-5);
                margin-top: var(--spacing-5);
                border-radius: var(--radius-lg);
                white-space: pre-wrap;
                font-family: var(--font-family-mono);
                font-size: var(--font-size-sm);
                display: none;
                overflow-x: auto;
                line-height: 1.6;
                box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
            }

            /* Focus States */
            *:focus-visible {
                outline: 2px solid rgba(0, 180, 180, 0.8);
                outline-offset: 2px;
            }
            *:focus:not(:focus-visible) { outline: none; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="header-content">
                <div>
                    <h1>Talkdesk API Explorer</h1>
                    <p>Explore and test API endpoints</p>
                    <span class="base-url">{{ base_url }}</span>
                </div>
                <a href="/prompts-admin" class="header-link">Prompts Administration</a>
            </div>
        </div>

        <div class="container">
            <div class="filter-panel">
                <div class="filter-controls">
                    <div class="filter-group">
                        <label for="tag-filter">Filter by Tag</label>
                        <select id="tag-filter">
                            <option value="">All Tags</option>
                            {% for tag in tags %}
                            <option value="{{ tag }}">{{ tag }}</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="filter-group">
                        <label for="search-filter">Search Endpoints</label>
                        <input type="text" id="search-filter" placeholder="Search by path or summary...">
                    </div>
                </div>
                <div class="filter-stats">
                    Showing <strong><span id="visible-count">{{ endpoints|length }}</span></strong> of <strong>{{ endpoints|length }}</strong> endpoints
                </div>
            </div>

            <div id="endpoint-list">
            {% for ep in endpoints %}
                <div class="endpoint-card" data-tags="{{ ep.tags|join(',') }}" data-path="{{ ep.path }}" data-summary="{{ ep.summary }}">
                    <div class="endpoint-header" onclick="toggleDetails(this)">
                        <div class="endpoint-info">
                            <span class="method {{ ep.method }}">{{ ep.method }}</span>
                            <span class="path">{{ ep.path }}</span>
                            {% if ep.tags %}
                                {% for tag in ep.tags %}
                                <span class="tag-badge">{{ tag }}</span>
                                {% endfor %}
                            {% endif %}
                        </div>
                        <span class="expand-icon">▼</span>
                    </div>
                    <div class="endpoint-summary">{{ ep.summary }}</div>
                    <div class="details">
                        <form onsubmit="executeRequest(event, '{{ ep.method }}', '{{ ep.path }}'); return false;">

                            {% if ep.params %}
                                <h4 class="section-title">Path Parameters</h4>
                                {% for param in ep.params %}
                                <div class="param-group">
                                    <label>{{ param }}</label>
                                    <input type="text" class="path-param" data-key="{{ param }}" required placeholder="Value for {{ param }}">
                                </div>
                                {% endfor %}
                            {% endif %}

                            {% if ep.has_body %}
                                <h4 class="section-title">Request Body (JSON)</h4>
                                <textarea class="req-body" placeholder='{"key": "value"}'></textarea>
                            {% endif %}

                            <button type="submit" class="submit-btn">Execute Request</button>
                        </form>
                        <pre class="response-area">Response will appear here...</pre>
                    </div>
                </div>
            {% endfor %}
            </div>
        </div>

        <script>
            function toggleDetails(header) {
                const card = header.closest('.endpoint-card');
                const details = card.querySelector('.details');
                const isExpanded = details.style.display === 'block';

                details.style.display = isExpanded ? 'none' : 'block';
                card.classList.toggle('expanded', !isExpanded);
            }

            function filterEndpoints() {
                const tagFilter = document.getElementById('tag-filter').value.toLowerCase();
                const searchFilter = document.getElementById('search-filter').value.toLowerCase();
                const cards = document.querySelectorAll('.endpoint-card');
                let visibleCount = 0;

                cards.forEach(card => {
                    const tags = card.getAttribute('data-tags').toLowerCase();
                    const path = card.getAttribute('data-path').toLowerCase();
                    const summary = card.getAttribute('data-summary').toLowerCase();

                    const matchesTag = !tagFilter || tags.includes(tagFilter);
                    const matchesSearch = !searchFilter || path.includes(searchFilter) || summary.includes(searchFilter);

                    if (matchesTag && matchesSearch) {
                        card.classList.remove('hidden');
                        visibleCount++;
                    } else {
                        card.classList.add('hidden');
                    }
                });

                document.getElementById('visible-count').textContent = visibleCount;
            }

            document.getElementById('tag-filter').addEventListener('change', filterEndpoints);
            document.getElementById('search-filter').addEventListener('input', filterEndpoints);

            async function executeRequest(e, method, originalPath) {
                e.preventDefault();
                const form = e.target;
                const responseArea = form.nextElementSibling;
                responseArea.style.display = 'block';
                responseArea.textContent = 'Sending request...';

                let finalPath = originalPath;
                const paramInputs = form.querySelectorAll('.path-param');
                paramInputs.forEach(input => {
                    const key = input.getAttribute('data-key');
                    const val = input.value.trim();
                    finalPath = finalPath.replace('{' + key + '}', val);
                });

                let bodyData = null;
                const bodyInput = form.querySelector('.req-body');
                if (bodyInput && bodyInput.value.trim()) {
                    try {
                        bodyData = JSON.parse(bodyInput.value);
                    } catch (err) {
                        responseArea.textContent = 'Error: Invalid JSON Body';
                        return;
                    }
                }

                try {
                    const res = await fetch('/execute', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            method: method,
                            path: finalPath,
                            body: bodyData
                        })
                    });
                    const data = await res.json();
                    responseArea.textContent = JSON.stringify(data, null, 2);
                } catch (err) {
                    responseArea.textContent = 'Error: ' + err.message;
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, endpoints=endpoints, base_url=api_client.base_url, tags=tags)

@app.route('/execute', methods=['POST'])
def execute():
    req_data = request.json
    method = req_data.get('method')
    path = req_data.get('path')
    body = req_data.get('body')

    result = api_client.execute_request(method, path, body)
    return jsonify(result)

# --- PROMPTS API ROUTES ---

@app.route('/api/prompts', methods=['GET'])
def api_list_prompts():
    """List all prompts with optional search and pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    search = request.args.get('q', None)

    result = prompts_manager.list_prompts(page=page, per_page=per_page, search=search)
    return jsonify(result)

@app.route('/api/prompts/<prompt_id>', methods=['GET'])
def api_get_prompt(prompt_id):
    """Get a specific prompt by ID"""
    result = prompts_manager.get_prompt(prompt_id)
    return jsonify(result)

@app.route('/api/prompts', methods=['POST'])
def api_create_prompt():
    """Create a new prompt"""
    data = request.json
    name = data.get('name')
    description = data.get('description')

    if not name:
        return jsonify({'error': 'Name is required'}), 400

    result = prompts_manager.create_prompt(name, description)
    return jsonify(result)

@app.route('/api/prompts/<prompt_id>', methods=['PATCH'])
def api_update_prompt(prompt_id):
    """Update prompt metadata"""
    data = request.json
    name = data.get('name')
    description = data.get('description')

    result = prompts_manager.update_prompt(prompt_id, name, description)
    return jsonify(result)

@app.route('/api/prompts/<prompt_id>', methods=['DELETE'])
def api_delete_prompt(prompt_id):
    """Delete a prompt"""
    result = prompts_manager.delete_prompt(prompt_id)
    return jsonify(result)

@app.route('/api/prompts/<prompt_id>/usage', methods=['GET'])
def api_get_prompt_usage(prompt_id):
    """Get usage statistics for a prompt"""
    result = prompts_manager.get_prompt_usage(prompt_id)
    return jsonify(result)

@app.route('/api/prompts/<prompt_id>/flows', methods=['GET'])
def api_get_prompt_flows(prompt_id):
    """Get flows using a specific prompt"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    result = prompts_manager.get_prompt_flows(prompt_id, page, per_page)
    return jsonify(result)

@app.route('/api/prompts/bulk', methods=['POST'])
def api_bulk_operation():
    """Perform bulk operations on prompts"""
    data = request.json
    operation = data.get('operation')
    requests_list = data.get('requests')

    if not operation or not requests_list:
        return jsonify({'error': 'Operation and requests are required'}), 400

    result = prompts_manager.bulk_operation(operation, requests_list)
    return jsonify(result)

@app.route('/api/prompts/upload', methods=['POST'])
def api_upload_prompt():
    """
    Handle prompt file upload workflow:
    1. Request upload link from Talkdesk
    2. Upload file to signed URL
    3. Create or update prompt
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    name = request.form.get('name')
    description = request.form.get('description', '')
    prompt_id = request.form.get('prompt_id')

    if not file.filename:
        return jsonify({'error': 'No file selected'}), 400

    if not name:
        return jsonify({'error': 'Prompt name is required'}), 400

    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in {'.mp3', '.wav'}:
        return jsonify({'error': 'Only MP3 and WAV files are allowed'}), 400

    content_type = 'audio/mpeg' if file_ext == '.mp3' else 'audio/wav'

    try:
        # Step 1: Request upload link
        upload_link_result = prompts_manager.request_upload_link(content_type)

        if upload_link_result.get('status') not in [200, 201]:
            return jsonify({'error': 'Failed to get upload link', 'details': upload_link_result}), 500

        upload_data = upload_link_result.get('data', {})
        upload_url = extract_hal_link(upload_data, 'upload_link')

        if not upload_url:
            return jsonify({'error': 'No upload URL received', 'response': upload_data}), 500

        # Step 2: Upload file to signed URL
        file.seek(0)
        upload_response = requests.put(
            upload_url,
            data=file.read(),
            headers={'Content-Type': content_type}
        )

        if upload_response.status_code not in [200, 201, 204]:
            return jsonify({'error': 'File upload failed', 'status': upload_response.status_code}), 500

        # Step 3: Create or update prompt
        if prompt_id:
            result = prompts_manager.update_prompt(prompt_id, name, description)
        else:
            result = prompts_manager.create_prompt(
                name=name,
                description=description,
                request_id=upload_data.get('id'),
                file_name=file.filename
            )

        return jsonify({'success': True, 'result': result})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/prompts/<prompt_id>/download', methods=['GET'])
def api_download_prompt(prompt_id):
    """Get download link for a prompt"""
    result = prompts_manager.get_download_link(prompt_id)

    if result.get('status') == 200:
        download_url = extract_hal_link(result.get('data', {}), 'location')
        if download_url:
            return jsonify({'url': download_url})

    return jsonify({'error': 'Failed to get download link', 'details': result}), 500

if __name__ == '__main__':
    # Ensure credentials are present
    if 'YOUR_CLIENT_ID' in CLIENT_ID:
        print("WARNING: Please set TALKDESK_CLIENT_ID and TALKDESK_CLIENT_SECRET environment variables.")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
