import os

from nodered_forge import NodeForgeApp

app = NodeForgeApp('torrentio', 'https://torrentio.strem.fun')

app.register_api_node('manifest', '/manifest.json', )

app.output_package('./dev/data/modules/')
