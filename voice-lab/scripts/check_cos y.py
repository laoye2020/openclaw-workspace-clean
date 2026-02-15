import importlib, pkgutil
print("cosyvoice listed:", any(m.name=='cosyvoice' for m in pkgutil.iter_modules()))
try:
    m = importlib.import_module('cosyvoice')
    print('cosyvoice loaded:', m)
except Exception as e:
    print('failed to import cosyvoice:', e)
