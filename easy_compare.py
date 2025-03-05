import sublime
import sublime_plugin
import tempfile
import os
import subprocess

prev_file_name = None
prev_file_path = None

def plugin_loaded():
    global settings
    settings = sublime.load_settings("easy_compare.sublime-settings")

def get_file_name(view):
    file_name = view.file_name()
    if not file_name:
        # create temp file
        selection = sublime.Region(0, view.size())
        content = view.substr(selection)
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", delete=False) as fp:
            fp.write(content)
            fp.close()
            file_name = fp.name
        return file_name
    else:
        return file_name

def get_tool_path(tool):
    global settings
    if tool == "tortoise_svn":
        tortoise_svn_path = settings.get('tortoise_svn_path')
        if tortoise_svn_path is None or not os.path.isfile(tortoise_svn_path):
            tortoise_svn_path = 'TortoiseProc.exe'
        return tortoise_svn_path
    elif tool == "tortoise_git":
        tortoise_git_path = settings.get('tortoise_git_path')
        if tortoise_git_path is None or not os.path.isfile(tortoise_git_path):
            tortoise_git_path = 'TortoiseGitProc.exe'
        return tortoise_git_path
    elif tool == "win_merge":
        win_merge_path = settings.get('win_merge_path')
        if win_merge_path is None or not os.path.isfile(win_merge_path):
            win_merge_path = 'WinMergeU.exe'
        return win_merge_path

def diff_via_tortoise(exe, a, b):
    cmd = "\"%s\" /command:diff /path \"%s\" /path2 \"%s\"" % (exe, b, a)
    try:
        print(cmd)
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(cmd,
                stdin=devnull,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=subprocess.SW_HIDE)
    except IOError as ex:
        sublime.error_message("Failed to execute command: {}".format(
            str(ex)))
        raise

def diff_via_win_merge(exe, a, b):
    cmd = "\"%s\" /e \"%s\" \"%s\"" % (exe, a, b)
    try:
        print(cmd)
        with open(os.devnull, 'w') as devnull:
            proc = subprocess.Popen(cmd,
                stdin=devnull,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False,
                creationflags=subprocess.SW_HIDE)
    except IOError as ex:
        sublime.error_message("Failed to execute command: {}".format(
            str(ex)))
        raise

def diff_via_tool(tool, left_file, right_file):
    exe_path = get_tool_path(tool)
    if tool == "tortoise_svn":
        diff_via_tortoise(exe_path, left_file, right_file)
    elif tool == "tortoise_git":
        diff_via_tortoise(exe_path, left_file, right_file)
    elif tool == "win_merge":
        diff_via_win_merge(exe_path, left_file, right_file)

class EasyCompare(sublime_plugin.WindowCommand):
    def __get_view__(self, number: int) -> sublime.View:
        if int(sublime.version()) >= 4000:  # ST4
            ## TODO: Validate that there's just 2 groups or tabs somehow.
            return self.window.selected_sheets()[number].view() if len(self.window.selected_sheets()) == 2 else self.window.active_view_in_group(number)
        else:  # ST3
            return self.window.active_view_in_group(number)

    def is_enabled(self):
        return True if self.__get_view__(0) and self.__get_view__(1) else False

    def run(self, **kwargs):
        tool = kwargs.get('tool', None)

        view_1 = self.__get_view__(0)
        view_2 = self.__get_view__(1)

        if view_1 and view_2:
            left_file = get_file_name(view_1)
            right_file = get_file_name(view_2)
            diff_via_tool(tool, left_file, right_file)

class EasyCompareLater(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.size() > 0:
            global prev_file_name, prev_file_path
            prev_file_path = get_file_name(self.view)
            prev_file_name = prev_file_path

            file_name = self.view.file_name()
            if not file_name:
                prev_file_name = self.view.name()
                if not prev_file_name:
                    prev_file_name = "untitled"

class EasyCompareWith(sublime_plugin.TextCommand):
    def run(self, edit):
        if self.view.size() <= 0:
            return

        global prev_file_path, settings
        current_file_path = get_file_name(self.view)
        default_tool = settings.get('default_tool', 'tortoise_svn')
        diff_via_tool(default_tool, prev_file_path, current_file_path)

    def is_visible(self):
        global prev_file_path
        if prev_file_path is None or not os.path.isfile(prev_file_path):
            return False
        else:
            return True

    def description(self):
        global prev_file_name, prev_file_path
        if prev_file_path is None or not os.path.isfile(prev_file_path):
            return "Compare With..."
        else:
            file_name = os.path.basename(prev_file_name)
            dir_name = os.path.dirname(prev_file_name)
            max_dir_len = 10
            if len(dir_name) > 10:
                dir_name = dir_name[0:max_dir_len] + "...\\"
            return "Compare With \"" + dir_name + file_name + "\""