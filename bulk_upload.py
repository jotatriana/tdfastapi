#!/usr/bin/env python3
"""
Bulk Upload Script for Talkdesk Prompts

Upload multiple audio files from a directory to Talkdesk Prompts.

Usage:
    python bulk_upload.py /path/to/audio/files
    python bulk_upload.py /path/to/audio/files --prefix "IVR_" --description "Auto-uploaded"
    python bulk_upload.py /path/to/audio/files --dry-run --recursive

Options:
    --prefix        Add prefix to prompt names (default: none)
    --suffix        Add suffix to prompt names (default: none)
    --description   Set description for all prompts (default: none)
    --dry-run       Show what would be uploaded without actually uploading
    --recursive     Search subdirectories for audio files
    --delay         Delay between uploads in ms (default: 300)
"""

import argparse
import os
import sys
import time
from pathlib import Path

# Import the shared client module
from talkdesk_client import TalkdeskGenericClient, PromptsManager


def get_audio_files(directory, recursive=False):
    """
    Find all MP3 and WAV files in the specified directory.

    Args:
        directory: Path to scan for audio files
        recursive: If True, search subdirectories as well

    Returns:
        List of Path objects for audio files, sorted alphabetically
    """
    extensions = {'.mp3', '.wav'}
    path = Path(directory)

    if not path.exists():
        print(f"Error: Directory not found: {directory}")
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: Not a directory: {directory}")
        sys.exit(1)

    if recursive:
        files = []
        for ext in extensions:
            files.extend(path.rglob(f'*{ext}'))
    else:
        files = [f for f in path.iterdir() if f.suffix.lower() in extensions]

    return sorted(files, key=lambda x: x.name.lower())


def generate_prompt_name(file_path, prefix='', suffix=''):
    """
    Generate a prompt name from a filename.

    Args:
        file_path: Path to the audio file
        prefix: Optional prefix to add
        suffix: Optional suffix to add

    Returns:
        Prompt name string
    """
    # Get filename without extension
    name = Path(file_path).stem

    # Apply prefix and suffix
    return f"{prefix}{name}{suffix}"


def format_file_size(size_bytes):
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def print_progress_bar(current, total, width=50):
    """Print a simple progress bar."""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '=' * filled + '-' * (width - filled)
    print(f'\r[{bar}] {current}/{total} ({percent*100:.1f}%)', end='', flush=True)


def main():
    parser = argparse.ArgumentParser(
        description='Bulk upload audio files to Talkdesk Prompts',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  %(prog)s ./audio-files
  %(prog)s ./audio-files --prefix "IVR_" --description "IVR prompts"
  %(prog)s ./audio-files --dry-run
  %(prog)s ./audio-files --recursive --suffix "_v2"
        '''
    )

    parser.add_argument(
        'directory',
        help='Directory containing audio files (MP3/WAV)'
    )
    parser.add_argument(
        '--prefix',
        default='',
        help='Prefix to add to prompt names'
    )
    parser.add_argument(
        '--suffix',
        default='',
        help='Suffix to add to prompt names'
    )
    parser.add_argument(
        '--description',
        default='',
        help='Description to set for all prompts'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be uploaded without actually uploading'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Search subdirectories for audio files'
    )
    parser.add_argument(
        '--delay',
        type=int,
        default=300,
        help='Delay between uploads in milliseconds (default: 300)'
    )

    args = parser.parse_args()

    # Find audio files
    print(f"Scanning directory: {args.directory}")
    print(f"Recursive: {args.recursive}")
    print()

    files = get_audio_files(args.directory, recursive=args.recursive)

    if not files:
        print("No MP3 or WAV files found.")
        sys.exit(0)

    # Calculate total size
    total_size = sum(f.stat().st_size for f in files)

    print(f"Found {len(files)} audio files ({format_file_size(total_size)} total)")
    print()

    # Show preview
    print("Files to upload:")
    print("-" * 70)
    for i, file in enumerate(files, 1):
        prompt_name = generate_prompt_name(file, args.prefix, args.suffix)
        size = format_file_size(file.stat().st_size)
        # Show relative path if recursive, otherwise just filename
        display_path = str(file.relative_to(args.directory)) if args.recursive else file.name
        print(f"  {i:3}. {display_path}")
        print(f"       -> Prompt name: \"{prompt_name}\" ({size})")
    print("-" * 70)
    print()

    if args.dry_run:
        print("DRY RUN - No files were uploaded.")
        print(f"Would upload {len(files)} files with:")
        print(f"  Prefix: \"{args.prefix}\"" if args.prefix else "  Prefix: (none)")
        print(f"  Suffix: \"{args.suffix}\"" if args.suffix else "  Suffix: (none)")
        print(f"  Description: \"{args.description}\"" if args.description else "  Description: (none)")
        sys.exit(0)

    # Confirm upload
    print(f"Ready to upload {len(files)} files.")
    confirm = input("Continue? [y/N]: ").strip().lower()

    if confirm not in ['y', 'yes']:
        print("Upload cancelled.")
        sys.exit(0)

    print()
    print("Starting upload...")
    print()

    # Initialize client
    api_client = TalkdeskGenericClient()
    prompts_manager = PromptsManager(api_client)

    # Track results
    successes = []
    failures = []

    # Upload files
    for i, file in enumerate(files, 1):
        prompt_name = generate_prompt_name(file, args.prefix, args.suffix)

        print(f"[{i}/{len(files)}] Uploading: {file.name}")
        print(f"         Name: {prompt_name}")

        result = prompts_manager.upload_prompt_file(
            file_path=str(file),
            name=prompt_name,
            description=args.description if args.description else None
        )

        if result.get('success'):
            print(f"         Status: SUCCESS")
            successes.append({'file': file.name, 'name': prompt_name})
        else:
            error_msg = result.get('error', 'Unknown error')
            print(f"         Status: FAILED - {error_msg}")
            failures.append({'file': file.name, 'name': prompt_name, 'error': error_msg})

        # Progress bar
        print_progress_bar(i, len(files))
        print()

        # Rate limiting delay (skip after last file)
        if i < len(files) and args.delay > 0:
            time.sleep(args.delay / 1000)

    # Summary
    print()
    print("=" * 70)
    print("UPLOAD SUMMARY")
    print("=" * 70)
    print(f"Total files:  {len(files)}")
    print(f"Successful:   {len(successes)}")
    print(f"Failed:       {len(failures)}")
    print()

    if failures:
        print("FAILED UPLOADS:")
        print("-" * 70)
        for f in failures:
            print(f"  {f['file']}")
            print(f"    Error: {f['error']}")
        print("-" * 70)
        print()
        sys.exit(1)
    else:
        print("All files uploaded successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()
