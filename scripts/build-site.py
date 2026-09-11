#!/usr/bin/env python3
"""Stage only public site files and render the current board with hosted source links.

Usage: python3 scripts/build-site.py --output /path/to/empty-directory
The source repository is never modified. Python 3 and Bash are required.
"""
import argparse
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
LINK_BASE = 'https://github.com/GhostlyGawd/engineering-board/blob/main/engineering-board/eb-self/'
PAGES = ('index.html', 'guide.html', 'site.css', 'site.js', 'llms.txt', '.nojekyll')


def stage(output: Path) -> None:
    output = output.resolve()
    if output == ROOT or ROOT in output.parents and output.parts[len(ROOT.parts)] != '.site-build':
        raise ValueError('Use an external output directory or .site-build within the repository.')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be empty; existing files are never removed.')
    # Render before creating output: failure cannot publish a stale committed board.
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    result = subprocess.run(
        ['bash', str(ROOT / 'hooks/scripts/board-view.sh'), 'eb-self', '--stdout', '--link-base', LINK_BASE],
        cwd=ROOT, env=env, check=True, capture_output=True,
    )
    if b'<!doctype html>' not in result.stdout.lower():
        raise ValueError('Board renderer did not return an HTML document.')
    output.mkdir(parents=True, exist_ok=True)
    for name in PAGES:
        shutil.copyfile(ROOT / 'docs' / name, output / name)
    for name in ('assets', 'example'):
        shutil.copytree(ROOT / 'docs' / name, output / name)
    (output / 'board.html').write_bytes(result.stdout)
    print(f'Staged public site at {output}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    stage(args.output)
