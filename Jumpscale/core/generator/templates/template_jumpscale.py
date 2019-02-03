
# from Jumpscale.core.JSBase import JSBase
import os
import sys
from Jumpscale import j

{% for syspath in md.syspaths %}
if "{{syspath}}" not in sys.path:
    sys.path.append("{{syspath}}")
{%- endfor %}

class JSGroup():
    pass


{% for name, jsgroup in md.jsgroups.items() %}
class group_{{jsgroup.name}}(JSGroup):
    def __init__(self):
        {% for module in jsgroup.jsmodules %}
        self._{{module.jname}} = None
        {%- endfor %}

    {% for module in jsgroup.jsmodules %}
    @property
    def {{module.jname}}(self):
        if self._{{module.jname}} is None:
            from {{module.importlocation}} import {{module.name}}
            self._{{module.jname}} =  {{module.name}}()
            # print("load:%s{{module.jname}}")
            if hasattr(self._{{module.jname}},"_init"):
                self._{{module.jname}}._init()
                # print("init:%s{{module.jname}}")
            else:
                from pudb import set_trace; set_trace()
            if hasattr(self._{{module.jname}},"_init2"):
                self._{{module.jname}}._init2()
                # print("init2:%s{{module.jname}}")
        return self._{{module.jname}}
    {%- endfor %}

{{jsgroup.jdir}} = group_{{jsgroup.name}}()
j.core._groups["{{name}}"] = {{jsgroup.jdir}}

{% endfor %}


