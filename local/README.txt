ASWIN SKP - LOCAL LARGE MODEL VIEWER

1. Extract the ZIP into a folder.
2. Double-click Start Viewer.cmd and choose your .skp file.
3. Wait for preparation, then a local browser viewer opens automatically.
4. Use the part selector or Previous / Next. Drag to rotate.
5. Keep the command window open while viewing; Ctrl+C stops the local server.

Requires 64-bit Python 3.10 or newer (python.org). First launch installs
OpenSKP 1.4.0 into .venv in this folder. Internet is needed for installation
and the browser rendering libraries. SKP and converted model bytes remain
on this PC, served only at 127.0.0.1. No cloud account or upload is used.

This is a large-model preparation workflow, not verified 2 GB compatibility.
Conversion still holds parsed geometry in PC memory; complex 2 GB files may
need tens of GB of RAM or fail. A single huge component may also exceed
browser memory. Part sizes count placements, not bytes. If a part is too
large, run: Start Viewer.cmd "C:\path\model.skp" --batch-size 50

Only one part is visible at once to bound browser memory. The parts preserve
world placement, material colors and shared component geometry. The original
nested hierarchy is flattened. Loose edges and textures are not included by
this Fragments exporter. Existing small-file viewer features remain separate.

Prepared files are kept in the temporary folder printed by the launcher.
They are not automatically deleted. For a persistent chosen output folder:
Start Viewer.cmd "C:\path\model.skp" --output "C:\path\prepared-model"
Use a new empty output folder for each model.

Built with OpenSKP (MIT) and That Open Fragments (MIT), plus Three.js (MIT).
https://github.com/iamahsanmehmood/openskp
https://github.com/ThatOpen/engine_fragment
https://github.com/mrdoob/three.js

