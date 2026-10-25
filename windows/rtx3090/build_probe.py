#!/usr/bin/env python3
"""Build a pinned external read-only probe, never the unlock application.

Requires git, Python 3.9+, Bun, clang and lld-link on PATH.
The external GPL-2.0-only sources and EDK2 notices remain in the reference
checkout; their licenses are included by its packaging utility.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

REVISION = '5c076dc4ee7fa369639669fa591ac74d8f6dfcd8'
SOURCE = 'https://github.com/craftingmod/rtx30-unlock'


def run(command, cwd):
    subprocess.run(command, cwd=cwd, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    root, output = args.reference.resolve(), args.output.resolve()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()
    if revision != REVISION:
        parser.error('reference revision does not match the reviewed pin')
    dirty = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=root, text=True)
    if dirty:
        parser.error('reference must be clean; use a fresh checkout')
    if output.exists():
        parser.error('output must be a new directory')
    for tool in ('clang', 'lld-link', 'bun'):
        if not shutil.which(tool):
            parser.error('missing required tool: ' + tool)
    includes = ['-I', 'deps/edk2/MdePkg/Include', '-I', 'deps/edk2/MdePkg/Include/X64']
    sources = ['src/probe/test_core.c', 'src/probe/probe_core.c',
               'src/probe/probe_app.c', 'src/probe/probe_profile.c', 'src/unlock/sha256.c']
    (root / 'build').mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as directory:
        executable = str(Path(directory) / 'probe-tests')
        run(['clang', '-std=c11', '-fshort-wchar', '-Wall', '-Wextra', '-Werror',
             *includes, *sources, '-o', executable], root)
        run([executable], root)
    # Both scripts use Bun built-ins; no package install or unlock build runs.
    run(['bun', 'tools/build-probe.ts'], root)
    run(['python3', 'tools/package_probe_usb.py', '--output', str(output)], root)
    binary = output / 'EFI/BOOT/BOOTX64.EFI'
    provenance = dict(source=SOURCE, revision=REVISION,
                      sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                      purpose='read-only diagnostics; NOT an unlock binary',
                      hardware_validation='not yet performed on target machine')
    (output / 'BUILD-PROVENANCE.json').write_text(json.dumps(provenance, indent=2) + '\n')
    (output / 'RTX30-PROBE/KEEP.txt').write_text('Keep this directory: diagnostic output destination.\n')
    shutil.copyfile(Path(__file__).with_name('README.md'), output / 'TARGET-INSTRUCTIONS.md')


if __name__ == '__main__':
    main()
