# aiophantom
asynchronous executor for Jinja2 template rendering with PhantomJS

# requirements
- python 3.6+
- selenium (+ selenium python package)
- jinja2

# usage
```python
from aiophantom import Renderer

async def render_shit(renderer):
   async with renderer as r:
      with open("output.png", "wb") as f:
         f.write(await r.render({"i": "Hello World"}))

renderer = Renderer("<p>{{ i }}</p>")
renderer._loop.run_until_complete(render_shit(renderer))
renderer._loop.close()
```
