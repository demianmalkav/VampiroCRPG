"""Build a small, offline source bundle from the Git-backed scene proof."""
from pathlib import Path
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[2]


def main():
    destination = Path(sys.argv[1]) if len(sys.argv)>1 else ROOT.parent/'la-noche-que-recuerda.zip'
    files = [p for p in (ROOT/'proof').rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix in ('.py','.html','.css','.js','.md')]
    files += [ROOT/'tests/specs'/name for name in ('m2_core_a_cases.json','m2_core_b_profile.json','m2_core_b_cases.json')]
    files += [ROOT/'iniciar-escena.cmd', ROOT/'iniciar-escena.sh', ROOT/'docs/M2_SCENE_RESULT_01.md']
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(files): archive.write(file, 'la-noche-que-recuerda/'+str(file.relative_to(ROOT)))
        archive.write(ROOT/'proof/scene/LEEME_PAQUETE.md', 'la-noche-que-recuerda/README.md')
    print(destination)


if __name__ == '__main__': main()
