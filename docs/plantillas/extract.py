import zipfile
import re
from collections import Counter

z = zipfile.ZipFile('docs/plantillas/Plantilla-institucional-roja.pptx')
colors = []
for name in z.namelist():
    if name.endswith('.xml'):
        xml = z.read(name).decode('utf-8')
        colors.extend(re.findall(r'val="([A-Fa-f0-9]{6})"', xml))

print(Counter(colors).most_common(15))
