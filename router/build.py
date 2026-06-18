# build.py
import os
import sys
import shutil
import subprocess
from pathlib import Path
import json

class AxeaneBuilder:
    """Build system for Axeane Kompta Automation Engine"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.build_dir = self.project_root / 'build'
        self.dist_dir = self.project_root / 'dist'
        self.spec_file = self.project_root / 'axeane.spec'
        
        # Files and folders to include in the build
        self.include_patterns = [
            'main.py',
            'run.py',
            'Function/**/*.py',
            'Moduls/**/*.py',
            'Logic/**/*.py',
            'Models/**/*.py',
            'UI/**/*.py',
            'Debug/**/*.py',
            'DB/**/*.json',
            'requirements.txt',
            'README.md'
        ]
        
        # Files to exclude
        self.exclude_patterns = [
            '**/__pycache__/**',
            '**/*.pyc',
            '**/*.pyo',
            'build/**',
            'dist/**',
            '*.spec',
            '.git/**',
            '.env',
            'Debug/logs/**'
        ]
    
    def clean(self):
        """Remove build and dist directories"""
        print("🧹 Cleaning previous builds...")
        
        for directory in [self.build_dir, self.dist_dir]:
            if directory.exists():
                shutil.rmtree(directory)
                print(f"   Removed {directory}")
        
        if self.spec_file.exists():
            self.spec_file.unlink()
            print(f"   Removed {self.spec_file}")
    
    def check_pyinstaller(self):
        """Check if PyInstaller is installed"""
        try:
            result = subprocess.run(
                ['pyinstaller', '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"✅ PyInstaller version: {result.stdout.strip()}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ PyInstaller not found!")
            print("   Install it with: pip install pyinstaller")
            return False
    
    def generate_spec(self):
        """Generate PyInstaller spec file"""
        print("📝 Generating PyInstaller spec file...")
        
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['run.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('DB', 'DB'),
        ('Function', 'Function'),
        ('Moduls', 'Moduls'),
        ('Logic', 'Logic'),
        ('Models', 'Models'),
        ('UI', 'UI'),
        ('Debug', 'Debug'),
    ],
    hiddenimports=[
        'playwright',
        'playwright.async_api',
        'httpx',
        'tkinter',
        'tkinter.ttk',
        'json',
        'asyncio',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AxeaneAutomation',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
        
        with open(self.spec_file, 'w', encoding='utf-8') as f:
            f.write(spec_content)
        
        print(f"   Created {self.spec_file}")
    
    def build_executable(self, onefile=True):
        """Build the executable using PyInstaller"""
        print("🔨 Building executable...")
        
        if not self.check_pyinstaller():
            return False
        
        # Generate spec file if it doesn't exist
        if not self.spec_file.exists():
            self.generate_spec()
        
        # Build command
        cmd = ['pyinstaller']
        
        if onefile:
            cmd.append('--onefile')
        
        cmd.extend([
            '--clean',
            '--noconfirm',
            '--distpath', str(self.dist_dir),
            '--workpath', str(self.build_dir),
            str(self.spec_file)
        ])
        
        print(f"   Running: {' '.join(cmd)}")
        
        try:
            subprocess.run(cmd, check=True, cwd=self.project_root)
            print("✅ Build completed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Build failed: {e}")
            return False
    
    def create_portable_zip(self):
        """Create a portable ZIP distribution"""
        print("📦 Creating portable ZIP distribution...")
        
        # Create portable directory structure
        portable_dir = self.dist_dir / 'AxeaneAutomation_Portable'
        if portable_dir.exists():
            shutil.rmtree(portable_dir)
        
        portable_dir.mkdir(parents=True)
        
        # Copy Python files
        for pattern in self.include_patterns:
            for source_file in self.project_root.glob(pattern):
                if source_file.is_file():
                    rel_path = source_file.relative_to(self.project_root)
                    dest_file = portable_dir / rel_path
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_file, dest_file)
        
        # Create requirements.txt if it doesn't exist
        requirements_file = portable_dir / 'requirements.txt'
        if not requirements_file.exists():
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write("""playwright>=1.40.0
httpx>=0.25.0
""")
        
        # Create README
        readme_file = portable_dir / 'README.txt'
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write("""Axeane Kompta Automation Engine
================================

INSTALLATION:
1. Install Python 3.8 or higher
2. Install dependencies: pip install -r requirements.txt
3. Install Playwright browsers: playwright install chromium

USAGE:
- Run the application: python run.py
- For help: python run.py --help

CONFIGURATION:
- Edit files in the DB/ folder to customize accounting rules
- Check Debug/logs/ for network and error logs

For more information, see the full documentation.
""")
        
        # Create ZIP file
        zip_path = self.dist_dir / 'AxeaneAutomation_Portable.zip'
        if zip_path.exists():
            zip_path.unlink()
        
        shutil.make_archive(
            str(zip_path.with_suffix('')),
            'zip',
            self.dist_dir,
            'AxeaneAutomation_Portable'
        )
        
        print(f"✅ Created {zip_path}")
    
    def build_all(self, onefile=True, portable=True):
        """Run complete build process"""
        print("=" * 60)
        print("🏗️  AXEANE AUTOMATION BUILD SYSTEM")
        print("=" * 60)
        
        # Clean previous builds
        self.clean()
        
        # Build executable
        if not self.build_executable(onefile=onefile):
            return False
        
        # Create portable ZIP
        if portable:
            self.create_portable_zip()
        
        print("\n" + "=" * 60)
        print("✅ BUILD COMPLETE!")
        print("=" * 60)
        print(f"\n📁 Executable: {self.dist_dir / 'AxeaneAutomation.exe'}")
        if portable:
            print(f"📦 Portable ZIP: {self.dist_dir / 'AxeaneAutomation_Portable.zip'}")
        print("\nYou can now distribute these files to end users.")
        
        return True

def main():
    """Main entry point for build script"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Build system for Axeane Kompta Automation Engine',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python build.py                    # Build executable + portable ZIP
  python build.py --no-portable      # Build executable only
  python build.py --no-onefile       # Build as folder instead of single exe
  python build.py --clean            # Clean build artifacts only
        """
    )
    
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean build artifacts and exit'
    )
    
    parser.add_argument(
        '--no-onefile',
        action='store_true',
        help='Build as folder instead of single executable'
    )
    
    parser.add_argument(
        '--no-portable',
        action='store_true',
        help='Skip creating portable ZIP distribution'
    )
    
    args = parser.parse_args()
    
    builder = AxeaneBuilder()
    
    if args.clean:
        builder.clean()
        print("✅ Clean complete")
        return
    
    success = builder.build_all(
        onefile=not args.no_onefile,
        portable=not args.no_portable
    )
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
    