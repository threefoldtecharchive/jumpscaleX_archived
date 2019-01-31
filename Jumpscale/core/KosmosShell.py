import inspect

from prompt_toolkit.buffer import Buffer
from prompt_toolkit.document import Document
from prompt_toolkit.completion import Completion
from prompt_toolkit.filters import is_done
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import ConditionalContainer, Window
from prompt_toolkit.layout.controls import BufferControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.lexers import PygmentsLexer
from ptpython.filters import ShowDocstring, PythonInputFilter
from ptpython.prompt_style import PromptStyle
from ptpython.utils import get_jedi_script_from_document
from pygments.lexers import PythonLexer



class KosmosShellConfig():

    pass


def get_object(tbc, locals_=None, globals_=None, walkback=False):
    """
    tries starting from the string e.g. j.clients.ssh to get to an object out of the stack
    :param tbc: the line on the console = text before cursor
    :param locals_:
    :param globals_:
    :param walkback:
    :return:
    """

    j = KosmosShellConfig.j

    try:
        obj = eval(tbc)
        return obj
    except Exception as e:
        # print(e)
        pass

    tbc2 = tbc.split(".")[0]  # e.g. ssh.a becomes ssh, because I need to find the ssh object in the stack

    obj = None
    frame_ = inspect.currentframe()
    if locals_ is None:
        locals_ = frame_.f_locals
        locals_ = j._locals_get(locals_)

    if tbc2 in locals_:
        obj = locals_[tbc2]

    if not obj:

        if not globals_:
            globals_ = frame_.f_back.f_globals

        if tbc2 in globals_:
            obj = globals_[tbc2]

    if not obj:

        if walkback:
            # now walk up to the frames
            while obj is None and frame_:
                locals_ = frame_.f_locals

                if tbc2 in locals_:
                    obj = locals_[tbc2]
                else:
                    frame_ = frame_.f_back

    if "." in tbc:
        tbc3 = ".".join(tbc.split(".")[1:])
        try:
            obj2 = eval("obj.%s" % tbc3)
            return obj2
        except:
            return
    return obj


def get_completions(self, document, complete_event):
    """
    Get Python completions.
    """

    j = KosmosShellConfig.j
    obj = None
    tbc = document.current_line_before_cursor
    if "." in tbc:
        c = ".".join(tbc.split(".")[:-1])

        try:
            obj = get_object(c, self.get_locals(), self.get_globals())
        except Exception as e:
            return  # print (e) # TODO: DISPLAY IN BOTTOM PANE
        # print(obj)

        remainder = tbc[len(c)+1:]  # e.g. everything after j.clients.ssh.

        if obj:

            if hasattr(obj.__class__, "_methods_"):
                for x in obj._properties_children():
                    if x is None:
                        continue
                    if x.startswith(remainder):
                        x2 = c+"."+x
                        x3 = x2[len(tbc):]
                        yield Completion(x3, 0, display=x, display_meta=None, style='bg:ansigreen fg:ansiblack')
                for x in obj._properties_model():
                    if x.startswith(remainder):
                        x2 = c+"."+x
                        x3 = x2[len(tbc):]
                        yield Completion(x3, 0, display=x, display_meta=None, style='bg:ansiyellow fg:ansiblack')
                for x in obj._methods():
                    if x.startswith(remainder):
                        x2 = c+"."+x
                        x3 = x2[len(tbc):]
                        yield Completion(x3, 0, display=x, display_meta=None, style='bg:ansiblue fg:ansiblack')
                for x in obj._properties():
                    if x.startswith(remainder):
                        x2 = c+"."+x
                        x3 = x2[len(tbc):]
                        yield Completion(x3, 0, display=x, display_meta=None, style='bg:ansired fg:ansiblack')
                return

    # Do Path completions
    if complete_event.completion_requested or self._complete_path_while_typing(document):
        for c in self._path_completer.get_completions(document, complete_event):
            yield c

    # If we are inside a string, Don't do Jedi completion.
    if self._path_completer_grammar.match(document.text_before_cursor):
        return

    # Do Jedi Python completions.
    if complete_event.completion_requested or self._complete_python_while_typing(document):
        script = get_jedi_script_from_document(document, self.get_locals(), self.get_globals())

        if script:
            completions = script.completions()
            try:
                completions = script.completions()
            except TypeError:
                # Issue #9: bad syntax causes completions() to fail in jedi.
                # https://github.com/jonathanslenders/python-prompt-toolkit/issues/9
                pass
            except UnicodeDecodeError:
                # Issue #43: UnicodeDecodeError on OpenBSD
                # https://github.com/jonathanslenders/python-prompt-toolkit/issues/43
                pass
            except AttributeError:
                # Jedi issue #513: https://github.com/davidhalter/jedi/issues/513
                pass
            except ValueError:
                # Jedi issue: "ValueError: invalid \x escape"
                pass
            except KeyError:
                # Jedi issue: "KeyError: u'a_lambda'."
                # https://github.com/jonathanslenders/ptpython/issues/89
                pass
            except IOError:
                # Jedi issue: "IOError: No such file or directory."
                # https://github.com/jonathanslenders/ptpython/issues/71
                pass
            except AssertionError:
                # In jedi.parser.__init__.py: 227, in remove_last_newline,
                # the assertion "newline.value.endswith('\n')" can fail.
                pass
            except SystemError:
                # In jedi.api.helpers.py: 144, in get_stack_at_position
                # raise SystemError("This really shouldn't happen. There's a bug in Jedi.")
                pass
            except NotImplementedError:
                # See: https://github.com/jonathanslenders/ptpython/issues/223
                pass
            except Exception:
                # Supress all other Jedi exceptions.
                pass
            else:
                for c in completions:
                    if not c.name_with_symbols.startswith("_"):
                        yield Completion(c.name_with_symbols, len(c.complete) - len(c.name_with_symbols),
                                         display=c.name_with_symbols)


