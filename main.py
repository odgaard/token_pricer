#!/usr/bin/env python3
import argparse
import os
import tiktoken
from pathlib import Path

def count_tokens_in_file(file_path):
    """Count tokens in a single file using Claude 3.5 Sonnet's tokenizer."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Claude 3.5 Sonnet uses cl100k_base encoding
        encoding = tiktoken.get_encoding("cl100k_base")
        tokens = encoding.encode(content)
        return len(tokens)
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return 0

def get_default_extensions():
    """Return a list of default file extensions to process."""
    return [
        '.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c',
        '.h', '.hpp', '.cs', '.rb', '.php', '.go', '.rs', '.swift',
        '.kt', '.kts', '.scala', '.sql', '.html', '.css', '.scss',
        '.sass', '.less', '.md', '.txt', '.json', '.yaml', '.yml'
    ]

def format_token_count(count):
    """Format token count with thousands separator and cost estimate."""
    return f"{count:,} tokens (≈${(count / 1_000_000 * 3):.2f} at $3/1M tokens)"

def main():
    parser = argparse.ArgumentParser(
        description='Count tokens in code files using Claude 3.5 Sonnet\'s tokenizer'
    )
    parser.add_argument('path', help='Path to file or directory')
    parser.add_argument(
        '--extensions',
        help='Comma-separated list of file extensions to process (e.g., .py,.js,.txt)',
        default=','.join(get_default_extensions())
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Show token count for each file'
    )
    parser.add_argument(
        '--max-file-size',
        type=int,
        default=1024 * 1024,  # 1MB
        help='Maximum file size to process in bytes'
    )

    args = parser.parse_args()

    # Convert extensions string to list and ensure they start with dot
    extensions = [ext if ext.startswith('.') else f'.{ext}'
                 for ext in args.extensions.split(',')]

    path = Path(args.path)
    total_tokens = 0
    total_files = 0
    skipped_files = 0

    if path.is_file():
        if path.stat().st_size <= args.max_file_size:
            tokens = count_tokens_in_file(path)
            if args.verbose:
                print(f"{path}: {format_token_count(tokens)}")
            total_tokens += tokens
            total_files += 1
        else:
            print(f"Skipped {path}: File too large")
            skipped_files += 1
    else:
        for root, _, files in os.walk(path):
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in extensions:
                    if file_path.stat().st_size <= args.max_file_size:
                        tokens = count_tokens_in_file(file_path)
                        if args.verbose:
                            print(f"{file_path}: {format_token_count(tokens)}")
                        total_tokens += tokens
                        total_files += 1
                    else:
                        if args.verbose:
                            print(f"Skipped {file_path}: File too large")
                        skipped_files += 1

    print(f"\nSummary:")
    print(f"Total files processed: {total_files:,}")
    print(f"Files skipped (too large): {skipped_files:,}")
    print(f"Total: {format_token_count(total_tokens)}")

if __name__ == '__main__':
    main()
