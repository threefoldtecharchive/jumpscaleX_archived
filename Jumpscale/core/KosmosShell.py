
from ptpython.utils import get_jedi_script_from_document
from prompt_toolkit.completion import Completer, Completion, PathCompleter

class KosmosShellConfig():

    pass

def get_completions(self, document, complete_event):
    """
    Get Python completions.
    """

    j = KosmosShellConfig.j

    tbc=document.current_line_before_cursor

    if j and "." in tbc:
        c=".".join(tbc.split(".")[:-1])
        remainder = tbc[len(c)+1:]  #e.g. everything after j.clients.ssh.

        obj=None
        if c in self.get_locals():
            obj = self.get_locals()[c]
        elif c in self.get_globals():
            obj = self.get_globals()[c]
        else:
            try:
                o=eval(c)
                if hasattr(o.__class__,"_methods_"):
                    obj = o
            except:
                pass

        if obj:

            # print(dir(obj))
            if hasattr(obj.__class__,"_methods_"):
                for x in obj._properties_children():
                    if x is None:
                        continue
                    if x.startswith(remainder):
                        x2=c+"."+x
                        x3=x2[len(tbc):]
                        yield Completion(x3, 0,display=x,display_meta=None, style='bg:ansigreen fg:ansiblack')
                for x in obj._properties_model():
                    if x.startswith(remainder):
                        x2=c+"."+x
                        x3=x2[len(tbc):]
                        yield Completion(x3, 0,display=x,display_meta=None, style='bg:ansiyellow fg:ansiblack')
                for x in obj._methods():
                    if x.startswith(remainder):
                        x2=c+"."+x
                        x3=x2[len(tbc):]
                        yield Completion(x3, 0,display=x,display_meta=None, style='bg:ansiblue fg:ansiblack')
                for x in obj._properties():
                    if x.startswith(remainder):
                        x2=c+"."+x
                        x3=x2[len(tbc):]
                        yield Completion(x3, 0,display=x,display_meta=None, style='bg:ansired fg:ansiblack')
            # else:
            #     for x in dir(obj):
            #         if x.startswith(remainder):
            #             x2=c+"."+x
            #             x3=x2[len(tbc):]
            #             yield Completion(x3, 0,display=x,display_meta=None, style='bg:ansired fg:ansiblack')

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


