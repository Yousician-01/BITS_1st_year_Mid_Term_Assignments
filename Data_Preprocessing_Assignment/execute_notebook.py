"""Execute from a fresh kernel; optional argument: root or notebooks (working directory)."""
from pathlib import Path
import json, os, sys, tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

root=Path(__file__).resolve().parent
workdir=root if len(sys.argv)<2 or sys.argv[1]=='root' else root/'notebooks'
path=root/'notebooks'/'Data_Preprocessing_Assignment_1.ipynb'
with tempfile.TemporaryDirectory(prefix='assignment_kernel_') as temp:
    os.environ['IPYTHONDIR']=str(Path(temp)/'ipython')
    os.environ['JUPYTER_RUNTIME_DIR']=str(Path(temp)/'runtime')
    specdir=Path(temp)/'assignment-python'
    specdir.mkdir()
    (specdir/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],
                                                 'display_name':'Assignment Python','language':'python'}))
    km=KernelManager(kernel_name='assignment-python',kernel_spec_manager=KernelSpecManager(kernel_dirs=[temp]))
    nb=nbformat.read(path,as_version=4)
    client=NotebookClient(nb,km=km,timeout=600,resources={'metadata':{'path':str(workdir)}})
    def progress(cell_index,**kwargs): print('Executing cell',cell_index,flush=True)
    client.on_cell_start=progress
    try:
        client.execute(cwd=str(workdir))
    finally:
        nbformat.write(nb,path)
        # An externally supplied manager belongs to this helper, not NotebookClient.
        # Stop it before Windows attempts to remove the temporary IPython database.
        if km.has_kernel:
            km.shutdown_kernel(now=True)
    errors=[o for c in nb.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
    assert not errors, errors
    print('PASS: clean-kernel notebook execution from',workdir)