def get_doc_string(tbc):
    obj = get_object(tbc, locals_=None, globals_=None, walkback=True)
    if not obj:
        return
    return inspect.getdoc(obj)


class HasDocString(PythonInputFilter):

    def __call__(self):
        tbc = self.python_input.default_buffer.document.current_line_before_cursor
        return bool(get_doc_string(tbc)) and len(self.python_input.docstring_buffer.text)


def setup_docstring_containers(repl):
    # see ptpython.layout
    parent_container = repl.app.layout.container.children[0].children[0]
    # the same as ptpython containers, but without signature checking
    parent_container.children.extend([
        ConditionalContainer(
            content=Window(
                height=Dimension.exact(1),
                char='\u2500',
                style='class:separator'),
            filter=HasDocString(repl) & ShowDocstring(repl) & ~is_done),
        ConditionalContainer(
            content=Window(
                BufferControl(
                    buffer=repl.docstring_buffer,
                    lexer=PygmentsLexer(PythonLexer),
                ),
                height=Dimension(max=12)),
            filter=HasDocString(repl) & ShowDocstring(repl) & ~is_done),
    ])


def ptconfig(repl):
    repl.exit_message = "We hope you had fun using te kosmos shell"
    repl.show_docstring = True

    # Show docstring (bool).
    repl.show_docstring = True

    # When CompletionVisualisation.POP_UP has been chosen, use this
    # scroll_offset in the completion menu.
    repl.completion_menu_scroll_offset = 0

    # Show line numbers (when the input contains multiple lines.)
    repl.show_line_numbers = True

    # Show status bar.
    repl.show_status_bar = False

    # Highlight matching parethesis.
    repl.highlight_matching_parenthesis = True

    # Mouse support.
    repl.enable_mouse_support = True

    # Don't insert a blank line after the output.
    repl.insert_blank_line_after_output = False

    # Enable auto suggestions. (Pressing right arrow will complete the input,
    # based on the history.)
    repl.enable_auto_suggest = True

    # Ask for confirmation on exit.
    repl.confirm_exit = False


    # Use this colorscheme for the code.
    repl.use_code_colorscheme('perldoc')

    # Set color depth (keep in mind that not all terminals support true color).
    repl.color_depth = 'DEPTH_24_BIT'  # True color.

    # Syntax.
    repl.enable_syntax_highlighting = True

    # Add custom key binding for PDB.

    @repl.add_key_binding(Keys.ControlB)
    def _(event):
        ' Pressing Control-B will insert "pdb.set_trace()" '
        event.cli.current_buffer.insert_text('\nimport pdb; pdb.set_trace()\n')

    # Custom key binding for some simple autocorrection while typing.

    corrections = {
        'impotr': 'import',
        'pritn': 'print',
        'pr': 'print(',
    }

    @repl.add_key_binding(' ')
    def _(event):
        ' When a space is pressed. Check & correct word before cursor. '
        b = event.cli.current_buffer
        w = b.document.get_word_before_cursor()
        if w is not None:
            if w in corrections:
                b.delete_before_cursor(count=len(w))
                b.insert_text(corrections[w])
        b.insert_text(' ')

    class CustomPrompt(PromptStyle):
        """
        The classic Python prompt.
        """

        def in_prompt(self):
            return [('class:prompt', 'JSX> ')]

        def in2_prompt(self, width):
            return [('class:prompt.dots', '...')]

        def out_prompt(self):
            return []

    repl.all_prompt_styles['custom'] = CustomPrompt()
    repl.prompt_style = 'custom'

    repl._completer.__class__.get_completions = get_completions

    @repl.add_key_binding('?')
    def _(event):
        j = KosmosShellConfig.j
        b = event.cli.current_buffer
        tbc = b.document.current_line_before_cursor

        d = get_doc_string(tbc)
        if d:
            repl.docstring_buffer.reset(document=Document(d, cursor_position=0))
        else:
            repl.docstring_buffer.reset()

    setup_docstring_containers(repl)
