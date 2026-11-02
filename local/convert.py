"""Local SKP preparation. Model bytes never leave this computer."""
import argparse
import dataclasses
import gc
import json
from pathlib import Path
import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import tempfile
import webbrowser


def prepare(source, target, batch_size=500):
    from openskp import SkpFile
    from openskp.export import fragments
    from openskp.instanced_scene import InstancedNode
    print('Reading model locally. Large models may take substantial RAM and time.', flush=True)
    scene = SkpFile.open(source).build_instanced_scene()
    # Flatten placements with accumulated world transforms. Do not bake copies
    # of repeated component geometry into world-space vertex buffers.
    placements = [(node, matrix) for node, matrix in fragments._collect_leaves(scene)
                  if node.mesh_resource_id is not None]
    if not placements:
        raise ValueError('No supported face geometry found in this model.')
    parts = []
    for start in range(0, len(placements), batch_size):
        nodes = [dataclasses.replace(node, matrix=matrix, children=[])
                 for node, matrix in placements[start:start + batch_size]]
        used = {node.mesh_resource_id for node in nodes}
        chunk = dataclasses.replace(scene,
            scene_hierarchy=InstancedNode(name='Part', children=nodes),
            mesh_resources=[r for r in scene.mesh_resources if r.id in used])
        filename = f'part-{len(parts):05d}.frag'
        fragments.export(chunk, target / filename)
        parts.append({'file': filename, 'items': len(nodes)})
        print(f'Prepared part {len(parts)} ({min(start + batch_size, len(placements))}/{len(placements)} placements)', flush=True)
        del chunk
        gc.collect()
    manifest = {'name': Path(source).name, 'sourceBytes': Path(source).stat().st_size,
                'parts': parts, 'bounds': dataclasses.asdict(scene.bounds) if scene.bounds else None}
    (target / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    print(f'Ready: {len(parts)} parts. Only one part is loaded in the browser at a time.', flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', nargs='?')
    parser.add_argument('--batch-size', type=int, default=500)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error('batch-size must be positive')
    source = args.source
    if not source:
        from tkinter import Tk, filedialog
        root = Tk()
        root.withdraw()
        source = filedialog.askopenfilename(title='Choose a SketchUp model', filetypes=[('SketchUp', '*.skp')])
        root.destroy()
    if not source:
        return
    source = Path(source).resolve(strict=True)
    if source.suffix.lower() != '.skp':
        parser.error('Choose a .skp file')
    target = Path(args.output) if args.output else Path(tempfile.mkdtemp(prefix='aswin-skp-'))
    target.mkdir(parents=True, exist_ok=True)
    prepare(source, target, args.batch_size)
    (target / 'index.html').write_text(Path(__file__).with_name('viewer.html').read_text(encoding='utf-8'), encoding='utf-8')
    if args.prepare_only:
        return
    # Serve only generated output, on loopback; never expose the source folder.
    handler = functools.partial(SimpleHTTPRequestHandler, directory=str(target))
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    address = f'http://127.0.0.1:{server.server_port}/'
    print(f'Opening {address}\nKeep this window open. Press Ctrl+C to stop.\nPrepared files: {target}', flush=True)
    webbrowser.open(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    main()

