from mypy.plugin import Plugin

class MyPlugin(Plugin):
    def get_function_hook(self, fullname):
        if fullname == '__main__.f':
            return my_hook
        assert fullname
        return None

def my_hook(ctx):
    return ctx.api.named_generic_type('builtins.int', [])

def register(version):
    return MyPlugin