def ptconfig(repl):

    # from __future__ import unicode_literals
    from pygments.token import Token
    from ptpython.prompt_style import PromptStyle
    from ptpython.layout import CompletionVisualisation
    # from prompt_toolkit.filters import ViInsertMode
    from prompt_toolkit.key_binding.key_processor import KeyPress
    from prompt_toolkit.keys import Keys

    repl.exit_message="We hope you had fun using te kosmos shell"
    repl.show_docstring = True

    # Show function signature (bool).
    repl.show_signature = False #not needed because is shown in bottomn

    # Show docstring (bool).
    repl.show_docstring = True

    # Show the "[Meta+Enter] Execute" message when pressing [Enter] only
    # inserts a newline instead of executing the code.
    repl.show_meta_enter_message = True

    # Show completions. (NONE, POP_UP, MULTI_COLUMN or TOOLBAR)
    repl.completion_visualisation = CompletionVisualisation.MULTI_COLUMN

    # When CompletionVisualisation.POP_UP has been chosen, use this
    # scroll_offset in the completion menu.
    repl.completion_menu_scroll_offset = 0

    # Show line numbers (when the input contains multiple lines.)
    repl.show_line_numbers = True

    # Show status bar.
    repl.show_status_bar = False

    # When the sidebar is visible, also show the help text.
    repl.show_sidebar_help = True

    # Highlight matching parethesis.
    repl.highlight_matching_parenthesis = True

    # Line wrapping. (Instead of horizontal scrolling.)
    repl.wrap_lines = True

    # Mouse support.
    repl.enable_mouse_support = True

    # Complete while typing. (Don't require tab before the
    # completion menu is shown.)
    repl.complete_while_typing = True

    # Vi mode.
    repl.vi_mode = False

    # Paste mode. (When True, don't insert whitespace after new line.)
    repl.paste_mode = False

    # Use the classic prompt. (Display '>>>' instead of 'In [1]'.)
    repl.prompt_style = 'classic'  # 'classic' or 'ipython'

    # Don't insert a blank line after the output.
    repl.insert_blank_line_after_output = False

    # History Search.
    # When True, going back in history will filter the history on the records
    # starting with the current input. (Like readline.)
    # Note: When enable, please disable the `complete_while_typing` option.
    #       otherwise, when there is a completion available, the arrows will
    #       browse through the available completions instead of the history.
    repl.enable_history_search = False

    # Enable auto suggestions. (Pressing right arrow will complete the input,
    # based on the history.)
    repl.enable_auto_suggest = True

    # Enable open-in-editor. Pressing C-X C-E in emacs mode or 'v' in
    # Vi navigation mode will open the input in the current editor.
    repl.enable_open_in_editor = True

    # Enable system prompt. Pressing meta-! will display the system prompt.
    # Also enables Control-Z suspend.
    repl.enable_system_bindings = True

    # Ask for confirmation on exit.
    repl.confirm_exit = False

    # Enable input validation. (Don't try to execute when the input contains
    # syntax errors.)
    repl.enable_input_validation = True

    # Use this colorscheme for the code.
    repl.use_code_colorscheme('perldoc')

    # Set color depth (keep in mind that not all terminals support true color).

    #repl.color_depth = 'DEPTH_1_BIT'  # Monochrome.
    #repl.color_depth = 'DEPTH_4_BIT'  # ANSI colors only.
    # repl.color_depth = 'DEPTH_8_BIT'  # The default, 256 colors.
    repl.color_depth = 'DEPTH_24_BIT'  # True color.

    # Syntax.
    repl.enable_syntax_highlighting = True

    # Add custom key binding for PDB.

    @repl.add_key_binding(Keys.ControlB)
    def _(event):
        ' Pressing Control-B will insert "pdb.set_trace()" '
        event.cli.current_buffer.insert_text('\nimport pdb; pdb.set_trace()\n')

    # Typing ControlE twice should also execute the current command.
    # (Alternative for Meta-Enter.)
    """
    @repl.add_key_binding(Keys.ControlE, Keys.ControlE)
    def _(event):
        b = event.current_buffer
        if b.accept_action.is_returnable:
            b.accept_action.validate_and_handle(event.cli, b)
    """


    # Typing 'jj' in Vi Insert mode, should send escape. (Go back to navigation
    # mode.)
    """
    @repl.add_key_binding('j', 'j', filter=ViInsertMode())
    def _(event):
        " Map 'jj' to Escape. "
        event.cli.key_processor.feed(KeyPress(Keys.Escape))
    """

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


    @repl.add_key_binding('?')
    def _(event):
        b = event.cli.current_buffer
        lbc = b.document.current_line_before_cursor
        # b.delete_before_cursor(count=1)
        print("NEED TO FIND A WAY HOW TO SHOW (GET FROM OBJ) HELP TEXT")
        # from prompt_toolkit.shortcuts import message_dialog
        # message_dialog(
        #     title='Example dialog window',
        #     text='Do you want to continue?\nPress ENTER to quit.')
        # b.document.insert_after("THOS OS TEST")
        # print(b.document.__dict__)
        # print("\n'''")
        # for i in range(10):
        #     print(lbc)
        # print("'''")

    # class CustomPrompt(PromptStyle):
    #     def in_tokens(self, cli):
    #         return [
    #             (Token.In, 'Input['),
    #             (Token.In.Number, '%s' % repl.current_statement_index),
    #             (Token.In, '] >>: '),
    #         ]
    #
    #     def in2_tokens(self, cli, width):
    #        return [
    #             (Token.In, '...: '.rjust(width)),
    #         ]
    #
    #     def out_tokens(self, cli):
    #         return [
    #             (Token.Out, 'Result['),
    #             (Token.Out.Number, '%s' % repl.current_statement_index),
    #             (Token.Out, ']: '),
    #         ]

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





